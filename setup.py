from setuptools import setup, find_packages

setup(
    name="module_validator",
    version="1",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["module_validator = module_validator.main:main"],
        "module_validator.module": [
            "default = module_validator.main:default_output",
            "register = module_validator.main:register",
        ],
        "module_validator.inference": [            
            "embedding = module_validator.modules.embedding.embedding:process",
            "translation = module_validator.modules.translation.translation:process"
        ],
    },
    summary="Module Validator for Substrate subnet validation",
    license="MIT",
    url="https://github.com/bakobiibizo/module_validator",
    author="bakobiibizo",
    author_email="richard@agentartificial.com",
)