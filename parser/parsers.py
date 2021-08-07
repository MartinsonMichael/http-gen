import json
import logging
import os
import re

from parser.parser_types import *
from parser.utils import (
    POSSIBLE_CHANGERS,
)
from parser.validator import post_process_parsed_results

logger = logging.Logger(__name__)


def parse_folder(proto_path: str) -> ParseResult:
    logger.log(35, f"parse folder {proto_path}...")
    result = ParseResult()

    # parse meta
    meta_path = os.path.join(proto_path, "META.json")
    if os.path.exists(meta_path):
        with open(meta_path) as file:
            meta_data: Dict[str, Any] = json.loads(file.read())
        result.meta = meta_data
        logging.log(35, f"Find meta: {result.meta}")

    for proto_file_path in os.listdir(proto_path):
        if proto_file_path.endswith(".proto"):
            buf: ParseResult = parse_file(os.path.join(proto_path, proto_file_path))
            result.messages.extend(buf.messages)
            result.services.extend(buf.services)

    logger.log(35, f"parse folder {proto_path} DONE")

    post_process_parsed_results(result)
    return result


def parse_file(proto_file_path: str) -> ParseResult:
    logger.log(35, f"parse file {proto_file_path}...")
    result = ParseResult()
    state = "none"

    msg: Message = Message()
    service: Service = Service()

    changers: List[str] = []

    for line in open(proto_file_path).readlines():
        if re.match(r"\s*\n", line) is not None:
            continue

        if re.match(r"\s*//.*\n", line) is not None:
            continue

        if re.match(rf"\s*@[\w|-]+\s*\n", line) is not None:
            m = re.match(rf"\s*@(?P<changer>{'|'.join(POSSIBLE_CHANGERS)})\s*\n", line)
            if m is None:
                logger.log(35, f"unknown changer in line:\n|{line}|")
                raise ValueError(f"unknown changer in line:\n|{line}|")
            changers.append(m.group('changer'))
            continue

        if state == "none":
            if line.startswith("message"):
                msg = Message(changers)
                changers: List[str] = []
                m = re.match(r"message\s+(?P<name>\w+)\s+{", line)
                msg.name = m.group('name')
                state = "msg"
                logger.log(35, f"start parse message {msg.name}")
                continue

            if line.startswith("service"):
                m = re.match(r"service\s+(?P<name>\w+)\s+{", line)
                service = Service(changers)
                changers: List[str] = []
                service.name = m.group('name')
                state = "service"
                logger.log(35, f"start parse service {service.name}")
                continue

        elif state == "msg":
            if re.match(r"\s*}", line) is not None:
                result.messages.append(msg)
                logger.log(35, f"add message {msg.name}")
                state = "none"
                continue

            m = re.match(
                r"\s*(?P<repeated>repeated)?\s*(?P<type>\w+)\s+(?P<name>\w+)(\s+=\s+(?P<number>\d+))?",
                line,
            )
            m_map = re.match(
                r"\s*map<(?P<map_key_type>\w+)\s*,\s*(?P<map_value_type>\w+)>\s+(?P<name>\w+)(\s+=\s+(?P<number>\d+))?",
                line,
            )
            if m is not None:
                msg.attributes.append(
                    MessageAttribute(
                        atr_name=m.group('name'),
                        atr_type=m.group('type'),
                        repeated=m.group('repeated') == 'repeated',
                        changers=changers,
                    )
                )
                changers: List[str] = []
            elif m_map is not None:
                msg.attributes.append(
                    MessageAttribute(
                        is_map=True,
                        atr_name=m_map.group('name'),
                        map_key_type=m_map.group('map_key_type'),
                        map_value_type=m_map.group('map_value_type'),
                        changers=changers,
                    )
                )
                changers: List[str] = []
            else:
                logger.log(35, f"unexpected message None match in line:\n|{line}|")

        elif state == "service":
            if re.match(r"\s*}", line) is not None:
                result.services.append(service)
                logger.log(35, f"add service {service.name}")
                state = "none"
                continue

            m = re.match(
                r"\s*rpc\s+(?P<name>\w+)\s*\(\s*(?P<input>\w+)\s*\)\s+returns\s+\(\s*(?P<output>\w+)\s*\)\s+{}",
                line
            )
            if m is not None:
                service.methods.append(
                    ServiceMethod(
                        name=m.group('name'),
                        input_type=m.group('input'),
                        output_type=m.group('output'),
                        changers=changers,
                    )
                )
                logger.log(35, f"add changers: '{', '.join(changers)}' to method {m.group('name')}")
                changers: List[str] = []
            else:
                logger.log(35, f"unexpected service None match in line:\n|{line}|")

    logger.log(35, f"parse file {proto_file_path} DONE")
    return result


def parse(proto_path: str) -> ParseResult:
    return parse_folder(proto_path)
