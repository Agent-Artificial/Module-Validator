from setuptools import setup

setup(
    name="embedding_module",
    version="1",
    entry_points={
        "module_validator.embedding": ["embedding=module_validator.modules.embedding.embedding.Embedding:process"],
    }
)