import os

from ts_client.ts_microservice_utils import get_file_names
from ts_client.ts_utils import (
    ParseResult,
    HEAD,
    TAB,
)


def generate_axios_client(parse_result: ParseResult, ts_path: str) -> None:
    service_name = parse_result.meta.get("micro_service_name", "BACK")
    axiosInstance, messages_file_name, client_file_name = (
        get_file_names(parse_result.meta.get('micro_service_name', None))
    )

    base_api_address = parse_result.meta['address']
    base_address = base_api_address.split("api")[0]

    with open(os.path.join(ts_path, f"{client_file_name}.ts"), "w") as file:
        file.write(
            f"{HEAD}\n\n"
            f"\n"
            f"import axios from \"axios\";\n"
            f"import Cookies from \"universal-cookie\";\n"
            f"\n"
            f"const cookies = new Cookies();\n"
            f"cookies.set('token', localStorage.getItem(\"token\"), {{path: '/'}});\n"
            f"\n"
            f"export const BASE_{service_name}_API_ADDRESS = \"{base_api_address}\";\n"
            f"export const BASE_{service_name}_ADDRESS = \"{base_address}\";\n"
            f"\n"
            f"export const {axiosInstance} = axios.create({{\n"
            f"{TAB}baseURL: BASE_{service_name}_API_ADDRESS,\n"
            f"{TAB}responseType: \"json\",\n"
            f"{TAB}headers: {{\n"
            f"{TAB}{TAB}\"token\": localStorage.getItem(\"token\"),\n"
            f"{TAB}}}\n"
            f"}});\n"
        )

