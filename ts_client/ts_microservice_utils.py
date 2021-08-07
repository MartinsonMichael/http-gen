from typing import Optional, Tuple


def get_file_names(micro_service_name: Optional[str] = None) -> Tuple[str, str, str]:
    axiosInstance = "axiosInstance"
    messages_file_name = "generated_messages"
    client_file_name = "client"

    if micro_service_name is not None:
        axiosInstance = f"axiosInstance{micro_service_name}"
        client_file_name = f"client_{micro_service_name.lower()}"
        # this should be used only in generate_message file itself
        # messages_file_name = f"generated_messages_{micro_service_name.lower()}"

    return axiosInstance, messages_file_name, client_file_name
