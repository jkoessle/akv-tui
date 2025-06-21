import base64
import textwrap
from logging import getLogger

from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.mgmt.resource import SubscriptionClient

logger = getLogger()


def get_authenticated_credential() -> (
    DefaultAzureCredential | InteractiveBrowserCredential
):
    """Authenticates against Azure and return credentials.

    We first try to use DefaultAzureCredential and fall back to
    InteractiveBrowserCredential.

    Returns:
        DefaultAzureCredential | InteractiveBrowserCredential: Azure credential
    """
    try:
        cred = DefaultAzureCredential(exclude_interactive_browser_credential=True)
        list(SubscriptionClient(cred).subscriptions.list())
    except Exception:  # noqa: BLE001
        logger.debug(
            "Default login failed. Opening browser for interactive login...",
        )
        return InteractiveBrowserCredential()
    return cred


def convert_der_to_pem(der_bytes: bytes) -> str:
    """Converts bytes to pem string.

    Args:
        der_bytes (bytes): bytes encoded certificate

    Returns:
        str: PEM certificate
    """
    base64_cert = base64.b64encode(der_bytes).decode("ascii")
    return (
        "-----BEGIN CERTIFICATE-----\n"
        + "\n".join(textwrap.wrap(base64_cert, 64))
        + "\n-----END CERTIFICATE-----"
    )
