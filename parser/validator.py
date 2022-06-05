from parser import ParseResult
from parser.utils import (
    is_base_type,
)


def post_process_parsed_results(parsed_results: ParseResult) -> None:
    for service in parsed_results.services:
        if 'Session-auth' in service.changers:
            for method in service.methods:
                method.changers.append('Session-auth')

        if 'FLASK-do-not-generate' in service.changers:
            for method in service.methods:
                method.changers.append('FLASK-do-not-generate')

        if 'Admin-auth' in service.changers:
            for method in service.methods:
                method.changers.append('Admin-auth')


def validate_parsed_data(parsed_results: ParseResult) -> None:
    msg_names = [msg.name for msg in parsed_results.messages]
    for msg in parsed_results.messages:
        for atr in msg.attributes:
            if atr.atr_type in msg_names:
                continue
            elif is_base_type(atr.atr_type):
                continue
            elif atr.is_map and is_base_type(atr.map_key_type) and (is_base_type(atr.map_value_type) or atr.map_value_type in msg_names):
                continue
            else:
                raise ValueError(f"message {msg.name} contain attribute with unknown type {atr.atr_type}")

    for service in parsed_results.services:
        for method in service.methods:
            if method.input_type == "Null" or method.input_type in msg_names:
               pass
            else:
                raise ValueError(
                    f"service {service.name} contain method {method.name} with unknown input type {method.input_type}"
                )
            if method.output_type == "Null" or method.output_type in msg_names:
                pass
            else:
                raise ValueError(
                    f"service {service.name} contain method {method.name} with unknown output type {method.input_type}"
                )

            # if 'InputFiles' in method.changers and method.input_type != "Null":
            #     raise ValueError("you can use only one of: 'Input message', 'InputFile'")

            if 'OutputFile' in method.changers and method.output_type != "Null":
                raise ValueError("you can use only one of: 'Output message', 'OutputFile'")
