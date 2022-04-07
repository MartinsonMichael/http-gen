import logging

from parser.parser_types import *

logger = logging.Logger(__name__)


POSSIBLE_CHANGERS = [
    'Generate-once-ts', 'FLASK-do-not-generate',
    'Session-auth',
    'InputFiles', 'OutputFile',
    'Optional',
    'Permission'
]


def _comment_remover(s: str) -> str:
    if s == "":
        return ""
    if '//' not in s:
        return s
    if "\"" not in s and "'" not in s:
        return s.split('//')[0]
    prefix = ""

    # state possible variants:
    #   `-` - nothing
    #   `"` or `'` string begin
    #   `/` comment begin
    state = "-"  # or `"`, `'`, `/`
    for c in s + "//":
        if c != "/":
            prefix += c

        if state == "-":
            if c == "/":
                state = "/"
                continue
            if c == "\"" or c == "\'":
                state = c
        if state == "/":
            if c == "/":
                return prefix
            state = "-"
            if c == "\"" or c == "\'":
                state = c
                prefix = prefix[:-1] + "/" + prefix[-1]
        if state == "\"" or state == "\'":
            if state == c:
                state = "-"
    return s


def is_base_type(atr_type: str) -> bool:
    return atr_type in ['int32', 'string', 'float', 'bool', 'bytes']


def find_message_by_name(parser_result: ParseResult, msg_name: str) -> Message:
    for msg in parser_result.messages:
        if msg.name == msg_name:
            return msg

    raise ValueError(f"no such message: {msg_name}")
