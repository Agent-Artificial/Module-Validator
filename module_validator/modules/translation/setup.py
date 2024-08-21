from setuptools import setup

setup(
    name="translation_module",
    version="1",
    entry_points={
        "module_validator.translation": ["translation=module_validator.modules.translation.translation.Translation:process"],
    }
)