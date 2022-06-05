import json

from typing import Union, Callable, Optional
from django.http import HttpResponse, HttpRequest, FileResponse

from kb.api_services.url2map import URL_TO_MSG_MAPPING


class RPCException(Exception):

    def __init__(self, error_msg: Optional[str] = None):
        super(RPCException, self).__init__()
        self.error_msg = error_msg

    def __str__(self) -> str:
        if self.error_msg is not None:
            return self.error_msg
        return "rpc error"

    __repr__ = __str__


class MessageCreatorMiddleware:

    def __init__(self, get_response: Callable):
        self._get_response = get_response

    def __call__(self, request: HttpRequest) -> Union[HttpResponse, FileResponse]:

        print(request.get_raw_uri(), request.path)

        if request.method == 'OPTION':
            return HttpResponse(content='use RPC')

        if request.path not in URL_TO_MSG_MAPPING.keys():
            return HttpResponse(content="invalid api method", status=400)

        method_name = request.path
        api_description = URL_TO_MSG_MAPPING[method_name]

        if api_description['input_msg'] is not None:
            try:
                json_body = json.loads(request.body.decode())
                input_msg = api_description['input_msg'].from_json(json_body)
            except json.JSONDecodeError:
                return HttpResponse(content="invalid JSON", status=400)
            except KeyError:
                return HttpResponse(
                    content=(
                        f"invalid message, expect {api_description['input_msg_nams']}, "
                        f"got: {request.body.decode()}"
                    ),
                    status=400,
                )
        else:
            input_msg = None

        try:
            if input_msg is not None:
                response = self._get_response(input_msg, request.user, request)
            else:
                response = self._get_response(request.user, request)
        except RPCException as e:
            return HttpResponse(
                content=json.dumps({"error_msg": str(e), "row_error": ""}),
                status=400,
            )
        except Exception as e:
            return HttpResponse(
                content=json.dumps({"error_msg": "unexpected error", "row_error": str(e)}),
                status=400,
            )

        if api_description['output_msg'] is not None:
            if not isinstance(response, api_description['output_msg']):
                return HttpResponse(
                    content=json.dumps({
                        "error_msg": (
                            f"unexpected msg, expected {api_description['output_msg_name']}, "
                            f"but got:\n{str(response)}"
                        ),
                        "row_error": ""
                    }),
                    status=500,
                )
        if api_description['has_output_file']:
            if not isinstance(response, str):
                return HttpResponse(
                    content=json.dumps({
                        "error_msg": (
                            f"unexpected str:file_path,"
                            f"but got:\n{str(response)}"
                        ),
                        "row_error": ""
                    }),
                    status=500,
                )

        if api_description['has_output_file']:
            return FileResponse(open(response, 'rb'))

        return HttpResponse(content=json.dumps(response.to_json()), status=200)
