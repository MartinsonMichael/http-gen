import logging
from typing import Optional
from datetime import datetime

from parser import (
    ParseResult,
    MessageAttribute,
    Message,
    ServiceMethod,
    find_message_by_name,
    is_base_type,
)

TAB = "    "
HEAD = f"""// This file is generated, DO NOT EDIT IT
// Michael Martinson http generator (c)
// Date: {datetime.now()}"""


logger = logging.Logger(__name__)


def _lower_first_letter(s: str) -> str:
    if len(s) == 0:
        return s
    return s[0].lower() + s[1:]


def _base_type_to_ts_types(atr_type: str) -> str:
    assert is_base_type(atr_type), f"Attempt to convert non base type {atr_type} ty ts base type"

    if atr_type == "int32":
        return "number"
    elif atr_type == "string":
        return "string"
    elif atr_type == "bytes":
        return "string"
    elif atr_type == "float":
        return "number"
    elif atr_type == "bool":
        return "boolean"
    else:
        ValueError(f"unknown base py type: {atr_type}")


def _make_map_type(atr: MessageAttribute) -> str:
    if is_base_type(atr.map_value_type):
        return (
            f"{{[key: {_base_type_to_ts_types(atr.map_key_type)}]: {_base_type_to_ts_types(atr.map_value_type)}}}"
        )
    else:
        return (
            f"{{[key: {_base_type_to_ts_types(atr.map_key_type)}]: {atr.map_value_type}}}"
        )


def _make_atr_with_type(atr: MessageAttribute, use_msg: Optional[bool] = None) -> str:
    ans = f"{atr.atr_name}"

    if 'Optional' in atr.changers:
        ans += "?"
    ans += ": "

    if is_base_type(atr.atr_type):
        ans += _base_type_to_ts_types(atr.atr_type)
    elif not atr.is_map:
        ans += f"{'msg.' if use_msg else ''}{atr.atr_type}"
    else:
        ans += f"{{ [key: {_base_type_to_ts_types(atr.map_key_type)}]:"
        if is_base_type(atr.map_value_type):
            ans += f" {_base_type_to_ts_types(atr.map_value_type)} }}"
        else:
            ans += f" {'msg.' if use_msg else ''}{atr.map_value_type} }}"
    if atr.repeated:
        ans += "[]"
    return ans


def _is_all_atr_basic(msg: Message) -> bool:
    for atr in msg.attributes:
        if not is_base_type(atr.atr_type):
            return False
    return True


def _has_basic_atr(msg: Message) -> bool:
    for atr in msg.attributes:
        if is_base_type(atr.atr_type):
            return True
    return False


def _has_map_atr(msg: Message) -> bool:
    for atr in msg.attributes:
        if atr.is_map:
            return True
    return False
