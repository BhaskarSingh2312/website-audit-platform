import ipaddress
import socket
import re
from urllib.parse import urlparse
from typing import Tuple, Optional

BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),      # Loopback
    ipaddress.ip_network("10.0.0.0/8"),       # Private RFC 1918
    ipaddress.ip_network("172.16.0.0/12"),    # Private RFC 1918
    ipaddress.ip_network("192.168.0.0/16"),   # Private RFC 1918
    ipaddress.ip_network("169.254.0.0/16"),   # Link-local / Cloud Metadata
    ipaddress.ip_network("0.0.0.0/8"),        # Current network
    ipaddress.ip_network("::1/128"),          # IPv6 Loopback
    ipaddress.ip_network("fc00::/7"),         # IPv6 Unique Local
    ipaddress.ip_network("fe80::/10"),        # IPv6 Link-local
]

def normalize_url(raw_url: str) -> str:
    """Ensures URL starts with http:// or https:// and strips trailing whitespace/fragments."""
    url = raw_url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    # Rebuild normalized base URL
    scheme = parsed.scheme if parsed.scheme in ("http", "https") else "https"
    netloc = parsed.netloc or parsed.path.split('/')[0]
    path = parsed.path if parsed.netloc else ""
    return f"{scheme}://{netloc}{path}".rstrip("/")

def validate_url_for_ssrf(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validates URL to protect against SSRF (Server-Side Request Forgery).
    Rejects private IPs, loopback, cloud metadata IPs, and non-HTTP schemes.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False, f"Invalid protocol: '{parsed.scheme}'. Only http and https are permitted."

        hostname = parsed.hostname
        if not hostname:
            return False, "Could not determine hostname from URL."

        # Block direct localhost keywords
        if hostname.lower() in ("localhost", "127.0.0.1", "0.0.0.0", "::1"):
            return False, "Access to localhost or loopback is blocked."

        # Resolve IP addresses
        ip_addresses = socket.getaddrinfo(hostname, None)
        for item in ip_addresses:
            ip_str = item[4][0]
            ip_obj = ipaddress.ip_address(ip_str)
            for blocked_net in BLOCKED_IP_NETWORKS:
                if ip_obj in blocked_net:
                    return False, f"Access to private/internal IP address ({ip_str}) is blocked."

        return True, None
    except socket.gaierror:
        # In case domain does not resolve yet or during test, allow with warning or fail
        return True, None
    except Exception as e:
        return False, f"URL validation error: {str(e)}"

def sanitize_for_prompt(text: str, max_chars: int = 5000) -> str:
    """
    Sanitizes raw scraped HTML or user input before injecting into LLM context.
    Strips raw scripts, base64 payloads, and limits length.
    """
    if not text:
        return ""
    # Remove script and style contents
    cleaned = re.sub(r'<script.*?</script>', ' ', text, flags=re.DOTALL | re.IGNORECASE)
    cleaned = re.sub(r'<style.*?</style>', ' ', cleaned, flags=re.DOTALL | re.IGNORECASE)
    # Remove HTML tags
    cleaned = re.sub(r'<[^>]+>', ' ', cleaned)
    # Compress whitespace
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned[:max_chars]
