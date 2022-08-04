from py_common.py_utils import (
    ParseResult,
    HEAD,
    TAB,
)


def generate_urls(parse_result: ParseResult, urls_path: str) -> None:
    with open(urls_path, "w") as file:
        file.write(
            f"{HEAD}"
            f"\n\n"
            f"from django.urls import path\n"
            f"\n"
        )
        for service in parse_result.services:
            file.write(f"from .{service.name}_impl import {service.name}\n")

        file.write("\n\n")

        for service in parse_result.services:
            file.write(f"service_{service.name} = {service.name}()\n")

        file.write("\n")
        file.write(f"urlpatterns = [\n")

        for service in parse_result.services:
            file.write(f"{TAB}# urls for {service.name}\n")
            for method in service.methods:
                file.write(f"{TAB}path('{method.name}', service_{service.name}.call__{method.name}),\n")
            file.write(f"\n")

        file.write(f"]\n")
