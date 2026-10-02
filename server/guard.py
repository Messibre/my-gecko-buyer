import ipaddress
import socket
from urllib.parse import urlparse


def is_public_url(url: str) -> bool:
    """Returns True if the URL uses https and resolves to a safe public IP."""
    try:
        parsed = urlparse(url)
    except Exception:
        return False

    # 1. Accept only https:// URLs
    if parsed.scheme != "https":
        return False
        
    hostname = parsed.hostname
    if not hostname:
        return False
        
    # DECISION ON DNS FAILURE: 
    # If a hostname fails to resolve, we fail-closed and return False. 
    # A failure might be an attempt to use an unresolvable internal/local 
    # hostname to bypass the check, or it's simply a broken link. It's safer to refuse.
    try:
        addr_info = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return False
        
    # 3. Reject loopback, private, link-local, reserved, and multicast
    for res in addr_info:
        ip_str = res[4][0]
        try:
            ip = ipaddress.ip_address(ip_str)
        except ValueError:
            continue
            
        if (ip.is_private or ip.is_loopback or ip.is_link_local or 
            ip.is_reserved or ip.is_multicast):
            return False
            
    return True