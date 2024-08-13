import argparse
import os
import requests
import json
import base64
import yaml
from dotenv import load_dotenv
from module_validator.config import Config

ENV = os.getenv('MODULE_VALIDATOR_ENV', 'development')

load_dotenv()

configurator = Config("module_validator/config")

def parseargs():
    parser = argparse.ArgumentParser()
    parser.add_argument("module_type", type=str)
    parser.add_argument("output", type=str)
    args = parser.parse_args()
    return args

def main():
    args = parseargs()
    module = args.module_type
    
    
def install_registrar_module(module_name: str):
    
    