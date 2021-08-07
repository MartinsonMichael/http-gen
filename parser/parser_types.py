from typing import List, Optional, Dict, Any


class MessageAttribute:
    def __init__(
            self,
            atr_name: Optional[str] = None,
            atr_type: Optional[str] = None,
            repeated: Optional[bool] = False,
            is_map: Optional[bool] = False,
            map_key_type: Optional[str] = None,
            map_value_type: Optional[str] = None,
            changers: List[str] = [],
    ):
        self.changers = changers
        self.atr_name = atr_name
        self.atr_type = atr_type
        self.repeated = repeated

        self.is_map = is_map
        self.map_key_type = map_key_type
        self.map_value_type = map_value_type

    def __str__(self):
        return f"{self.atr_name}: {'[]' if self.repeated else ''}{self.atr_type}"


class Message:
    def __init__(self, changers: List[str] = []):
        self.changers = changers
        self.name: str = ""
        self.attributes: List[MessageAttribute] = []

    def __str__(self):
        res = self.name + "\n"
        for x in self.attributes:
            res += "\t" + str(x) + "\n"
        return res


class ServiceMethod:
    def __init__(self, name: str, input_type: str, output_type: str, changers: List[str] = []):
        self.changers = changers
        self.name = name
        self.input_type = input_type
        self.output_type = output_type

    def __str__(self):
        return f"{self.name}: {self.input_type} -> {self.output_type}"


class Service:
    def __init__(self, changers: List[str] = []):
        self.changers: List[str] = changers
        self.name: str = ""
        self.methods: List[ServiceMethod] = []

    def __str__(self):
        res = self.name + "\n"
        for x in self.methods:
            res += "\t" + str(x) + "\n"
        return res


class ParseResult:
    def __init__(self):
        self.messages: List[Message] = []
        self.services: List[Service] = []
        self.meta: Dict[str, Any] = {}

    def __str__(self):
        res = f"Services ({len(self.services)}):\n"
        for x in self.services:
            res += str(x) + "\n"
        res += f"Messages ({len(self.messages)}):\n"
        for x in self.messages:
            res += str(x) + "\n"
        return res
