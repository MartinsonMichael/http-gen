import os

from py_common.py_utils import (
    ParseResult,
    make_service_head,
    TAB,
    _make_output_type,
)


def generate_services(parse_result: ParseResult, service_path: str, pytry: bool) -> None:
    for service in parse_result.services:

        with open(os.path.join(service_path, f"service_{service.name}.py"), "w") as file:
            file.write(make_service_head(parse_result))

            file.write(f"class Abstract{service.name}:\n\n")
            for method in service.methods:
                file.write(
                    f"{TAB}@csrf_exempt\n"
                    f"{TAB}def service_{method.name}(self, request: HttpRequest, **kwargs) -> HttpResponse:\n"
                    f"{TAB}{TAB}if request.method == 'OPTIONS':\n"
                    f"{TAB}{TAB}{TAB}return make_response()\n"
                    f"\n"
                )
                if method.input_type != "Null":
                    BASE_TAB = f"{TAB}{TAB}"
                    if pytry:
                        file.write(f"{TAB}{TAB}try:\n")
                        BASE_TAB = f"{TAB}{TAB}{TAB}"
                    file.write(
                        f"{BASE_TAB}input_data: msg.{method.input_type} = msg.{method.input_type}.from_json(json.loads(request.body))\n"
                    )
                    if pytry:
                        file.write(
                            f"{TAB}{TAB}except Exception as e:\n"
                            f'{TAB}{TAB}{TAB}return make_response(f"error while parsing request:\\n{{str(e)}}", 400)\n'
                            f"\n"
                        )

                # changers
                is_ses_auth = 'Session-auth' in method.changers
                if is_ses_auth:
                    file.write(
                        f"{TAB}{TAB}token = request.headers.get('token', '')\n"
                        f"{TAB}{TAB}if token in '':\n"
                        f"{TAB}{TAB}{TAB}token = request.COOKIES.get('token', '')\n"
                        f"{TAB}{TAB}session = get_session_by_token(token)\n"
                        f"{TAB}{TAB}if session is None:\n"
                        f"{TAB}{TAB}{TAB}return make_response(f'Unauthorized', 401)\n"
                        f"\n"
                    )

                BASE_TAB = f"{TAB}{TAB}"
                if pytry:
                    file.write(f"{TAB}{TAB}try:\n")
                    BASE_TAB = f"{TAB}{TAB}{TAB}"

                file.write(f"{BASE_TAB}")
                if method.output_type != "Null":
                    file.write(f"output_data: msg.{method.output_type} = ")
                elif 'OutputFile' in method.changers:
                    file.write(f"file_path: str = ")
                file.write(f"self.{method.name}(")

                params = []
                if method.input_type != "Null":
                    params.append('input_data')
                if 'InputFiles' in method.changers:
                    params.append('request.FILES')
                if is_ses_auth:
                    params.append('session')
                file.write(", ".join(params))
                file.write(")\n")
                if pytry:
                    file.write(
                        f"{TAB}{TAB}except ValueError as e:\n"
                        f'{TAB}{TAB}{TAB}return make_response(str(e), 400)\n'
                        f"{TAB}{TAB}except Exception as e:\n"
                        f'{TAB}{TAB}{TAB}return make_response(f"error while processing request:\\n{{str(e)}}", 400)\n'
                        f"\n"
                    )

                if method.output_type != "Null":
                    file.write(
                        f"{TAB}{TAB}return make_response(\n"
                        f"{TAB}{TAB}{TAB}content=json.dumps(output_data.to_json()),\n"
                        f"{TAB}{TAB}{TAB}status=200,\n"
                        f"{TAB}{TAB})\n"
                    )
                elif 'OutputFile' in method.changers:
                    file.write(
                        f"{TAB}{TAB}return make_response(\n"
                        f'{TAB}{TAB}{TAB}content="",\n'
                        f"{TAB}{TAB}{TAB}status=200,\n"
                        f"{TAB}{TAB}{TAB}file_path=file_path,\n"
                        f"{TAB}{TAB})\n"
                    )
                else:
                    file.write(
                        f"{TAB}{TAB}return make_response()\n"
                    )
                file.write(
                    f"\n"
                )

                # deferred
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
                    f") -> {_make_output_type(method.output_type, file_output='OutputFile' in method.changers, use_msg=True)}:\n"
                    f"{TAB}{TAB}raise NotImplemented\n"
                    f"\n"
                )
            file.write("\n")
