from parser import (
    ParseResult,
    is_base_type
)

from py_server.py_utils import (
    MESSAGE_HEAD,
    TAB,
    _make_attribute_declaration,
)


def generate_messages(parse_result: ParseResult, msg_path: str) -> None:
    with open(msg_path, "w") as file:
        file.write(MESSAGE_HEAD)

        for msg in parse_result.messages:
            file.write(f"class {msg.name}:\n")
            if len(msg.attributes) != 0:
                file.write(
                    f"{TAB}def __init__(self, "
                    f"{', '.join([_make_attribute_declaration(atr) for atr in msg.attributes])}):\n"
                )
            else:
                file.write(
                    f"{TAB}def __init__(self):\n"
                    f"{TAB}{TAB}pass\n"
                )
            for atr in msg.attributes:
                file.write(f"{TAB}{TAB}self.{_make_attribute_declaration(atr)} = {atr.atr_name}\n")
            file.write("\n")

            file.write(
                f"{TAB}def to_json(self) -> Union[Dict, List]:\n"
                f"{TAB}{TAB}return {{\n"
            )
            for atr in msg.attributes:
                file.write(f"{TAB}{TAB}{TAB}'{atr.atr_name}': ")
                if not atr.is_map:
                    if not atr.repeated:
                        file.write(f"self.{atr.atr_name}")
                        if not is_base_type(atr.atr_type):
                            file.write(f".to_json()")
                    else:
                        if is_base_type(atr.atr_type):
                            file.write(f"self.{atr.atr_name}")
                        else:
                            file.write(f"[x.to_json() for x in self.{atr.atr_name}]")
                else:
                    if is_base_type(atr.map_value_type):
                        file.write(f"{{key: value for key, value in self.{atr.atr_name}.items()}}")
                    else:
                        file.write(
                            f"{{key: value.to_json() for key, value in self.{atr.atr_name}.items()}}")
                if 'Optional' in atr.changers:
                    file.write(f" if self.{atr.atr_name} is not None else None")
                file.write(",\n")
            file.write(
                f"{TAB}{TAB}}}"
            )
            file.write("\n\n")

            file.write(
                f"{TAB}@staticmethod\n"
                f"{TAB}def from_json(obj: Dict) -> '{msg.name}':\n"
            )
            if len(msg.attributes) == 0:
                file.write(f"{TAB}{TAB}pass")

            else:
                file.write(
                    # f"{TAB}{TAB}obj = json.loads(data)\n"
                    f"{TAB}{TAB}return {msg.name}(\n"
                )
                for atr in msg.attributes:
                    file.write(TAB + TAB + TAB)
                    file.write(f"{atr.atr_name}=")
                    if not atr.is_map:
                        if not atr.repeated:
                            if is_base_type(atr.atr_type):
                                file.write(f"obj['{atr.atr_name}'],\n")
                            else:
                                file.write(f"{atr.atr_type}.from_json(obj['{atr.atr_name}']),\n")
                        else:
                            if is_base_type(atr.atr_type):
                                file.write(f"obj['{atr.atr_name}'],\n")
                            else:
                                file.write(f"[{atr.atr_type}.from_json(x) for x in obj['{atr.atr_name}']],\n")
                    else:
                        if is_base_type(atr.map_value_type):
                            file.write(f"obj['{atr.atr_name}'],\n")
                        else:
                            file.write(f"{{key: value.from_json() for key, value in obj['{atr.atr_name}'].items()}},\n")

                file.write(f"{TAB}{TAB})")
                file.write("\n\n\n")
