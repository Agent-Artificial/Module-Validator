from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Optional, Any, Literal
from substrateinterface.utils import ss58

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

class Ss58Key(BaseModel):
    ss58_address: str
    
    def __init__(self, address: str) -> None:
        self.address = self.encode(address)
        super().__init__(address=self.address)
    
    def encode(self, public_address: str) -> str:
        encoded_address = ss58.ss58_encode(public_address)
        return self.__setattr__("ss58_address", encoded_address)

    def __str__(self) -> str:
        return str(self.address)
    
    def __setattr__(self, name: str, value: Any) -> None:
        if name == "ss58_address":
            return super().__setattr__(name, value)
        return super().__setattr__(name, self.encode(value))

    def __hash__(self) -> int:
        return hash(self.address)
    

class MinerConfig(BaseModel):
    module_name: Optional[str] = "embedding"
    key_name: Optional[str] = "eden_miner1"
    key_path_name: Optional[str] = "eden_miner1"
    host: Optional[str] = "0.0.0.0"
    port: Optional[int] = 5959


class ModuleConfig(BaseModel):
    def __init__(self, **kwargs):
        super().__setattr__(**kwargs)
        
    def __setattr__(self, name: str, value: Any) -> None:
        if name == "key":
            return super().__setattr__(name, Ss58Key(value))
        return super().__setattr__(name, value)


class BaseModule(BaseModel, ABC):
    def __init__(self, **kwargs) -> None:
        def setattr(self, name: str, value: Any) -> None:
            if name == "key":
                return super().__setattr__(name, Ss58Key(value))
            return super().__setattr__(name, value)
        super().__init__(**kwargs)
        self.__setattr__ = setattr
        
    @abstractmethod
    async def process(self, url: str) -> Any:
        """Process a request made to the module."""


class TokenUsage(BaseModel):
    """Token usage model"""
    total_tokens: int = 0
    prompt_tokens: int = 0
    request_tokens: int = 0
    response_tokens: int = 0
    
class Message(BaseModel):
    content: str
    role: Literal["user", "assistant", "system"]
