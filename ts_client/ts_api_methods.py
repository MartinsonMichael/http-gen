import os
from typing import TextIO

from ts_client.ts_microservice_utils import get_file_names
from ts_client.ts_utils import (
    ParseResult,
    ServiceMethod,
    Message,
    HEAD,
    TAB,
    find_message_by_name,
    is_base_type,
    _base_type_to_ts_types,
    _lower_first_letter,
    _make_atr_with_type,
)


def _write_method_to_file(
    method: ServiceMethod,
    file: TextIO,
    parse_result: ParseResult,
    axiosInstance: str,
    export_action_interface: bool = False,
) -> None:
    file.write(
        f'export const {method.name}_START = "{method.name}_START";\n'
        f"{'export ' if export_action_interface else ''}interface {method.name}_START_Action {{\n"
        f"{TAB}type: typeof {method.name}_START\n"
        f"{TAB}payload: undefined\n"
        f"}}\n"
    )
    file.write(
        f'export const {method.name}_SUCCESS = "{method.name}_SUCCESS";\n'
        f"{'export ' if export_action_interface else ''}interface {method.name}_SUCCESS_Action {{\n"
        f"{TAB}type: typeof {method.name}_SUCCESS\n"
    )
    if method.output_type == "Null":
        file.write(f"{TAB}payload: undefined\n")
    elif is_base_type(method.output_type):
        file.write(f"{TAB}payload: {_base_type_to_ts_types(method.output_type)}\n")
    else:
        file.write(f"{TAB}payload: msg.{method.output_type}\n")
    file.write(f"}}\n")

    file.write(
        f'export const {method.name}_REJECTED = "{method.name}_REJECTED";\n'
        f"{'export ' if export_action_interface else ''}interface {method.name}_REJECTED_Action {{\n"
        f"{TAB}type: typeof {method.name}_REJECTED\n"
        f"{TAB}payload: string\n"
        f"}}\n"
    )
    file.write("\n")

    file.write(
        f"export const {method.name} = ("
    )

    input_params = []
    if method.input_type != "Null":
        msg: Message = find_message_by_name(parse_result, method.input_type)
        for i, atr in enumerate(msg.attributes):
            input_params.append(_make_atr_with_type(atr, use_msg=True))
    if 'InputFiles' in method.changers:
        input_params.append('files: FormData')
    input_params = sorted(input_params, key=lambda x: 0 if '?' not in x else 1)
    file.write(", ".join(input_params))

    file.write(
        f") => {{\n"
        f"{TAB}return async (dispatch: any) => {{\n"
        f"{TAB}{TAB}dispatch({{type: {method.name}_START, payload: undefined}});\n"
        f"\n"
    )

    # add  data into multi-form in case of files
    if 'InputFiles' in method.changers and method.input_type != "Null":
        file.write(
            f"{TAB}{TAB}files.append(\"non_file_json_data\", JSON.stringify({{\n"
        )
        msg: Message = find_message_by_name(parse_result, method.input_type)
        for atr in msg.attributes:
            file.write(f"{TAB}{TAB}{TAB}'{atr.atr_name}': {atr.atr_name},\n")
        file.write(
            f"{TAB}{TAB}}}));\n\n"
        )

    file.write(
        f"{TAB}{TAB}await {axiosInstance}.post(\n"
        f"{TAB}{TAB}{TAB}'{method.name}',\n"
    )
    if method.input_type != "Null":
        if 'InputFiles' not in method.changers:
            msg: Message = find_message_by_name(parse_result, method.input_type)
            file.write(f"{TAB}{TAB}{TAB}{{\n")
            for atr in msg.attributes:
                file.write(f"{TAB}{TAB}{TAB}{TAB}'{atr.atr_name}': {atr.atr_name},\n")
            file.write(f"{TAB}{TAB}{TAB}}},\n")

    if 'InputFiles' in method.changers:
        file.write(
            f"{TAB}{TAB}{TAB}files,\n"
        )

    file.write(
        # f"{TAB}{TAB}{TAB}{{\n"
        # f"{TAB}{TAB}{TAB}{TAB}'headers': {{\n"
        # f"{TAB}{TAB}{TAB}{TAB}{TAB}'Access-Control-Allow-Origin': '*',\n"
        # f"{TAB}{TAB}{TAB}{TAB}{TAB}'Access-Control-Allow-Headers': '*',\n"
        # f"{TAB}{TAB}{TAB}{TAB}}},\n"
        # f"{TAB}{TAB}{TAB}}},\n"
        f"{TAB}{TAB})"
    )
    # then
    file.write(
        f".then(\n"
        f"{TAB}{TAB}{TAB}(response: AxiosResponse<msg.{method.output_type}, any>) => {{\n"
        f'{TAB}{TAB}{TAB}{TAB}if (!Object.keys(response.headers).includes("error")) {{\n'
        f"{TAB}{TAB}{TAB}{TAB}{TAB}dispatch({{type: {method.name}_SUCCESS, payload: "
    )
    if method.output_type == "Null":
        file.write(f"undefined}});\n")
    # NOTE commented, because not axios data already have proper type
    # elif is_base_type(method.output_type):
    #     file.write(f"response.data}});\n")
    else:
        file.write(f"msg.construct_{method.output_type}(response.data)}});\n")
    file.write(
        f"{TAB}{TAB}{TAB}{TAB}}} else {{\n"
        f"{TAB}{TAB}{TAB}{TAB}{TAB}dispatch({{type: {method.name}_REJECTED, payload: response.data}});\n"
        # f"{TAB}{TAB}{TAB}{TAB}{TAB}dispatch(addErrorToQueue(response.data));\n"
        f"{TAB}{TAB}{TAB}{TAB}}}\n"
        f"{TAB}{TAB}{TAB}}}\n"
        f"{TAB}{TAB})"
    )
    # catch
    file.write(
        f".catch(\n"
        f"{TAB}{TAB}{TAB}(error: any) => {{\n"
        f'{TAB}{TAB}{TAB}{TAB}dispatch({{type: {method.name}_REJECTED, payload: error.toString()}});\n'
        # f'{TAB}{TAB}{TAB}{TAB}dispatch(addErrorToQueue("Server side error"));\n'
        f"{TAB}{TAB}{TAB}}}\n"
        f"{TAB}{TAB});\n"
    )

    file.write(
        f"{TAB}}}\n"
        f"}};\n\n\n"
    )


