import bittensor 
from abc import ABC, abstractmethod
from fastapi import Response
from pydantic import ConfigDict
from typing import Dict, Any


class SynapseRequest(bittensor.Synapse, ABC):
    request_input: Dict[str, Any]
    response_output: Response
    model_config: ConfigDict = ConfigDict(
        {"arbitrary_types_allowed": True}
    )
    
    @abstractmethod
    def deserialize(self) -> bittensor.Synapse:
        """Deserializes the response into a Synapse object."""
    
    @abstractmethod
    def serialize(self) -> bittensor.Synapse:
        """Serializes the Synapse object into a SynapseRequest object."""