import logging
import os
from typing import Optional

from parser import ParseResult

from py_server.py_django_urls import generate_urls
from py_server.py_implementation import generate_impl_file
from py_common.py_messages import generate_messages
from py_server.py_service import generate_services
from py_server.py_session_auth import generate_session_auth

logger = logging.Logger(__name__)


def py_gen_server(parse_result: ParseResult, py_path: str, pytry: bool = False) -> None:
    logger.log(35, f"py Server generation [extra parameters: PyTry={pytry}]...")

    gen_py_path = os.path.join(py_path, 'api_services')
    if not os.path.exists(gen_py_path):
        os.makedirs(gen_py_path)
        with open(os.path.join(gen_py_path, '__init__.py'), 'w') as file:
            file.write("")

    generate_messages(parse_result, os.path.join(gen_py_path, "generated_messages.py"))
    generate_services(parse_result, gen_py_path, pytry)

    generate_impl_file(parse_result, py_path)
    generate_urls(parse_result, os.path.join(py_path, "api_urls.py"))

    generate_session_auth(parse_result, os.path.join(gen_py_path, 'session_auth.py'))
    logger.log(35, "py Server generation... DONE")
