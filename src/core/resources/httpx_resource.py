from httpx import AsyncClient, Limits, Timeout


def HttpxClientResource(
    timeout: int = 5,
    max_keepalive_connections: int = 10,
    max_connections: int = 100,
) -> AsyncClient:
    """
    Creates and returns a configured httpx.AsyncClient

    :param timeout: Total timeout in seconds for all operations.
    :param max_keepalive_connections: Maximum number of keep-alive connections.
    :param max_connections: Maximum number of simultaneous connections.

    :return: an AsyncClient instance with the given parameters.
    """
    limits = Limits(
        max_keepalive_connections=max_keepalive_connections,
        max_connections=max_connections,
    )
    timeout_config = Timeout(timeout, read=timeout, write=timeout)
    client = AsyncClient(timeout=timeout_config, limits=limits)

    return client
