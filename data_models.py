
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from pathlib import Path


TOPICS = [
    "The pursuit of knowledge",
    "The impact of technology on society",
    "The struggle between tradition and modernity",
    "The nature of good and evil",
    "The consequences of war",
    "The search for identity",
    "The journey of self-discovery",
    "The effects of greed",
    "The power of love",
    "The inevitability of change",
    "The quest for power",
    "The meaning of freedom",
    "The impact of colonization",
    "The illusion of choice",
    "The influence of media",
    "The role of education",
    "The effects of isolation",
    "The battle against inner demons",
    "The corruption of innocence",
    "The loss of culture",
    "The value of art",
    "The complexities of leadership",
    "The nature of sacrifice",
    "The deception of appearances",
    "The consequences of environmental degradation",
    "The cycle of life and death",
    "The impact of global capitalism",
    "The struggle for equality",
    "The influence of religion",
    "The exploration of space",
    "The effects of addiction",
    "The dangers of ambition",
    "The dynamics of family",
    "The nature of truth",
    "The consequences of scientific exploration",
    "The illusion of happiness",
    "The pursuit of beauty",
    "The impact of immigration",
    "The clash of civilizations",
    "The struggle against oppression",
    "The quest for eternal life",
    "The nature of time",
    "The role of fate and destiny",
    "The impact of climate change",
    "The dynamics of revolution",
    "The challenge of sustainability",
    "The concept of utopia and dystopia",
    "The nature of justice",
    "The role of mentorship",
    "The price of fame",
    "The impact of natural disasters",
    "The boundaries of human capability",
    "The mystery of the unknown",
    "The consequences of denial",
    "The impact of trauma",
    "The exploration of the subconscious",
    "The paradox of choice",
    "The limitations of language",
    "The influence of genetics",
    "The dynamics of power and control",
    "The nature of courage",
    "The erosion of privacy",
    "The impact of artificial intelligence",
    "The concept of the multiverse",
    "The struggle for resource control",
    "The effects of globalization",
    "The dynamics of social class",
    "The consequences of unbridled capitalism",
    "The illusion of security",
    "The role of memory",
    "The dynamics of forgiveness",
    "The challenges of democracy",
    "The mystery of creation",
    "The concept of infinity",
    "The meaning of home",
    "The impact of pandemics",
    "The role of mythology",
    "The fear of the unknown",
    "The challenge of ethical decisions",
    "The nature of inspiration",
    "The dynamics of exclusion and inclusion",
    "The consequences of prejudice",
    "The effects of fame and anonymity",
    "The nature of wisdom",
    "The dynamics of trust and betrayal",
    "The struggle for personal autonomy",
    "The concept of rebirth",
    "The meaning of sacrifice",
    "The impact of terrorism",
    "The challenge of mental health",
    "The exploration of alternate realities",
    "The illusion of control",
    "The consequences of technological singularity",
    "The role of intuition",
    "The dynamics of adaptation",
    "The challenge of moral dilemmas",
    "The concept of legacy",
    "The impact of genetic engineering",
    "The role of art in society",
    "The effects of cultural assimilation",
]


class Message(BaseModel):
    """
    A class representing a message.

    Explanation:
    This class defines a data model for a message with a single attribute 'text' of type str.
    """

    role: str
    content: str


class Ss58Address(BaseModel):
    """
    A class representing an SS58 address.

    Explanation:
    This class defines a data model for an SS58 address with a single attribute 'address' of type str.
    """

    address: str  # Example field, adjust as needed


class ConfigDict(BaseModel):
    """
    A class representing a configuration dictionary.

    Explanation:
    This class defines a data model for a configuration dictionary with a single attribute 'arbitrary_types_allowed' that specifies whether arbitrary types are allowed by default.
    """

    arbitrary_types_allowed: bool = True


class ValidatorSettings(BaseModel):
    name: str
    ss58_address: str
    keypath: str
    keyname: str
    host_address: str
    external_address: str
    port: int
    chain: str
    use_testnet: bool
    subnet_list: Optional[List[int]]


class GenerationMessages(BaseModel):
    messages: list
    model: str


class MinerRequest(BaseModel):
    request: GenerationMessages
    inference_type: str

    class Config:
        arbitrary_types_allowed = True
        
        
CHAIN_CLIENTS = {
    "communex": "comx",
    "bittensor": "btcli",
    "polkadot": "polkadotjs",
    "olas": "mech_client"
}

CLIENT_FILES = {
    "commune": ".venv/lib/python3.10/site-packages/communex",
    "bittensor": ".bit/lib/python3.10/site-packages/bittensor",
    "polkadot": "node_modules/polkadotjs",
    "olas": ".olas/lib/python3.10/site-packages/olas"
}


class MinerRequest(BaseModel):
    data: Any = Field(default=None)
    
    
class ModuleConfig(BaseModel):
    module_name: str = Field(default="module_name")
    module_path: str = Field(default="modules/{module_name}")
    module_endpoint: str = Field(default="/modules/{module_name}")
    module_url: str = Field(default="http://localhost")
    __pydantic_field_set__ = {"module_name", "module_path", "module_endpoint", "module_url"}
