from module_validator.chain.vision.run_miner_auto_update import run_auto_updater
from utils.configuration import main as config_main
from utils.set_cwd import set_working_directory_to_submodule


set_working_directory_to_submodule("module_validator/chain/vision")


def run():
    config = config_main()
    run_auto_updater()
    
    
if __name__ == "__main__":
    run()