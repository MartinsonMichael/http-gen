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

                params = ['self']
                if method.input_type != "Null":
                    params.append(f'args: msg.{method.input_type}')
                # if 'InputFiles' in method.changers:
                #     params.append('files: Dict[str, UploadedFile]')
                params.append("request: HttpRequest")
                # if is_ses_auth:
                #     params.append('session: Any')
                params.append("user_info: AuthUserInfo")

                file.write(
                    f"{TAB}@csrf_exempt\n"
                    f"{TAB}def call__{method.name}(self, request) -> {_make_output_type(method.output_type, file_output='OutputFile' in method.changers, use_msg=True)}:\n"
                    f"{TAB}{TAB}return self.{method.name}("
                )
                if method.input_type != "Null":
                    file.write('request.input_msg, ')
                file.write(
                    f"request, request.user_info)\n\n"
                )

                # # changers
                # is_ses_auth = 'Session-auth' in method.changers
                # if is_ses_auth:
                #     file.write(
                #         f"{TAB}{TAB}token = request.headers.get('token', '')\n"
                #         f"{TAB}{TAB}if token in '':\n"
                #         f"{TAB}{TAB}{TAB}token = request.COOKIES.get('token', '')\n"
                #     )
                #     if 'Permission' in method.changers:
                #         file.write(f"{TAB}{TAB}permissions = [\"{method.changer_obj['Permission']}\"]\n")
                #     else:
                #         file.write(f"{TAB}{TAB}permissions = None\n")
                #     file.write(
                #         f"{TAB}{TAB}session = get_session_by_token(token, request, permissions)\n"
                #         f"{TAB}{TAB}if session is None:\n"
                #         f"{TAB}{TAB}{TAB}return make_response(f'Unauthorized', 401)\n"
                #         f"\n"
                #     )
                #
                # if method.input_type != "Null":
                #     BASE_TAB = f"{TAB}{TAB}"
                #     if pytry:
                #         file.write(f"{TAB}{TAB}try:\n")
                #         BASE_TAB = f"{TAB}{TAB}{TAB}"
                #     if 'InputFiles' in method.changers:
                #         file.write(
                #             f"{BASE_TAB}input_data = None\n"
                #             f"{BASE_TAB}assert \"multipart/form-data; boundary=\" in request.headers['Content-Type']\n"
                #             f"{BASE_TAB}boundary = request.headers['Content-Type'].split(\"boundary=\")[1].encode('utf-8')\n"
                #             f"{BASE_TAB}start = b'\\r\\nContent-Disposition: form-data; name=\"non_file_json_data\"\\r\\n\\r\\n'\n"
                #             f"{BASE_TAB}for part in request.body.split(boundary):\n"
                #             f"{BASE_TAB}{TAB}if start in part:\n"
                #             f"{BASE_TAB}{TAB}{TAB}data_part = part[len(start):-4].decode('utf-8')\n"
                #             f"{BASE_TAB}{TAB}{TAB}input_data: msg.{method.input_type} = msg.{method.input_type}.from_json(json.loads(data_part))\n"
                #             f"\n"
                #             f"{BASE_TAB}if input_data is None:\n"
                #             f"{BASE_TAB}{TAB}raise ValueError(\"Can't find form data\")\n"
                #         )
                #     else:
                #         file.write(
                #             f"{BASE_TAB}input_data: msg.{method.input_type} = msg.{method.input_type}.from_json(json.loads(request.body))\n"
                #         )
                #     if pytry:
                #         file.write(
                #             f"{TAB}{TAB}except Exception as e:\n"
                #             f'{TAB}{TAB}{TAB}return make_response(f"error while parsing request:\\n{{str(e)}}", 400)\n'
                #             f"\n"
                #         )
                #     else:
                #         file.write("\n")
                #
                # BASE_TAB = f"{TAB}{TAB}"
                # if pytry:
                #     file.write(f"{TAB}{TAB}try:\n")
                #     BASE_TAB = f"{TAB}{TAB}{TAB}"
                #
                # file.write(f"{BASE_TAB}")
                # if method.output_type != "Null":
                #     file.write(f"output_data: msg.{method.output_type} = ")
                # elif 'OutputFile' in method.changers:
                #     file.write(f"file_path: str = ")
                # file.write(f"self.{method.name}(")
                #
                # params = []
                # if method.input_type != "Null":
                #     params.append('input_data')
                # if 'InputFiles' in method.changers:
                #     params.append('request.FILES')
                # if is_ses_auth:
                #     params.append('session')
                # file.write(", ".join(params))
                # file.write(")\n")
                # if pytry:
                #     file.write(
                #         f"{TAB}{TAB}except ValueError as e:\n"
                #         f'{TAB}{TAB}{TAB}return make_response(str(e), 400)\n'
                #         f"{TAB}{TAB}except Exception as e:\n"
                #         f'{TAB}{TAB}{TAB}return make_response(f"error while processing request:\\n{{str(e)}}", 400)\n'
                #         f"\n"
                #     )
                #
                # if method.output_type != "Null":
                #     file.write(
                #         f"{TAB}{TAB}return make_response(\n"
                #         f"{TAB}{TAB}{TAB}content=json.dumps(output_data.to_json()),\n"
                #         f"{TAB}{TAB}{TAB}status=200,\n"
                #         f"{TAB}{TAB})\n"
                #     )
                # elif 'OutputFile' in method.changers:
                #     file.write(
                #         f"{TAB}{TAB}return make_response(\n"
                #         f'{TAB}{TAB}{TAB}content="",\n'
                #         f"{TAB}{TAB}{TAB}status=200,\n"
                #         f"{TAB}{TAB}{TAB}file_path=file_path,\n"
                #         f"{TAB}{TAB})\n"
                #     )
                # else:
                #     file.write(
                #         f"{TAB}{TAB}return make_response()\n"
                #     )
                # file.write(
                #     f"\n"
                # )

                # deferred
                file.write(f"{TAB}def {method.name}(")
                file.write(", ".join(params))
                file.write(
                    f") -> {_make_output_type(method.output_type, file_output='OutputFile' in method.changers, use_msg=True)}:\n"
                    f"{TAB}{TAB}raise RPCException(error_msg='not implemented')\n"
                    f"\n"
                )
            file.write("\n")
