import json
import asyncio
import aiohttp
from requests.sessions import session
from data_models import MinerRequest
from communex._common import get_node_url
from communex.client import CommuneClient
from communex.compat.key import Keypair

comx = CommuneClient(get_node_url())


def get_keypair(key_name):
    with open("/home/bakobi/.commune/key/" + key_name + ".json", "r", encoding="utf-8") as f:
        json_data = json.loads(f.read())["data"]
        data = json.loads(json_data)
        return Keypair(
            ss58_address=data["ss58_address"],
            private_key=data["private_key"],
            public_key=data["public_key"],
        )


miner_request = MinerRequest(data=sample_data).model_dump()

keypair = get_keypair("eden.Validator")

address_dict = comx.query_map_address(netuid=10)
key_dict = comx.query_map_key(netuid=10)
vali_uid = None
addresses = []
for uid, key in key_dict.items():
    if key == keypair.ss58_address:
        continue
    
ignore_list = ("0.0.0.0", "None:None", "127.0.0.1", "")
for uid, address in address_dict.items():
    if uid == vali_uid:
        continue
    if address in ignore_list:
        continue
    addresses.append(address)
    

    
if __name__ == "__main__":
    asyncio.run(main(addresses, miner_request))
    