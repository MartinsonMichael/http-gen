import os

from ts_client.ts_microservice_utils import get_file_names
from ts_client.ts_utils import (
    ParseResult,
    HEAD,
    TAB,
    _is_all_atr_basic,
    is_base_type,
    _base_type_to_ts_types,
    _make_atr_with_type,
    _has_map_atr,
    _has_basic_atr,
    _make_map_type,
)


def generate_messages(parse_result: ParseResult, ts_path: str) -> None:
    axiosInstance, messages_file_name, client_file_name = (
        get_file_names(parse_result.meta.get('micro_service_name', None))
    )

    if parse_result.meta.get('micro_service_name', None) is not None:
        messages_file_name = f"{messages_file_name}_{parse_result.meta['micro_service_name'].lower()}"

    with open(os.path.join(ts_path, f"{messages_file_name}.ts"), "w") as file:
        file.write(
            f"{HEAD}\n\n"
        )

        for msg in parse_result.messages:
            file.write(
                f"export interface {msg.name} {{\n"
            )
            for atr in msg.attributes:
                file.write(f"{TAB}{_make_atr_with_type(atr)}\n")
            file.write(f"}}\n")

            file.write(f"export function construct_{msg.name}(x: any): {msg.name} {{\n")
            if _is_all_atr_basic(msg):
                file.write(
                    f"{TAB}return x as {msg.name}\n"
                    f"}}\n\n\n"
                )

            elif not _has_map_atr(msg):
                file.write(f"{TAB}return {{\n")
                if _has_basic_atr(msg):
                    file.write(f"{TAB}{TAB}...x,\n")
                for atr in msg.attributes:
                    if is_base_type(atr.atr_type):
                        continue

                    file.write(f"{TAB}{TAB}{atr.atr_name}: ")
                    if 'Optional' in atr.changers:
                        file.write(f"(x['{atr.atr_name}'] !== null ? ")

                    if atr.is_map:
                        raise ValueError("impossible situation for case")
                    elif atr.repeated:
                        file.write(f"x['{atr.atr_name}'].map((item: any) => construct_{atr.atr_type}(item))")
                    else:
                        file.write(f"construct_{atr.atr_type}(x['{atr.atr_name}'])")

                    if 'Optional' in atr.changers:
                        file.write(" : undefined)")
                    file.write(",\n")

                file.write(f"{TAB}}} as {msg.name}\n")
                file.write(f"}}\n\n\n")
            else:
                file.write(f"{TAB}let obj = {{\n")
                if _has_basic_atr(msg):
                    file.write(f"{TAB}{TAB}...x,\n")
                for atr in msg.attributes:
                    if is_base_type(atr.atr_type):
                        continue

                    file.write(f"{TAB}{TAB}{atr.atr_name}: ")
                    if 'Optional' in atr.changers:
                        file.write(f"(Object.keys(x).includes('{atr.atr_name}') ? ")

                    if atr.is_map:
                        file.write(f"{{}} as {_make_map_type(atr)}")
                    elif atr.repeated:
                        file.write(f"x['{atr.atr_name}'].map((item: any) => construct_{atr.atr_type}(item))")
                    else:
                        file.write(f"construct_{atr.atr_type}(x['{atr.atr_name}'])")

                    if 'Optional' in atr.changers:
                        file.write(" : undefined)")
                    file.write(",\n")

                file.write(f"{TAB}}};\n")

                for atr in msg.attributes:
                    if not atr.is_map:
                        continue

                    BASE_TAB = f"{TAB}"
                    if 'Optional' in atr.changers:
                        file.write(f"{TAB}if (Object.keys(x).includes('{atr.atr_name}')) {{\n")
                        BASE_TAB = f"{TAB}{TAB}"

                    file.write(
                        f"{BASE_TAB}Object.keys(x['{atr.atr_name}']).forEach(\n"
                        f"{BASE_TAB}{TAB}(obj_key: {atr.map_key_type}) => obj.{atr.atr_name}[obj_key] = "
                    )
                    if is_base_type(atr.map_value_type):
                        file.write(f"x['{atr.atr_name}'][obj_key]\n")
                    else:
                        file.write(f"construct_{atr.map_value_type}(x['{atr.atr_name}'][obj_key])\n")
                    file.write(f"{BASE_TAB});\n")

                    if 'Optional' in atr.changers:
                        file.write(f"{TAB}}}")
                file.write(
                    f"\n"
                    f"{TAB}return obj as {msg.name};"
                    f"}}\n\n\n"
                )
