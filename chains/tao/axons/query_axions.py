import random
import numpy as np
import bittensor
from typing import List
from fastapi import HTTPException
from bittensor.axon import axon
from bittensor.metagraph import metagraph
from bittensor.dendrite import dendrite
from bittensor.synapse import Synapse




async def ping_uids(input_dendrite: dendrite, input_metagraph: metagraph, input_uids: List[int], timeout: int = 30):
    axons = [input_metagraph.axons[uid] for uid in input_uids]
    try:
        responses = await input_dendrite(
            axons,
            Synapse(),
            deserialize=False,
            timeout=timeout,
        )
        zipped = zip(input_uids, responses)
        success_uids = [uid for uid, response in zipped if response.status_code == 200]
    except HTTPException as e:
        return {"error": str(e), "message": f"Unable to query axons. {input_uids}", "status_code": e.status_code}
    if success_uids:
        return {"data": success_uids, "status_code": 200}


async def get_api_nodes(dendrite, metagraph, n=0.1, timeout=30):
    trusted_uids = [
        uid.item() for uid in metagraph.uids if metagraph.validator_trust[uid] > 0
    ]
    condition = metagraph.S > np.quantile(metagraph.S, 1 - n)[0].tolist()
    top_uids = np.where(
        condition,
        ping_uids,
        trusted_uids
    )
    init_query_uids = set(top_uids).intersection(trusted_uids)
    return await ping_uids(
        input_dendrite=dendrite,
        input_metagraph=metagraph, 
        input_uids=list(init_query_uids),
        timeout=timeout
    )["data"]
    
    
def get_api_axons(
    wallet,
    metagraph=None, 
    n=0.1,
    timeout=30,
    uids=None
):
    dendrite = bittensor.dendrite(wallet=wallet)
    if metagraph is None:
        metagraph = dendrite.metagraph
    if uids is None:
        uids = get_api_nodes(dendrite, metagraph, n=n, timeout=timeout)
    return [metagraph.axons[uid] for uid in uids]