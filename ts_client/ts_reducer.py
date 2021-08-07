import logging
import os

from ts_client.ts_utils import (
    ParseResult,
    TAB,
    _lower_first_letter,
)

logger = logging.Logger(__name__)


def generate_reducer(parse_result: ParseResult, ts_path: str) -> None:
    for service in parse_result.services:
        dir_name = os.path.join(ts_path, _lower_first_letter(service.name))
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        file_path = os.path.join(dir_name, f"{_lower_first_letter(service.name)}_reducer.ts")
        if os.path.exists(file_path):
            logger.log(35, f"reducer for {service.name} already exist, it won't be recreated")
            continue
        logger.log(35, f"reducer for {service.name} doesn't exist, it would be created")

        with open(file_path, "w") as file:
            file.write(
                f'import * as msg from "../generated_messages"\n'
                f'import {{ {service.name}ActionType }} from "./{_lower_first_letter(service.name)}_actions"\n'
                f'\n\n'
            )

            file.write(
                f"export interface {service.name}State {{\n"
                f"{TAB}// TODO add valuable state, probably rename\n"
                f"\n"
                f"{TAB}isLoading: boolean\n"
                f"{TAB}error?: string\n"
                f"}}\n"
                f"\n"
                f"const initialState: {service.name}State = {{\n"
                f"{TAB}// TODO add valuable state, probably rename\n"
                f"\n"
                f"{TAB}isLoading: false,\n"
                f"{TAB}error: undefined,\n"
                f"}} as {service.name}State;\n"
                f"\n\n"
                f"export function {service.name}Reducer(state = initialState, action: {service.name}ActionType): {service.name}State {{\n"
                f"{TAB}switch (action.type) {{\n"
            )

            for i, method in enumerate(service.methods):
                file.write(
                    f'{TAB}{TAB}case "{method.name}_START":\n'
                    f"{TAB}{TAB}{TAB}return {{\n"
                    f"{TAB}{TAB}{TAB}{TAB}...state,\n"
                    f"{TAB}{TAB}{TAB}{TAB}isLoading: true,\n"
                    f"{TAB}{TAB}{TAB}{TAB}error: undefined,\n"
                    f"{TAB}{TAB}{TAB}}} as {service.name}State;\n"
                    f"\n"
                )
                file.write(
                    f'{TAB}{TAB}case "{method.name}_SUCCESS":\n'
                    f"{TAB}{TAB}{TAB}return {{\n"
                    f"{TAB}{TAB}{TAB}{TAB}...state,\n"
                    f"{TAB}{TAB}{TAB}{TAB}isLoading: false,\n"
                    f"{TAB}{TAB}{TAB}{TAB}error: undefined,\n"
                    f"{TAB}{TAB}{TAB}}} as {service.name}State;\n"
                    f"\n"
                )
                file.write(
                    f'{TAB}{TAB}case "{method.name}_REJECTED":\n'
                    f"{TAB}{TAB}{TAB}return {{\n"
                    f"{TAB}{TAB}{TAB}{TAB}...state,\n"
                    f"{TAB}{TAB}{TAB}{TAB}isLoading: false,\n"
                    f"{TAB}{TAB}{TAB}{TAB}error: action.payload,\n"
                    f"{TAB}{TAB}{TAB}}} as {service.name}State;\n"
                    f"\n"
                    f"\n"
                )

            file.write(
                f"{TAB}{TAB}default:\n"
                f"{TAB}{TAB}{TAB}return state\n"
                f"{TAB}}}\n"
                f"}}\n"
            )

