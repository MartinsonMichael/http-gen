import os

from parser import ParseResult
from py_common.py_utils import TAB


def generate_url2msg_mapping(parse_result: ParseResult, py_path: str) -> None:
    with open(os.path.join(py_path, "url2map.py"), "w") as file:
        file.write(
            "from .generated_messages import *\n\n"
            "URL_TO_MSG_MAPPING = {\n"
        )
        for service in parse_result.services:
            for method in service.methods:
                access_control = "'admin'" if 'Admin-auth' in method.changers else "'session'" if 'Session-auth' in method.changers else None
                file.write(
                    f"{TAB}'{method.name}': {{\n"
                    f"{TAB}{TAB}'input_msg_name': '{method.input_type}',\n"
                    f"{TAB}{TAB}'input_msg': {method.input_type if method.input_type != 'Null' else 'None'},\n"
                    f"{TAB}{TAB}'has_input_file': {'True' if 'InputFiles' in method.changers else 'False'},\n"
                    f"{TAB}{TAB}'output_msg_name': '{method.output_type}',\n"
                    f"{TAB}{TAB}'output_msg': {method.output_type if method.output_type != 'Null' else 'None'},\n"
                    f"{TAB}{TAB}'has_output_file': {'True' if 'OutputFile' in method.changers else 'False'},\n"
                    f"{TAB}{TAB}'access_control': {access_control}\n"
                    f"{TAB}}},"
                    f"\n"
                )
        file.write("}\n")
