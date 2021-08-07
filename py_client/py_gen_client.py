import logging
import os

from parser import ParseResult

from py_common.py_messages import generate_messages
from py_client.py_client_methods import generate_client_methods

logger = logging.Logger(__name__)


def py_gen_client(parse_result: ParseResult, py_path: str, pytry: bool = False) -> None:
    logger.log(35, f"py Client generation [extra parameters: PyTry={pytry}]...\n")

    service_name = parse_result.meta.get('micro_service_name')

    gen_py_path = os.path.join(py_path, f"{service_name}Service_client")
    if not os.path.exists(gen_py_path):
        os.makedirs(gen_py_path)
    with open(os.path.join(gen_py_path, '__init__.py'), 'w') as file:
        file.write(
            f"from .generated_messages_{service_name.lower()}_client import *\n"
            f"from .{service_name.lower()}_client_methods import *\n\n"
        )

    generate_messages(
        parse_result,
        os.path.join(
            gen_py_path,
            f"generated_messages_{service_name.lower()}_client.py",
        )
    )
    generate_client_methods(parse_result, gen_py_path)

    logger.log(35, "py Client generation... DONE")
