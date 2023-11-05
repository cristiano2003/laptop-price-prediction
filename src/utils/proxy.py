import requests


def check_proxy(proxy: tuple, timeout: int = 10) -> bool:
    """
        Just able to check http proxy with authentication
    Args:
        proxy (tuple): (host, port, username, password)
        timeout (int): timeout

    Returns:
        bool: True if the proxy is working, otherwise False
    """

    if len(proxy) != 4:
        return False

    host, port, username, password = proxy

    proxy_config = {
        'https': f'http://{username}:{password}@{host}:{port}',
        'http': f'http://{username}:{password}@{host}:{port}',
    }

    try:
        response = requests.get('https://ipinfo.io/ip', proxies=proxy_config, timeout=timeout)
    except Exception as e:
        return False
    else:
        if response.text == host:
            return True
        else:
            return False
