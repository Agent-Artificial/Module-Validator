import json
import requests
from modules.translation.translation_module import Translation
from data_models import MinerRequest

response = requests.get('https://registrar-cellium.ngrok.app/modules/translation/sample_request')
miner_request = MinerRequest(data=json.loads(response))

trans = Translation()
print(miner_request)
trans.process(miner_request)