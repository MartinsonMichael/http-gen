import logging
import os

from ts_client.ts_utils import (
    HEAD,
    TAB,
    _lower_first_letter,
)

logger = logging.Logger(__name__)


def generate_message_service(ts_path: str) -> None:
    service_name = "notificationService"
    dir_name = os.path.join(ts_path, _lower_first_letter(service_name))
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

    # reducer
    reducer_path = os.path.join(dir_name, f"{service_name}_reducer.ts")
    with open(reducer_path, 'w') as file:
        file.write(
            f'import * as msg from "../generated_messages"\n'
            f'import {{ {service_name}ActionType }} from "./{_lower_first_letter(service_name)}_actions"\n'
            f'\n\n'
        )
        file.write(
            f"export interface {service_name}State {{\n"
            f"{TAB}messageIndex: number\n"
            f"{TAB}messages: {{[key: number]: string}}\n"
            f"\n"
            f"{TAB}errorIndex: number\n"
            f"{TAB}errors: {{[key: number]: string}}\n"
            f"}}\n"
            f"\n"
            f"const initialState: {service_name}State = {{\n"
            f"{TAB}messageIndex: 0,\n"
            f"{TAB}messages: {{}},\n"
            f"\n"
            f"{TAB}errorIndex: 0,\n"
            f"{TAB}errors: {{}},\n"
            f"}} as {service_name}State;\n"
            f"\n\n"
            f"export function {service_name}Reducer(state = initialState, action: {service_name}ActionType): {service_name}State {{\n"
            f"{TAB}switch (action.type) {{\n"
        )
        file.write(
            f'{TAB}{TAB}case "AddMessageType":\n'
            f"{TAB}{TAB}{TAB}const msg = state.messages;\n"
            f"{TAB}{TAB}{TAB}msg[state.messageIndex] = action.payload;\n"
            f"{TAB}{TAB}{TAB}return {{\n"
            f"{TAB}{TAB}{TAB}{TAB}...state,\n"
            f"{TAB}{TAB}{TAB}{TAB}messages: msg,\n"
            f"{TAB}{TAB}{TAB}{TAB}messageIndex: state.messageIndex + 1,\n"
            f"{TAB}{TAB}{TAB}}} as {service_name}State;\n"
            f"\n"
        )
        file.write(
            f'{TAB}{TAB}case "PopMessageType":\n'
            f"{TAB}{TAB}{TAB}const msgs = {{...state.messages}};\n"
            f"{TAB}{TAB}{TAB}delete msgs[action.payload];\n"
            f"{TAB}{TAB}{TAB}return {{\n"
            f"{TAB}{TAB}{TAB}{TAB}...state,\n"
            f"{TAB}{TAB}{TAB}{TAB}messages: msgs,\n"
            f"{TAB}{TAB}{TAB}}} as {service_name}State;\n"
            f"\n"
        )
        file.write(
            f'{TAB}{TAB}case "addErrorType":\n'
            f"{TAB}{TAB}{TAB}const err = state.errors;\n"
            f"{TAB}{TAB}{TAB}err[state.errorIndex] = action.payload;\n"
            f"{TAB}{TAB}{TAB}return {{\n"
            f"{TAB}{TAB}{TAB}{TAB}...state,\n"
            f"{TAB}{TAB}{TAB}{TAB}errors: err,\n"
            f"{TAB}{TAB}{TAB}{TAB}errorIndex: state.errorIndex + 1,\n"
            f"{TAB}{TAB}{TAB}}} as {service_name}State;\n"
            f"\n"
        )
        file.write(
            f'{TAB}{TAB}case "removeErrorType":\n'
            f"{TAB}{TAB}{TAB}const errs = {{...state.errors}};\n"
            f"{TAB}{TAB}{TAB}delete errs[action.payload];\n"
            f"{TAB}{TAB}{TAB}return {{\n"
            f"{TAB}{TAB}{TAB}{TAB}...state,\n"
            f"{TAB}{TAB}{TAB}{TAB}errors: errs,\n"
            f"{TAB}{TAB}{TAB}}} as {service_name}State;\n"
            f"\n"
        )
        file.write(
            f'{TAB}{TAB}default:\n'
            f"{TAB}{TAB}{TAB}return state;"
            f"\n"
        )
        file.write(
            f"{TAB}}}\n"
            f"}}\n\n"
        )

    # actions
    action_path = os.path.join(dir_name, f"{service_name}_actions.ts")
    with open(action_path, 'w') as file:
        file.write(
            f"{HEAD}\n\n"
            f'import {{ axiosInstance }} from "../client"\n'
            f'import * as msg from "../generated_messages"\n\n'
        )

        file.write(
            f'export const AddMessageType = "AddMessageType";\n'
            f"interface AddMessageType_Action {{\n"
            f"{TAB}type: typeof AddMessageType,\n"
            f"{TAB}payload: string,\n"
            f"}}\n"
            f"\n"
            f"export function addMessageToQueue(msg: string) {{\n"
            f"{TAB}return {{type: AddMessageType, payload: msg}}\n"
            f"}}\n\n"
        )
        file.write(
            f'export const PopMessageType = "PopMessageType";\n'
            f"interface PopMessageType_Action {{\n"
            f"{TAB}type: typeof PopMessageType,\n"
            f"{TAB}payload: number,\n"
            f"}}\n"
            f"\n"
            f"export function removeMessageFromQueue(index: number) {{\n"
            f"{TAB}return {{type: AddMessageType, payload: index}}\n"
            f"}}\n\n"
        )
        file.write(
            f'export const addErrorType = "addErrorType";\n'
            f"interface addErrorType_Action {{\n"
            f"{TAB}type: typeof addErrorType,\n"
            f"{TAB}payload: string,\n"
            f"}}\n"
            f"\n"
            f"export function addErrorToQueue(error: string) {{\n"
            f"{TAB}return {{type: addErrorType, payload: error}}\n"
            f"}}\n\n"
        )
        file.write(
            f'export const removeErrorType = "removeErrorType";\n'
            f"interface removeErrorType_Action {{\n"
            f"{TAB}type: typeof removeErrorType,\n"
            f"{TAB}payload: number,\n"
            f"}}\n"
            f"\n"
            f"export function removeErrorFromQueue(index: number) {{\n"
            f"{TAB}return {{type: removeErrorType, payload: index}}\n"
            f"}}\n\n"
        )

        file.write(
            f"export type notificationServiceActionType = (\n"
            f"{TAB}AddMessageType_Action |\n"
            f"{TAB}PopMessageType_Action |\n"
            f"{TAB}addErrorType_Action |\n"
            f"{TAB}removeErrorType_Action\n"
            f")\n"
            f"\n"
        )
