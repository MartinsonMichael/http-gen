import os
import logging

from typing import Tuple, List

from parser import ParseResult
from py_common.py_messages import generate_messages
from py_common.py_utils import TAB

logging.basicConfig(level=os.environ.get('LOGGING_LEVEL', 'DEBUG'))
logger: logging.Logger = logging.getLogger(__name__)

FLASK_GENERATE_LINE_BEGIN = "# --- START OF GENERATED PART: DO NOT EDIT CODE BELLOW --- #"
FLASK_GENERATE_LINE_END = "# --- START OF GENERATED PART: DO NOT EDIT CODE UPPER --- #"

PYPATH_PREFIX = 'webapi'


def py_gen_server_flask(parse_result: ParseResult, py_path: str, pytry: bool = False) -> None:
    assert os.path.exists(py_path), "File with existing flask server doesn't exist"
    pre_lines, post_lines = _separate_input_py_file(py_path)

    logger.info(f"separated file:'{py_path}' into {len(pre_lines)} pre-lines and {len(post_lines)} post-lines")
    os.remove(py_path)
    logger.info(f"removed old file:'{py_path}'")

    with open(py_path, 'w') as file:
        for line in pre_lines:
            file.write(line)
        file.write(FLASK_GENERATE_LINE_BEGIN + '\n')
        logger.info("finished rewriting pre-lines")

        try:
            generated_lines = _simple_flask_generate(parse_result, py_path)
            for line in generated_lines:
                file.write(line)
                file.write("\n")
        except Exception as e:
            logger.critical(
                f"Exception while generating:\n"
                f"{str(e)}\n"
                f"restoring original file..."
            )

        logger.info("finished generated lines")
        file.write(FLASK_GENERATE_LINE_END + '\n')
        for line in post_lines:
            file.write(line)
        logger.info("finished rewriting post-lines")

    logger.info("done")


def _separate_input_py_file(py_path: str) -> Tuple[List[str], List[str]]:
    pre_lines = []
    post_lines = []

    with open(py_path, 'r') as file:
        all_lines = file.readlines()
        logger.info(f"Read {len(all_lines)} lines from path {py_path}")

    state = "pre"
    for line in all_lines:
        if line == FLASK_GENERATE_LINE_BEGIN or line == FLASK_GENERATE_LINE_BEGIN + '\n':
            if state == "pre":
                state = "middle"
            else:
                raise ValueError(
                    f"Found 'FLASK_GENERATE_LINE_BEGIN' not in 'pre' mode (but in '{state}')\n"
                    f"make sure that you file have structure:\n"
                    f"<some code>\n"
                    f"{FLASK_GENERATE_LINE_BEGIN}\n"
                    f"<generated code>\n"
                    f"{FLASK_GENERATE_LINE_END}\n"
                    f"<some code>"
                )
            continue
        if line == FLASK_GENERATE_LINE_END or line == FLASK_GENERATE_LINE_END + '\n':
            if state == "middle":
                state = "post"
            else:
                raise ValueError(
                    f"Found 'FLASK_GENERATE_LINE_BEGIN' not in 'middle' mode (but in '{state}')\n"
                    f"make sure that you file have structure:\n"
                    f"<some code>\n"
                    f"{FLASK_GENERATE_LINE_BEGIN}\n"
                    f"<generated code>\n"
                    f"{FLASK_GENERATE_LINE_END}\n"
                    f"<some code>"
                )
            continue

        if state == 'pre':
            pre_lines.append(line)
        if state == 'post':
            post_lines.append(line)

    return pre_lines, post_lines


