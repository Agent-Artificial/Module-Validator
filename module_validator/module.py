class Module:
    def __init__(self, name: str) -> None:
        self.name = name

    def __call__(self, output: str) -> None:
        print(output)
