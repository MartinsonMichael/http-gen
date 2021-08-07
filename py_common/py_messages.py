from py_common.py_utils import (
    ParseResult,
    MESSAGE_HEAD,
    TAB,
    _make_attribute_declaration,
    is_base_type,
)


def generate_messages(parse_result: ParseResult, msg_path: str) -> None:
    with open(msg_path, "w") as file:
        file.write(MESSAGE_HEAD)

        for msg in parse_result.messages:
            file.write(f"class {msg.name}:\n")

            msg_params = ['self']
            for atr in msg.attributes:
                if 'Optional' not in atr.changers:
                    msg_params.append(_make_attribute_declaration(atr))
            for atr in msg.attributes:
                if 'Optional' in atr.changers:
                    msg_params.append(_make_attribute_declaration(atr) + " = None")
            file.write(
                f"{TAB}def __init__({', '.join(msg_params)}):\n"
            )
            if len(msg.attributes) == 0:
                file.write(f"{TAB}{TAB}pass\n")

            for atr in msg.attributes:
                file.write(f"{TAB}{TAB}self.{_make_attribute_declaration(atr)} = {atr.atr_name}\n")
            file.write("\n")

            file.write(
                f"{TAB}def to_json(self) -> Union[Dict, List]:\n"
                f"{TAB}{TAB}return {{\n"
            )
            for atr in msg.attributes:
                file.write(f"{TAB}{TAB}{TAB}'{atr.atr_name}': ")
                if atr.is_map and not is_base_type(atr.map_value_type):
                    file.write(f"{{key: value.to_json() for key, value in self.{atr.atr_name}.items()}}")
                elif is_base_type(atr.atr_type) or (atr.is_map and is_base_type(atr.map_value_type)):
                    file.write(f"self.{atr.atr_name}")
                elif not atr.repeated:
                    file.write(f"self.{atr.atr_name}.to_json()")
                else:
                    file.write(f"[x.to_json() for x in self.{atr.atr_name}]")

                if "Optional" in atr.changers:
                    file.write(f" if self.{atr.atr_name} is not None else None")
                file.write(f",\n")

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
                    if is_base_type(atr.atr_type) or (atr.is_map and is_base_type(atr.map_value_type)):
                        file.write(f"obj['{atr.atr_name}']")
                    elif atr.is_map:
                        file.write(f"{{key: value.from_json() for key, value in obj['{atr.atr_name}'].items()}}")
                    elif atr.repeated:
                        file.write(f"[{atr.atr_type}.from_json(x) for x in obj['{atr.atr_name}']]")
                    else:
                        file.write(f"{atr.atr_type}.from_json(obj['{atr.atr_name}'])")

                    if 'Optional' in atr.changers:
                        file.write(f" if '{atr.atr_name}' in obj.keys() else None")
                    file.write(f",\n")

                file.write(f"{TAB}{TAB})")
                file.write("\n\n\n")
