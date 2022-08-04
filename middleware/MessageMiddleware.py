import json

from typing import Union, Callable, Optional
from django.http import HttpResponse, HttpRequest, FileResponse

from webapi.methods.api_services.url2map import URL_TO_MSG_MAPPING
from webapi.middleware.AuthMiddleware import AuthUserInfo


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

        if request.method == 'OPTION':
            return HttpResponse(content='use RPC')

        method_name = request.path.split('/')[-1] if '/' in request.path else request.path

        if method_name not in URL_TO_MSG_MAPPING.keys():
            return HttpResponse(content="invalid api method", status=400)

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
                        f"invalid message, expect {api_description['input_msg_nams']}, got: {request.body.decode()}"
                    ),
                    status=400,
                )
        else:
            input_msg = None

        user_info = None
        if hasattr(request, 'user'):
            user_info = request.user

        try:
            request.input_msg = input_msg
            request.user_info = user_info
            response = self._get_response(request)
        except RPCException as e:
            return HttpResponse(
                content=json.dumps({"error_msg": str(e)}),
                status=400,
            )
        except Exception as e:
            return HttpResponse(
                content=json.dumps({"error_msg": f"unexpected error:\n{str(e)}"}),
                status=400,
            )

        if api_description['output_msg'] is not None:
            if not isinstance(response, api_description['output_msg']):
                return HttpResponse(
                    content=json.dumps({
                        "error_msg": (
                            f"unexpected msg, expected {api_description['output_msg_name']}, but got:\n{str(response)}"
                        )
                    }),
                    status=500,
                )
        if api_description['has_output_file']:
            if not isinstance(response, str):
                return HttpResponse(
                    content=json.dumps({"error_msg": f"unexpected str:file_path, but got:\n{str(response)}"}),
                    status=500,
                )

        if api_description['has_output_file']:
            return FileResponse(open(response, 'rb'))

        response = HttpResponse(content=json.dumps(response.to_json()), status=200)
        response.headers['Content-Type'] = "json"
        response.headers["Access-Control-Allow-Origin"] = "*"
        return response