def generate_methods(parse_result: ParseResult, ts_path: str) -> None:
    for service in parse_result.services:
        dir_name = os.path.join(ts_path, _lower_first_letter(service.name))
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

        # axiosInstance = "axiosInstance"
        # messages_file_name = "generated_messages"
        # client_file_name = "client"
        # service_name = parse_result.meta.get('micro_service_name', None)
        # if service_name is not None:
        #     axiosInstance = f"axiosInstance{service_name}"
        #     client_file_name = f"client_{service_name.lower()}"
        #     # messages_file_name = f"generated_messages_{service_name.lower()}"
        axiosInstance, messages_file_name, client_file_name = (
            get_file_names(parse_result.meta.get('micro_service_name', None))
        )

        COMMON_METHOD_HEADER = (
            f"{HEAD}\n\n"
            f'import {{ {axiosInstance} }} from "../{client_file_name}"\n'
            f'import * as msg from "../{messages_file_name}"\n'
            f'import {{ AxiosResponse }} from "axios";\n'
            # f'import {{ addErrorToQueue }} from "../notificationService/notificationService_actions";\n'
            f'\n\n'
        )
        with open(os.path.join(dir_name, f"{_lower_first_letter(service.name)}_actions.ts"), "w") as file:
            file.write(COMMON_METHOD_HEADER)
            for method in service.methods:
                if 'Generate-once-ts' in method.changers:
                    file.write(
                        f'import {{ '
                        f"{method.name}_START_Action, "
                        f"{method.name}_SUCCESS_Action, "
                        f"{method.name}_REJECTED_Action "
                        f'}} from "./{_lower_first_letter(method.name)}_action"\n'
                    )
            file.write("\n\n")

            for method in service.methods:
                if 'Generate-once-ts' in method.changers:
                    continue
                _write_method_to_file(method, file, parse_result, axiosInstance)

            file.write(
                f"\nexport type {service.name}ActionType = (\n"
            )
            for i, method in enumerate(service.methods):
                file.write(
                    f"{TAB}{method.name}_START_Action |\n"
                    f"{TAB}{method.name}_SUCCESS_Action |\n"
                    f"{TAB}{method.name}_REJECTED_Action {'|' if i + 1 < len(service.methods) else ''}\n"
                )
            file.write(
                f")"
            )

        for method in service.methods:
            if 'Generate-once-ts' not in method.changers:
                continue
            file_name = os.path.join(dir_name, f"{_lower_first_letter(method.name)}_action.ts")
            if os.path.exists(file_name):
                continue
            with open(file_name, "w") as file:
                file.write(COMMON_METHOD_HEADER)
                _write_method_to_file(method, file, parse_result, axiosInstance, export_action_interface=True)
