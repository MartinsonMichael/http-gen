import logging
import os

from parser import ParseResult
from py_common.py_utils import TAB

logger = logging.Logger(__name__)


def nginx_gen(parse_result: ParseResult, nginx_path: str) -> None:
    logger.log(35, "NGINX generation...")

    service_name = parse_result.meta.get('micro_service_name', 'common').lower()
    file_path = os.path.join(nginx_path, f"{service_name}_nginx.conf.part")

    with open(file_path, 'w') as file:
        for service in parse_result.services:
            for method in service.methods:
                host = parse_result.meta.get('container_name_prod')
                port = parse_result.meta['service_port']
                file.write(
                    f"{TAB}location /api/{method.name} {{\n"
                    f"{TAB}{TAB}proxy_pass http://{host}:{port};\n"
                    f"\n"
                    f"{TAB}{TAB}proxy_set_header   Host              $http_host;\n"
                    f"{TAB}{TAB}proxy_set_header   X-Real-IP         $remote_addr;\n"
                    f"{TAB}{TAB}proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;\n"
                    f"\n"
                    f"{TAB}{TAB}add_header Access-Control-Allow-Origin *;\n"
                    f"{TAB}{TAB}add_header Access-Control-Allow-Headers *;\n"
                    f"{TAB}}}\n"
                    f"\n"
                )

    logger.log(35, "NGINX generation DONE")
