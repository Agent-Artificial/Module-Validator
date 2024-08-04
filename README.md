# Module Validator

This is the alpha of the module validator system that we are building. It is designed to accept plugins from a central api called the module registrar. Using these modules it can run multiple types of inference depending on the subnet it is mining on. Its ultimate design will be chain agnostic and connect to the olas protocol. It comes coupled with a module validator that runs on the same principal but it validates inference instead of mines with it. 

## Environment
Copy your environment file
```
cp .env.example
```
Fill out the information as needed. 
Note this validator requires some form of text inference, we have provided the openai client to use but the inference type is not important. If you want to use a local model or another  provider just adjust the code to suit your needs. Its only there to dynamically create test data to avoid miners from learning the question set.

## Install

```
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install setuptools wheel
pip install -e .
pip install -r requirements.txt

python -m module.manager
```
You will be prompted by a cli
Select option 1 and enter `embedding`
This will download the embedding module for Eden, subnet 10 on Commune.
If there are any errors with the install
```
rm -r modules/embedding
python -m modules.install_module embedding
```
## Running the validator
```
python -m validators.commune_validator
```
Make sure your environment is setup by copying the .env file or by filling out the default config in validators/config
