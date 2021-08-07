import logging
import os

from py_common.py_utils import (
    ParseResult,
    TAB,
)

logger = logging.Logger(__name__)


def generate_session_auth(parse_result: ParseResult, session_auth_path: str) -> None:
    if os.path.exists(session_auth_path):
        logger.log(35, f"implementation file for Session-auth already exists, it won't be rewritten")
        return
    logger.log(35, f"implementation file for Session-auth doesn't exists, it will be created")

    with open(session_auth_path, "w") as file:
        file.write(
            f"from typing import Union, Any\n"
            f"\n"
            f"\n"
            f"def get_session_by_token(token: str) -> Union[Any, None]:\n"
            f'{TAB}"""\n'
            f'{TAB}This function should find session by given token\n'
            f'{TAB}Returns: session object (Any) if session exist, otherwise None\n'
            f'{TAB}"""\n'
            f"{TAB}raise NotImplemented\n"
            f"\n"
        )