def _simple_flask_generate(parse_result: ParseResult, py_path: str) -> List[str]:
    """

    :param parse_result:
    :param py_path:
    :return:
    """
    lines = ['\n', f'import {PYPATH_PREFIX}.generated_messages as msg']

    logger.info("Start to generate flask content...")
    folder_path, _ = os.path.split(py_path)
    msg_path = os.path.join(folder_path, 'generated_messages.py')
    generate_messages(parse_result, msg_path)
    logger.info("Messages generated")

    for service in parse_result.services:
        for method in service.methods:

            if 'FLASK-do-not-generate' in method.changers:
                logger.info(f"ignore implementation for  {method.name} due to 'FLASK-do-not-generate' flag")
                continue

            lines.append(f"from {PYPATH_PREFIX}.api_{method.name} import {method.name}")
            method_file_path = os.path.join(folder_path, f'api_{method.name}.py')

            if os.path.exists(method_file_path):
                logger.info(f"file for method {method.name} already exists")
                continue

            input_params = []
            if method.input_type != 'Null':
                input_params.append(f'input_data: msg.{method.input_type}')
            if 'Session-auth' in method.changers:
                input_params.append('user_id: int')
            if 'InputFiles' in method.changers:
                input_params.append('file_dict: ImmutableMultiDict[str, FileStorage]')

            output_type = f'msg.{method.output_type}' if method.output_type != 'Null' else 'None'

            with open(method_file_path, 'w') as file:
                file.write(
                    "from typing import Tuple, Union\n"
                    f"import {PYPATH_PREFIX}.generated_messages as msg\n"
                )
                if 'InputFiles' in method.changers:
                    file.write('from werkzeug.datastructures import ImmutableMultiDict, FileStorage\n')
                file.write(
                    "\n"
                    "\n"
                    f"def {method.name}({', '.join(input_params)}) -> Tuple[Union[{output_type}, str], int]:\n"
                    f"{TAB}\"\"\"\n"
                )
                if method.input_type != 'Null':
                    file.write(
                        f"{TAB}:param input_data: object of type {method.input_type} (see generated methods for more info)\n"
                    )
                if 'Session-auth' in method.changers:
                    file.write(
                        f"{TAB}:param user_id: int - id of user who perform this api method\n"
                    )
                if 'InputFiles' in method.changers:
                    file.write(
                        f"{TAB}:param file_dict: Dict[str, FileStorage] - input files, map of name to file object\n"
                    )
                file.write(
                    f"{TAB}:return  Tuple of two objects:\n"
                    f"{TAB}{TAB} * first - {output_type} | string - {output_type} if function call was successful,\n"
                    f"{TAB}{TAB}{TAB}string with error description otherwise\n"
                    f"{TAB}{TAB} * second - int - http code, if code not in range 200-299,\n"
                    f"{TAB}{TAB}{TAB}then the first object expected to be a string with error description\n"
                    f"{TAB}\"\"\"\n"
                    f"\n"
                    f"{TAB}raise NotImplemented\n"
                    f"\n"
                )

    lines.extend(['\n'])

    for service in parse_result.services:
        for method in service.methods:

            if 'FLASK-do-not-generate' in method.changers:
                logger.info(f"ignore generated part for for  {method.name} due to 'FLASK-do-not-generate' flag")
                continue

            if 'OutputFile' in method.changers:
                raise ValueError("'OutputFile' changer currently not implemented for flask, call @MichaelMD")

            lines.append(f"@app.post('/api/{method.name}')")

            impl_call_params = []
            if method.input_type != 'Null':
                impl_call_params.append('input_data')
            if 'Session-auth' in method.changers:
                impl_call_params.append('user_id')
                lines.append('@jwt_required()')

            if 'InputFiles' in method.changers:
                impl_call_params.append('request.files')

            lines.extend([
                f"def api_method_{method.name}() -> Tuple[Union[Response, str], int]:",
                f"{TAB}\"\"\"",
                f"{TAB}TODO @MichaelMD add comment auto generation",
                f"{TAB}\"\"\"",
            ])
            if 'Session-auth' in method.changers:
                lines.append(
                    f"{TAB}user_id: int = int(get_jwt_identity())"
                )
            if method.input_type != 'Null':
                lines.append(
                    f"{TAB}input_data: msg.{method.input_type} = msg.{method.input_type}.from_json(request.json)",
                )

            lines.extend([
                f"{TAB}output_data, code = {method.name}({', '.join(impl_call_params)})",
                f"{TAB}if code < 200 or 299 < code:",
                f"{TAB}{TAB}return output_data, code",
            ])

            if method.output_type != 'Null':
                lines.extend([
                    f"{TAB}assert isinstance(output_data, msg.{method.output_type}), \\",
                    f"{TAB}{TAB}f\"Wrong type of output_data, should be \'{method.output_type}\', got {{type(output_data)}}\"",
                    f"{TAB}return jsonify(output_data.to_json()), code",
                ])
            else:
                lines.extend([
                    f"{TAB}return '', code"
                ])

            lines.extend(['\n'])

    return lines
