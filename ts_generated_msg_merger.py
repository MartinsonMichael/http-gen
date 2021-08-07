import argparse
import logging
import os

logger = logging.Logger(__name__)


def main(ts_path: str, generated_message_file_prefix: str = "generated_messages"):
    logger.log(35, "Merging ts messages files...")
    with open(os.path.join(ts_path, f"{generated_message_file_prefix}.ts"), 'w') as file:
        for file_name in os.listdir(ts_path):
            if not file_name.startswith(generated_message_file_prefix):
                continue
            if file_name == f"{generated_message_file_prefix}.ts":
                continue
            logger.log(35, f"Find `{file_name}` to merge")
            with open(os.path.join(ts_path, file_name), 'r') as msg_file:
                for line in msg_file.readlines():
                    file.write(line)

            os.remove(os.path.join(ts_path, file_name))
            logger.log(35, f"`{file_name}` merged and deleted")
    logger.log(35, f"ts message merging completed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ts-path', type=str)

    args = parser.parse_args()
    main(args.ts_path)
