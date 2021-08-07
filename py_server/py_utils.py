import logging
from typing import Optional

from utils import ParseResult, MessageAttribute, is_base_type, Service

logger = logging.Logger(__name__)

TAB = "    "
HEAD = """# This file is generated, DO NOT EDIT IT
# Michael Martinson http generator (c)"""

MESSAGE_HEAD = f"""{HEAD}

from typing import List, Dict, Union, Any
import json


"""
SERVICE_HEAD = f"""{HEAD}

from typing import Optional

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpRequest, FileResponse

from .generated_messages import *
from .session_auth import get_session_by_token


def _make_message_response(content: str = "") -> HttpResponse:
    return HttpResponse(content=content)


def _make_file_response(file_path) -> FileResponse:
    return FileResponse(open(file_path, 'rb'))


def make_response(
        content: str = "", 
        status: int = 200, 
        file_path: Optional[str] = None
    ) -> Union[HttpResponse, FileResponse]:
    if file_path is not None:
        response = _make_file_response(file_path)
    else:
        response =  _make_message_response(content)
    response.status = 200
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Headers"] = "*"
    if status != 200:
        response["error"] = status
        response["Access-Control-Expose-Headers"] = "error"
    return response


"""


def _base_type_to_py_types(atr_type: str) -> str:
    assert is_base_type(atr_type), f"Attempt to convert non base type {atr_type} ty py base type"

    if atr_type == "int32":
        return "int"
    elif atr_type == "string":
        return "str"
    elif atr_type == "bytes":
        return "bytes"
    elif atr_type == "float":
        return "float"
    elif atr_type == "bool":
        return "bool"
    else:
        ValueError(f"unknown base py type: {atr_type}")


def _make_py_type(atr_type: str) -> str:
    if is_base_type(atr_type):
        return _base_type_to_py_types(atr_type)
    else:
        return f"'{atr_type}'"


def _make_atr_type(atr: MessageAttribute) -> str:
    ans = ""
    if 'Optional' in atr.changers:
        ans += "Optional["
    if atr.is_map:
        ans += f"Dict[{_make_py_type(atr.map_key_type)}, {_make_py_type(atr.map_value_type)}]"
    if atr.repeated:
        ans += f"List["
    ans += _make_py_type(atr.atr_type)
    if atr.repeated:
        ans += "]"
    if 'Optional' in atr.changers:
        ans += "]"
    return ans


def _make_attribute_declaration(atr: MessageAttribute) -> str:
    return f"{atr.atr_name}: {_make_atr_type(atr)}"


def _is_any_method_has_changer(service: Service, changer: str) -> bool:
    for method in service.methods:
        if changer in method.changers:
            return True
    return False


def _make_output_type(
        output_type: str,
        use_msg: Optional[bool] = None,
        file_output: Optional[bool] = None,
) -> str:
    if file_output:
        return "str"
    if output_type == "Null":
        return "None"
    if is_base_type(output_type):
        return output_type

    if use_msg:
        return f"msg.{output_type}"
    return output_type
