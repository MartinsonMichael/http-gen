import os

from py_common.py_utils import (
    ParseResult,
    MESSAGE_HEAD,
    TAB,
    _make_output_type,
    _make_input_type,
)


def generate_client_methods(parse_result: ParseResult, py_path: str) -> None:
    server_name = parse_result.meta['micro_service_name'].lower()
    with open(os.path.join(py_path, f"{server_name}_client_methods.py"), 'w') as file:
        file.write(MESSAGE_HEAD)
        file.write(
            f"import requests\n"
            f"import os\n"
            f"from .generated_messages_{server_name}_client import *\n"
            f"\n"
            f"\n"
        )
        for service in parse_result.services:
            file.write(f"assert '{service.name.upper()}_HOST_ADDRESS' in os.environ.keys(), \"You must specify '{service.name.upper()}_HOST_ADDRESS' as env variables\"\n\n\n")
            for method in service.methods:
                file.write(
                    f"def {server_name}_{method.name}({_make_input_type(method.input_type, 'input_msg')}) -> {_make_output_type(method.output_type)}:\n"
                    f"{TAB}{'response = ' if method.output_type != 'Null' else ''}requests.request(\n"
                    f"{TAB}{TAB}method=\"POST\",\n"
                    f"{TAB}{TAB}url=f\"{{os.environ['{service.name.upper()}_HOST_ADDRESS']}}{method.name}\",\n"
                )
                if method.input_type != "Null":
                    file.write(f"{TAB}{TAB}json=input_msg.to_json(),\n")
                file.write(
                    f"{TAB})\n"
                )
                file.write(f"{TAB}return ")
                if method.output_type == "Null":
                    file.write("None")
                else:
                    file.write(f"{method.output_type}.from_json(json.loads(response.content))")
                file.write("\n\n\n")
