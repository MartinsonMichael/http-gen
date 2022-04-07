import argparse
import logging
import sys
from typing import Optional

from nginx.nginx_gen import nginx_gen
from parser import parse, ParseResult
from py_server_django.py_gen_server import py_gen_server_django
from py_client.py_gen_client import py_gen_client
from py_server_flask.flask import py_gen_server_flask
from ts_client.ts_gen import ts_gen


logging.basicConfig(stream=sys.stdout, level=35)
logger = logging.Logger(__name__)


def main(
    proto_path: str,
    py_server_django_path: Optional[str] = None,
    py_server_flask_path: Optional[str] = None,
    py_client_path: Optional[str] = None,
    ts_path: Optional[str] = None,
    nginx_path: Optional[str] = None,
    pytry: bool = False,
):
    logger.log(35, f"Michael Martinson proto generator, Welcome!\nproto path: {proto_path}\n\n")

    parse_result: ParseResult = parse(proto_path)
    logger.log(35, "Parsed data correct!")

    if py_server_django_path is not None:
        py_gen_server_django(parse_result, py_server_django_path, pytry)

    if py_server_flask_path is not None:
        py_gen_server_flask(parse_result, py_server_flask_path, pytry)

    if py_client_path is not None:
        py_gen_client(parse_result, py_client_path, pytry)

    if ts_path is not None:
        ts_gen(parse_result, ts_path)

    if nginx_path is not None:
        nginx_gen(parse_result, nginx_path)

    logger.log(35, "Generation finished.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--proto-path', type=str)
    parser.add_argument('--py-server-django', type=str, default=None)
    parser.add_argument('--py-server-flask', type=str, default=None)

    parser.add_argument('--py-client', type=str, default=None)

    parser.add_argument('--ts-path', type=str, default=None)

    parser.add_argument('--nginx-path', type=str, default=None)

    parser.add_argument('--pytry', default=False, action='store_true')

    args = parser.parse_args()
    main(
        args.proto_path,
        args.py_server_django, args.py_server_flask, args.py_client,
        args.ts_path, args.nginx_path,
        pytry=args.pytry,
    )
