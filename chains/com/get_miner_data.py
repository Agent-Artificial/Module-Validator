import json
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

def get_miner_uids(subnet, key_dict=None):
    key_map = comx.query_map_key(netuid=subnet)
    address_map = comx.query_map_address(netuid=subnet)
    with open("modules.json", "r", encoding="utf-8") as f:
        miners = json.loads(f.read())
    if key_dict is None:
        key_dict = {}
    for miner in miners.values():
        name = miner["name"]
        keypair = get_keypair(name)
        vali_uid = None
        for uid, key in key_map.items():
            if key == keypair.ss58_address:
                vali_uid = uid                
        uids = []
        subnet_info[f"{subnet}"] = {}
        for uid, address in address_map.items():
            print(address)
            if ":" not in address:
                continue
            ip, port = address.split(":")
            if ip == "127.0.0.1" or ip == "localhost" or ip == "0.0.0.0" or ip == "None":
                continue
            if vali_uid == uid:
                continue
            uids.append(uid)
            address = f"https://{ip}:{port}"
            ss58key = key_map[uid]
            subnet_info[str(subnet)][ss58key] = {
                "key": ss58key,
                "address": address,
                "uid": uid
            }
            
    return subnet_info


if __name__ == "__main__":
    subnets = [3, 4, 6, 7, 8, 9, 10, 11, 13, 14, 15, 17]
    subnet_info = {}
    for subnet in subnets:
        subnet_info = get_miner_uids(subnet, subnet_info)
    
    with open("data/subnet_info.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(subnet_info, indent=4))