import os
import logging

from py_common.py_utils import (
    ParseResult,
    TAB,
    _make_output_type,
)

logger = logging.Logger(__name__)


def generate_impl_file(parse_result: ParseResult, py_path: str) -> None:

    for service in parse_result.services:
        imp_path = os.path.join(py_path, f"{service.name}_impl.py")
        if os.path.exists(imp_path):
            logger.log(35, f"implementation file for service {service.name}  already exists, it won't be rewritten")
            continue
        logger.log(35, f"implementation file for service {service.name} doesn't exists, it will be created")

        with open(imp_path, "w") as file:
            file.write(
                f"from typing import Any, Dict, Tuple\n\n"
                f"from .api_services.service_{service.name} import Abstract{service.name}\n"
                f"from .api_services import generated_messages as msg\n"
                f"\n\n"
                f"class {service.name}(Abstract{service.name}):\n"
                f"\n"
            )

            for method in service.methods:

                # changers
                is_ses_auth = 'Session-auth' in method.changers

                file.write(f"{TAB}def {method.name}(")
                params = ['self']
                if method.input_type != "Null":
                    params.append(f'input_data: msg.{method.input_type}')
                if 'InputFiles' in method.changers:
                    params.append('files: Dict[str, bytes]')
                if is_ses_auth:
                    params.append('session: Any')
                file.write(", ".join(params))
                file.write(
                    f") -> {_make_output_type(method.output_type, use_msg=True)}:\n"
                    f"{TAB}{TAB}raise NotImplemented\n"
                    f"\n"
                )
                file.write("\n")
