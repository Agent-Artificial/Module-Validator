import torch
from pydantic import BaseModel
from typing import Union, Optional, Any

from data_models import BaseMiner, BaseModule, ModuleConfig, MinerRequest, app, MinerConfig, Ss58Key


TASK_STRINGS = {
    "speech2text": "s2tt",
    "speech2speech": "s2st",
    "auto_speech_recognition": "asr",
    "text2speech": "t2st",
    "text2text": "t2tt",
}

TARGET_LANGUAGES = {
    "English": "eng",
    "Afrikaans": "afr",
    "Amharic": "amh",
    "Modern Standard Arabic": "arb",
    "Moroccan Arabic": "ary",
    "Egyptian Arabic": "arz",
    "Assamese": "asm",
    "Asturian": "ast",
    "North Azerbaijani": "azj",
    "Belarusian": "bel",
    "Bengali": "ben",
    "Bosnian": "bos",
    "Bulgarian": "bul",
    "Catalan": "cat",
    "Cebuano": "ceb",
    "Czech": "ces",
    "Central": "ckb",
    "Mandarin Chinese": "cmn",
    "Mandarin Chinese Hant": "cmn_Hant",
    "Welsh": "cym",
    "Danish": "dan",
    "German": "deu",
    "Estonian": "est",
    "Basque": "eus",
    "Finnish": "fin",
    "French": "fra",
    "Nigerian Fulfulde": "fuv",
    "West Central Oromo": "gaz",
    "Irish": "gle",
    "Galician": "glg",
    "Gujarati": "guj",
    "Hebrew": "heb",
    "Hindi": "hin",
    "Croatian": "hrv",
    "Hungarian": "hun",
    "Armenian": "hye",
    "Igbo": "ibo",
    "Indonesian": "ind",
    "Icelandic": "isl",
    "Italian": "ita",
    "Javanese": "jav",
    "Japanese": "jpn",
    "Kamba": "kam",
    "Kannada": "kan",
    "Georgian": "kat",
    "Kazakh": "kaz",
    "Kabuverdianu": "kea",
    "Halh Mongolian": "khk",
    "Khmer": "khm",
    "Kyrgyz": "kir",
    "Korean": "kor",
    "Lao": "lao",
    "Lithuanian": "lit",
    "Luxembourgish": "ltz",
    "Ganda": "lug",
    "Luo": "luo",
    "Standard Latvian": "lvs",
    "Maithili": "mai",
    "Malayalam": "mal",
    "Marathi": "mar",
    "Macedonian": "mkd",
    "Maltese": "mlt",
    "Meitei": "mni",
    "Burmese": "mya",
    "Dutch": "nld",
    "Norwegian Nynorsk": "nno",
    "Norwegian Bokmål": "nob",
    "Nepali": "npi",
    "Nyanja": "nya",
    "Occitan": "oci",
    "Odia": "ory",
    "Punjabi": "pan",
    "Southern Pashto": "pbt",
    "Western Persian": "pes",
    "Polish": "pol",
    "Portuguese": "por",
    "Romanian": "ron",
    "Russian": "rus",
    "Slovak": "slk",
    "Slovenian": "slv",
    "Shona": "sna",
    "Sindhi": "snd",
    "Somali": "som",
    "Spanish": "spa",
    "Serbian": "srp",
    "Swedish": "swe",
    "Swahili": "swh",
    "Tamil": "tam",
    "Telugu": "tel",
    "Tajik": "tgk",
    "Tagalog": "tgl",
    "Thai": "tha",
    "Turkish": "tur",
    "Ukrainian": "ukr",
    "Urdu": "urd",
    "Northern Uzbek": "uzn",
    "Vietnamese": "vie",
    "Xhosa": "xho",
    "Yoruba": "yor",
    "Cantonese": "yue",
    "Colloquial Malay": "zlm",
    "Standard Malay": "zsm",
    "Zulu": "zul",
}


class TranslationConfig(BaseModel):
    model_name_or_card: Union[str, Any] = "facebook/seamless-M4T-V2-large"
    vocoder_name: str = (
        "vocoder_v2"
        if model_name_or_card == "facebook/seamless-M4T-V2-large"
        else "vocoder_36langs"
    )
    device: Any = torch.device(device="cuda:0")
    text_tokenizer: str = model_name_or_card
    apply_mintox: bool = (True,)
    dtype: Any = (torch.float16,)
    input_modality: Optional[Any] = (None,)
    output_modality: Optional[Any] = None


class TranslationData(BaseModel):
    input: str
    task_string: str
    source_language: Optional[str] = None
    target_language: str
    
    
class TranslationRequest(MinerRequest):
    def __init__(self, data: TranslationData):
        super().__init__()
        self.data = data

   
__all__ = [
    "TranslationConfig",
    "TranslationData",
    "TranslationRequest",
    "TARGET_LANGUAGES",
    "TASK_STRINGS",
    "MinerConfig",
    "ModuleConfig",
    "BaseMiner",
    "BaseModule",
    "app",
    "Ss58Key"
]