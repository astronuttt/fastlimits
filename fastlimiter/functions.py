from fastapi import Request


def get_remote_address(request: Request) -> str:
    """Utility function to use remote address as a limit key"""
    if not request.client or not request.client.host:
        return "127.0.0.1"
    return request.client.host


def get_path(request: Request) -> str:
    """Utility function to use path as a limit key"""
    return request.url.path
