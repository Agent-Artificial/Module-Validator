import os
from pathlib import Path
from bittensor.wallet import Keypair
from bittensor.keyfile import decrypt_keyfile_data, encrypt_keyfile_data, deserialize_keypair_from_keyfile_data, ask_password_to_encrypt
from typing import Optional, List, Dict, Union, Any
from dotenv import load_dotenv


# load_dotenv()
# 
# class TaoKeyManager:
    # def __init__(
        # self, 
        # wallet_name: Optional[str] = None, 
        # key_name: Optional[str] = None, 
        # key_path: Optional[str]=None
    # ):
        # self.keypair: Keypair = None
        # self.wallet_name = wallet_name or os.getenv("MINER_WALLET_NAME")
        # self.key_name = key_name or os.getenv("MINER_HOT_KEYNAME")
        # self.keys = {}
        # self.hotkey_path = None
        # self.coldkey_path = None
        # self.set_paths(self.wallet_name, self.key_name)
        # self.key_path = key_path or os.getenv("MINER_KEY_PATH")
        # self.get_paths()
        # self.get_keypair(self.keyfile_path)
        # 
    # def get_paths(self):
        # if self.keys:
            # return [value[key]["key_path"] for key, value in self.keys.items()]
    # 
    # def set_paths(self, wallet_name, key_name):
        # self.hotkey_path = Path(self.key_path) / wallet_name / "hotkeys" / key_name
        # self.coldkey_path = Path(self.key_path) / wallet_name / "coldkey"
        # if key_name not in self.keys.keys():
            # self.keys[key_name] = {}
        # self.keys[key_name]["key_path"] = path
        # 
    # def get_keypair(self, get_coldkey=False):
        # cold_key_path = Path(self.coldkey_path)
        # hot_key_path = Path(self.hotkey_path)
        # password = ask_password_to_encrypt()
        # decrypted_cold_key = decrypt_keyfile_data(cold_key_path.read_bytes(), password)
        # if get_coldkey:
            # cold_keypair =  deserialize_keypair_from_keyfile_data(decrypted_cold_key)
        # hot_keypair = deserialize_keypair_from_keyfile_data(hot_key_path.read_text())
        # return hot_keypair, cold_keypair or None
                # 
        # 
        # 
# 
# 