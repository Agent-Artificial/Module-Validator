# import bittensor
# import uvicorn
# from fastapi import FastAPI
# from pydantic import BaseModel
from typing import Any, Callable #, List, Dict, Union
#from bittensor.cli import (
#    AutocompleteCommand,
#    DelegateStakeCommand,
#    DelegateUnstakeCommand,
#    GetIdentityCommand,
#    GetWalletHistoryCommand,
#    InspectCommand,
#    ListCommand,
#    ListDelegatesCommand,
#    MetagraphCommand,
#    MyDelegatesCommand,
#    NewColdkeyCommand,
#    NewHotkeyCommand,
#    NominateCommand,
#    OverviewCommand,
#    PowRegisterCommand,
#    ProposalsCommand,
#    RegenColdkeyCommand,
#    RegenColdkeypubCommand,
#    RegenHotkeyCommand,
#    RegisterCommand,
#    RegisterSubnetworkCommand,
#    RootGetWeightsCommand,
#    RootList,
#    RootRegisterCommand,
#    RootSetBoostCommand,
#    RootSetSlashCommand,
#    RootSetWeightsCommand,
#    RunFaucetCommand,
#    SenateCommand,
#    SetIdentityCommand,
#    SetTakeCommand,
#    StakeCommand,
#    StakeShow,
#    SubnetGetHyperparamsCommand,
#    SubnetHyperparamsCommand,
#    SubnetListCommand,
#    SubnetLockCostCommand,
#    SubnetSudoCommand,
#    SwapHotkeyCommand,
#    TransferCommand,
#    UnStakeCommand,
#    UpdateCommand,
#    UpdateWalletCommand,
#    VoteCommand,
#    WalletBalanceCommand,
#    WalletCreateCommand,
#    CommitWeightCommand,
#    RevealWeightCommand,
#    CheckColdKeySwapCommand
#    )
from chains.tao.axons.protocol import ModuleRequest
from bittensor.subnets import SubnetsAPI
from chains.tao.axons.btcli_functions import app, create_command_endpoint, create_endpoint
from data_models import MinerRequest, BaseModule


class Process:
    def __init__(self, process: Callable[..., Any]):
        self.process = process

# class ModuleAxon(SubnetsAPI):
    # def __init__(self, wallet: bittensor.wallet):
        # super().__init__(wallet)
        # self.netuid = 1
        # self.name = "test_miner_hot"
        # self.module = None
        # self.process = None
        # self.available_commands = []
        # self.blacklist = self.blacklist_request
        # self.priority = self.prioritize_module_request
    # 
    # def blacklist_request(self, synapse: ModuleRequest) -> bool:
        # blacklist = []
        # return synapse.to_headers["from"] not in blacklist
# 
    # def prioritize_module_request(self, synapse: ModuleRequest) -> float:
   #     Apply custom priority
        # return 1.0
    # 
    # def create_command_endpoint(self, path, command_name: str, command_class: Process):
        # self.available_commands.append(command_name)
        # create_command_endpoint(path, command_name=command_name, command_class=command_class)
        # 
    # def create_endpoint(self, path, command_info):
        # create_endpoint(path, command_info)
        # 
    # def prepare_synapse(self, *args, **kwargs) -> Any:
        # ModuleRequest(request_input=MinerRequest(*args, **kwargs))
# 
    # def process_responses(self, responses: List[Any]) -> Any:
        # full_response = None
        # for response in responses:
            # full_response += response
        # return full_response
