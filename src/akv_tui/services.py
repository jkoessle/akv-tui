from azure.keyvault.certificates import CertificateClient
from azure.keyvault.keys import KeyClient
from azure.keyvault.secrets import SecretClient
from azure.mgmt.keyvault import KeyVaultManagementClient
from azure.mgmt.resource import SubscriptionClient

from akv_tui import helpers


class VaultService:
    """Vault service class."""

    def __init__(self) -> None:
        """Initializes vault service."""
        self.credential = helpers.get_authenticated_credential()
        self._clients = {}

    def get_vaults(self) -> dict[str, str]:
        """Get available key vaults for subscription.

        Returns:
            dict[str, str]: Dict containing vault name and url
        """
        sub_client = SubscriptionClient(self.credential)
        vaults = {}
        for sub in sub_client.subscriptions.list():
            kv_client = KeyVaultManagementClient(self.credential, sub.subscription_id)
            for vault in kv_client.vaults.list():
                name = vault.name
                vaults[name] = f"https://{name}.vault.azure.net/"
        return vaults

    def get_items(self, vault_url: str, mode: str) -> list[str]:
        """Get available items for respective mode.

        If client is of type SecretClient returns available secret names.
        If client is of type KeyClient returns available key names.
        If client is of type CertificateClient returns available certificate names.

        Args:
            vault_url (str): URL for vault
            mode (str): Client mode

        Raises:
            ValueError: If mode is not in {"secrets", "keys", "certificates"}

        Returns:
            list[str]: List of available item names
        """
        client = self._get_client(vault_url, mode)
        if mode == "secrets":
            return [s.name for s in client.list_properties_of_secrets()]
        if mode == "keys":
            return [k.name for k in client.list_properties_of_keys()]
        if mode == "certificates":
            return [c.name for c in client.list_properties_of_certificates()]
        raise ValueError(f"Unsupported mode: {mode}")  # noqa: EM102, TRY003

    def get_value(self, vault_url: str, name: str, mode: str) -> str:
        """Get value for respective mode and name.

        Args:
            vault_url (str): URL for vault
            name (str): Secret name
            mode (str): Client mode

        Raises:
            ValueError: If mode is not in {"secrets", "keys", "certificates"}

        Returns:
            str: Value for secret name
        """
        client = self._get_client(vault_url, mode)
        if mode == "secrets":
            return client.get_secret(name).value
        if mode == "keys":
            # TODO(jkoessle): test what happens here  # noqa: FIX002, TD003
            return str(client.get_key(name).key)
        if mode == "certificates":
            return helpers.convert_der_to_pem(client.get_certificate(name).cer)

        raise ValueError(f"Unsupported mode: {mode}")  # noqa: EM102, TRY003

    def _get_client(
        self,
        vault_url: str,
        mode: str,
    ) -> SecretClient | KeyClient | CertificateClient:
        key = (vault_url, mode)
        if key not in self._clients:
            if mode == "secrets":
                self._clients[key] = SecretClient(
                    vault_url=vault_url,
                    credential=self.credential,
                )
            elif mode == "keys":
                self._clients[key] = KeyClient(
                    vault_url=vault_url,
                    credential=self.credential,
                )
            elif mode == "certificates":
                self._clients[key] = CertificateClient(
                    vault_url=vault_url,
                    credential=self.credential,
                )
        return self._clients[key]
