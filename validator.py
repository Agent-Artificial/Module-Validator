from module_validator.chain.vision.run_validator_auto_update import run_auto_updater
from utils.configuration import main as config_main
from utils.set_cwd import set_working_directory_to_submodule
import subprocess


set_working_directory_to_submodule("module_validator/chain/vision")


def run():
    config = config_main()
    command = ["./validation/proxy/api_server/asgi.py",  "--name", f"{config.wallet.name}", "--env_file", ".env", f"{config.netuid}"]
    subprocess.run(command, check=True)


if __name__ == "__main__":
    run()