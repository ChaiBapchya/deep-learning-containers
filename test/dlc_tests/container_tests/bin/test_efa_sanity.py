import subprocess
import sys
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

def main():
    check_ib_uverbs()
    check_fi_info()
    check_efa_installed_packages()
    run_fi_pingpong_test()

    return 0

def check_ib_uverbs():
    try:
        command = "lsmod | grep ib_uverbs"
        subprocess.check_call(command, shell=True, executable="/bin/bash")
        logger.info("ib_uverbs module is present in the modules - test succeeded")
    except subprocess.CalledProcessError:
        logger.error("Error: test check_ib_uverbs failed.")
        raise
    return True

def check_fi_info():
    try:
        command = "fi_info -p efa"
        response = subprocess.check_output(command, shell=True, executable="/bin/bash")
        logger.info("Efa provider info is present in response")
    except subprocess.CalledProcessError:
        logger.error("Error: test Check Efa provider failed.")
        raise
    return True

def check_efa_installed_packages():
    try:
        command = "cat /opt/amazon/efa_installed_packages"
        subprocess.check_call(command, shell=True, executable="/bin/bash")
        logger.info("efa packages are successfully installed in the correct path")
    except subprocess.CalledProcessError:
        logger.error("Error: test check EFA packages failed.")
        raise
    return True

def run_fi_pingpong_test():
    try:
        command = "cd ~ && ./src/bin/efa-tests/efa_test.sh"
        subprocess.check_call(command, shell=True, executable="/bin/bash")
        logger.info("fi ping test is successful")
    except subprocess.CalledProcessError:
        logger.error("Error: fi ping test failed.")
        raise
    return True

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        pass

