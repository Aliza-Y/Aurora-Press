class BaseAgent:
    name = "BaseAgent"
    
    def run(self, pipeline: dict, tools: dict) -> dict:
        raise NotImplementedError


REGISTRY = {}


def register(cls):
    REGISTRY[cls.__name__] = cls()
    return cls
