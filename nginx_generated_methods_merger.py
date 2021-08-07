import argparse
import itertools
import logging
import os

logger = logging.Logger(__name__)


def main(nginx_path: str):
    logger.log(35, "Merging NGINX config.part files...")

    lines_pre = []
    lines = []
    lines_post = []

    state = 0
    with open(os.path.join(nginx_path, "nginx.conf"), 'r') as file:
        for line in file.readlines():

            if state == 0:
                lines_pre.append(line)
            elif state == 1:
                lines.append(line)
            elif state == 2:
                lines_post.append(line)
            else:
                raise ValueError(f"strange state: {state}")

            if 'auto line' in line:
                state += 1

    lines_post = [lines[-1]] + lines_post

    lines = []

    for file_name in os.listdir(nginx_path):
        if not file_name.endswith("nginx.conf.part"):
            continue
        logger.log(35, f"Find `{file_name}` to merge")
        with open(os.path.join(nginx_path, file_name), 'r') as msg_file:
            lines.extend(msg_file.readlines())

        os.remove(os.path.join(nginx_path, file_name))
        logger.log(35, f"`{file_name}` merged and deleted")

    with open(os.path.join(nginx_path, "nginx.conf"), 'w') as file:
        for line in itertools.chain(lines_pre, lines, lines_post):
            file.write(line)

    logger.log(35, f"MGING message merging completed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--nginx-path', type=str)

    args = parser.parse_args()
    main(args.nginx_path)