# 
    # def set_module(self, module: BaseModule):
        # self.module = module
        # 
    # def set_process(self, module: BaseModule):
        # self.process = Process(process=module.process)
        # 
    # def serve_modules(self, app: FastAPI):
        # uvicorn.run(app, host="0.0.0.0", port=8000)
        # 
    # def cli_command(self, command: str, **kwargs):
        # commands = {
            # "wallet":["btcli", "wallet", "{command}", "--wallet.name", '{wallet_name}', "--subtensor.chain_endpoint", "ws://127.0.0.1:9946"],
            # "subnet": ["btcli", "subnet", "{command}", "--wallet.name", '{wallet_name}', "--wallet.hotkey", '{hotkey}', "--subtensor.chain_endpoint", "ws://127.0.0.1:9946"],
        # }
        # 
        # for key, value in commands.items():
            # if key == command:
                # subprocess_command = value.replace(f"{{{command}}}", command)
        # for key, value in kwargs.items():
            # if key in subprocess_command:
                # subprocess_command = subprocess_command.replace(f"{{{key}}}", value)
        # 
   # TODO Finish this function
    # def get_cli_parameters(self, parameters: Dict):
        # parameter_maps =  {
            # "netuid": "--netuid {netuid}",
            # "subtensor": {
                # "network": "--subtensor.network {network}",
            # },
            # "cuda": {
                # "use_cuda": "--cuda.use_cuda {use_cuda}",
            # },
            # "pow_register": {
                # "num_processes": "--pow_register.num_processes {num_processes}",
                # "update_interval": "--pow_register.update_interval {update_interval}",
                # "no_output_in_place": "--pow_register.no_output_in_place {no_output_in_place}",
                # "verbose": "--pow_register.verbose {verbose}",
                # "cuda.use_cuda": "--pow_register.cuda.use_cuda {use_cuda}",
                # "cuda.no_cuda": "--pow_register.cuda.no_cuda {no_cuda}",
                # "cuda.dev_id": "--pow_register.cuda.dev_id {dev_id}",
                # "cuda.tpb": "--pow_register.cuda.tpb {tpb}",
            # },
            # "root": {
                # "list": "list",
                # "weights": "weights --netuid {netuid} --weights {weights}",
                # "boost": "boost --netuid {netuid} --increase {increase}",
                # "slash": "slash --netuid {netuid} --slash {slash}",
                # "get_weights": "get_weights",
                # "senate_vote": "senate_vote --proposal {proposal}",
                # "senate": "senate",
                # "register": "register --wallet.name {name} --wallet.hotkey {hotkey}",
                # "proposals": "proposals",
                # "set_take": "--wallet.name {name} --wallet.hotkey {hotkey}",
                # "delegate": " --delegate_ss58key {delegate_ss58key} --amount {amount}",
                # "undelegate": "--delegate_ss58key {delegate_ss58key} --amount {amount}",
                # "my_delegates": "my_delegates",
                # "list_delegates": "--wallet.name {name}",
                # "nominate": "--wallet.name {name} --wallet.hotkey {hotkey}"
            # },
            # "wallet": {
                # "list": "list --path ~/.bittensor",
                # "overview": "overview --all --sort_by stake --sort_order descending",
                # "transfer": "transfer --dest 5Dp8... --amount 100",
                # "inspect": "wallet inspect --all",
                # "balance": "wallet balance --all",
                # "create": "wallet create --n_words 21",
                # "new_hotkey": "wallet new_hotkey --n_words 24",
                # "new_coldkey": "wallet regen_coldkey --mnemonic ",
                # "regen_coldkey": "",
                # "regen_coldkeypub": "wallet regen_coldkeypub --ss58_address",
                # "regen_hotkey": "wallet regen_hotkey --use_password {use_password}",
                # "faucet": "",
                # "update": "",
                # "swap_hotkey": "",
                # "set_identity": "",
                # "get_identity": "",
                # "history": "",
                # "check_coldkey_swap": "",
            # }
        # }
        # params = []
        # param_value = None
        # for parameter, value in parameters.items():
            # if "." in parameters:
                # param1, param2 = parameters.split(".")
                # if param2 in parameter_maps[param1].keys():
                    # param_value = parameter_maps[param1][param2]
            # else:
                # param_value = parameter_maps[parameter]
            # for param, val in value.items():                   
                # param_value.replace(f"{{{param}}}", val)
                # params.append(param_value)
        # return params                
    # 
    # def get_cli_commands(self):
        # return {
            # "subnets": {
                # "list": SubnetListCommand,
                # "metagraph": MetagraphCommand,
                # "lock_cost": SubnetLockCostCommand,
                # "create": RegisterSubnetworkCommand,
                # "pow_register": PowRegisterCommand,
                # "register": RegisterCommand,
                # "hyperparameters": SubnetHyperparamsCommand,
            # },
            # "root": {
                # "list": RootList,
                # "weights": RootSetWeightsCommand,
                # "get_weights": RootGetWeightsCommand,
                # "boost": RootSetBoostCommand,
                # "slash": RootSetSlashCommand,
                # "senate_vote": VoteCommand,
                # "senate": SenateCommand,
                # "register": RootRegisterCommand,
                # "proposals": ProposalsCommand,
                # "set_take": SetTakeCommand,
                # "delegate": DelegateStakeCommand,
                # "undelegate": DelegateUnstakeCommand,
                # "my_delegates": MyDelegatesCommand,
                # "list_delegates": ListDelegatesCommand,
                # "nominate": NominateCommand,
            # },
            # "wallet": {
                # "list": ListCommand,
                # "overview": OverviewCommand,
                # "transfer": TransferCommand,
                # "inspect": InspectCommand,
                # "balance": WalletBalanceCommand,
                # "create": WalletCreateCommand,
                # "new_hotkey": NewHotkeyCommand,
                # "new_coldkey": NewColdkeyCommand,
                # "regen_coldkey": RegenColdkeyCommand,
                # "regen_coldkeypub": RegenColdkeypubCommand,
                # "regen_hotkey": RegenHotkeyCommand,
                # "faucet": RunFaucetCommand,
                # "update": UpdateWalletCommand,
                # "swap_hotkey": SwapHotkeyCommand,
                # "set_identity": SetIdentityCommand,
                # "get_identity": GetIdentityCommand,
                # "history": GetWalletHistoryCommand,
                # "check_coldkey_swap": CheckColdKeySwapCommand,
            # },
            # "stake": {
                # "show": StakeShow,
                # "add": StakeCommand,
                # "remove": UnStakeCommand,
            # },
            # "weights": {
                # "commit": CommitWeightCommand,
                # "reveal": RevealWeightCommand,
            # },
            # "sudo": {
                # "set": SubnetSudoCommand,
                # "get": SubnetGetHyperparamsCommand,
            # },
            # "legacy": {
                # "update": UpdateCommand,
                # "faucet": RunFaucetCommand,
            # },
            # "info": {
                # "autocomplete": AutocompleteCommand,
            # }
        # }
            # 