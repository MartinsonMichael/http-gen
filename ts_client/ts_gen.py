import logging
import os

from parser import ParseResult

from ts_client.ts_api_methods import generate_methods
from ts_client.ts_axios import generate_axios_client
from ts_client.ts_message_service import generate_message_service
from ts_client.ts_messages import generate_messages
from ts_client.ts_reducer import generate_reducer

logger = logging.Logger(__name__)


def ts_gen(parse_result: ParseResult, ts_path: str) -> None:
    logger.log(35, "ts generation...")

    generate_messages(parse_result,ts_path)
    generate_methods(parse_result, ts_path)
    generate_reducer(parse_result, ts_path)

    # generate_message_service(ts_path)
    # generate_axios_client(parse_result, ts_path)

    logger.log(35, "ts generation DONE")
