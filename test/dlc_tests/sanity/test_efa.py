import os

import pytest

from test.test_utils import CONTAINER_TESTS_PREFIX, LOGGER, is_tf2
from test.test_utils.ec2 import get_ec2_instance_type

EFA_SCRIPT = os.path.join(CONTAINER_TESTS_PREFIX, "test_efa_sanity.py")

EFA_EC2_GPU_INSTANCE_TYPE = get_ec2_instance_type(default="p3dn.24xlarge", processor="gpu")


@pytest.mark.model("N/A")
@pytest.mark.integration("EFA")
@pytest.mark.parametrize("ec2_instance_type", EFA_EC2_GPU_INSTANCE_TYPE, indirect=True)
def test_sanity(training, ec2_connection, region, gpu_only, py3_only):
    run_efa_test(training, ec2_connection, region, docker_executable="nvidia-docker", container_name="efa")


def run_efa_test(
    image_uri,
    ec2_connection,
    region,
    docker_executable="docker",
    container_name="efa",
    test_script=EFA_SCRIPT,
    logfile="output.log",
):
    framework = get_framework_from_image_uri(image_uri)
    container_test_local_dir = os.path.join("$HOME", "container_tests")
    ec2_connection.run(f"$(aws ecr get-login --no-include-email --region {region})", hide=True)

    ec2_connection.run(
        f"{docker_executable} run --name {container_name} -v "
        f"{container_test_local_dir}:{os.path.join(os.sep, 'test')} -itd {image_uri}",
        hide=True,
    )

    try:
        test_output = ec2_connection.run(
            f"{docker_executable} exec --user root {container_name} "
            f"/bin/bash -c '{test_script} {framework}' | tee {logfile}",
            hide=True,
            warn=True,
            timeout=3000,
        )
    except Exception:
        debug_output = ec2_connection.run(f"cat {logfile}")
        LOGGER.error(f"Caught exception while trying to run test via fabric. Output: {debug_output.stdout}")
        raise

    assert test_output.ok, f"EFA tests failed. Output:\n{test_output.stdout}"


def get_framework_from_image_uri(image_uri):
    frameworks = ("tensorflow", "mxnet", "pytorch")
    for framework in frameworks:
        if framework in image_uri:
            if framework == "tensorflow" and is_tf2(image_uri):
                return "tensorflow2"
            return framework
    raise RuntimeError(f"Could not find any framework {frameworks} in {image_uri}")
