import base64
from pydantic import Field
from dotenv import load_dotenv

from .data_models import TranslationRequest, MinerConfig, ModuleConfig, BaseMiner
from .translation import SeamlessTranslator


load_dotenv()

translator = SeamlessTranslator()


translation_settings = ModuleConfig(
    module_path="module/translation",
    module_name="translation",
    module_endpoint="/modules/translation",
    module_url="https://translation.com/"
)

miner_settings = MinerConfig(
    module_name=Field(default="translation"),
    module_path=Field(default="modules/translation"),
    module_endpoint=Field(default="/modules/translation"),
    module_url=Field(default="https://translation.com/"),
    miner_key_dict={
        "test_miner_1": {
            "key": "5GN2dLhWa5sCB4A558Bkkh96BNdwwikPxCBJW6HQXmQf7ypR",
            "name": "test_miner_1",
            "host": "0.0.0.0",
            "port": 8000,
            "keypath": "$HOME/.commune/key/test_miner_1.json"
        }
    },
)

class TranslationMiner(BaseMiner):
    
    def __init__(self):
        super().__init__(miner_settings, translation_settings)
        self.add_route("translation")
    
    def process(self, request: TranslationRequest):
        text_request = "modules/translation/in/text_request.txt"
        audio_request = "modules/translation/in/audio_request.wav"
        request_path = ""
        if request.data["task_string"].startswith("speech"):
            with open(audio_request, "wb") as f:
                f.write(base64.b64decode(request.data["input"].encode("utf-8")))
            request_path = audio_request
        if request.data["task_string"].startswith("text"):
            with open(text_request, "w", encoding="utf-8") as f:
                f.write(request.data["input"])
            request_path = text_request
        output_text, output_audio = translator.translation_inference(
            in_file=request_path,
            source_langauge=request.data["source_language"].title(),
            target_languages=[request.data["target_language"].title()],
            task_string=request.data["task_string"]
        )
        if request.data["task_string"].endswith("2speech"):
            return base64.b64encode(output_audio).decode("utf-8")
        if request.data["task_string"].endswith("2text"):
            return str(output_text)


if __name__ == "__main__":
    miner = TranslationMiner()
    # with open("modules/translation/in/german_test_data.wav", "rb") as f:
    #     audio_data = f.read()
    # b64audio = base64.b64encode(audio_data).decode("utf-8")
    # translation_data = TranslationData(
    #     input=b64audio,
    #     task_string="speech2text",
    #     source_language="english",
    #     target_language="french"
    # ).model_dump()
    # translation_request = TranslationRequest(
    #     data=translation_data
    # )
    # result = miner.process(request=translation_request)
    # print(result)
    miner.run_server("0.0.0.0", 4269)