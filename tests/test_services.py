import pytest
from pytest_mock import MockerFixture

from akv_tui.services import VaultService


@pytest.fixture
def vault_service(mocker: MockerFixture):
    mocker.patch(
        "akv_tui.services.helpers.get_authenticated_credential",
        return_value="fake-credential",
    )
    return VaultService()


def test_get_vaults(mocker: MockerFixture, vault_service: VaultService):
    mock_sub = mocker.Mock()
    mock_sub.subscription_id = "sub123"

    mock_vault = mocker.Mock()
    mock_vault.name = "vault1"

    sub_client_mock = mocker.patch("akv_tui.services.SubscriptionClient")
    kv_client_mock = mocker.patch("akv_tui.services.KeyVaultManagementClient")

    sub_client_mock.return_value.subscriptions.list.return_value = [mock_sub]
    kv_client_mock.return_value.vaults.list.return_value = [mock_vault]

    result = vault_service.get_vaults()

    assert result == {"vault1": "https://vault1.vault.azure.net/"}
    kv_client_mock.assert_called_once_with("fake-credential", "sub123")


@pytest.mark.parametrize(
    ("mode", "method_name"),
    [
        ("secrets", "list_properties_of_secrets"),
        ("keys", "list_properties_of_keys"),
        ("certificates", "list_properties_of_certificates"),
    ],
)
def test_get_items(
    mocker: MockerFixture,
    vault_service: VaultService,
    mode: str,
    method_name: str,
):
    vault_url = "https://test.vault.azure.net/"
    item_mock = mocker.Mock()
    item_mock.name = f"{mode}_name"

    client_class = _get_client_class_name(mode)
    client_mock = mocker.Mock()
    mocker.patch(f"akv_tui.services.{client_class}", return_value=client_mock)
    getattr(client_mock, method_name).return_value = [item_mock]

    items = vault_service.get_items(vault_url, mode)

    assert items == [f"{mode}_name"]


@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        ("secrets", "my-secret-value"),
        ("keys", "mocked-key-object"),
        ("certificates", "PEM_FORMAT"),
    ],
)
def test_get_value(
    mocker: MockerFixture,
    vault_service: VaultService,
    mode: str,
    expected: str,
):
    vault_url = "https://test.vault.azure.net/"
    name = "test-item"

    client_class = _get_client_class_name(mode)
    client_mock = mocker.Mock()
    mocker.patch(f"akv_tui.services.{client_class}", return_value=client_mock)

    if mode == "secrets":
        secret = mocker.Mock()
        secret.value = expected
        client_mock.get_secret.return_value = secret
        result = vault_service.get_value(vault_url, name, mode)
        assert result == expected

    elif mode == "keys":
        key = mocker.Mock()
        key.key = expected
        client_mock.get_key.return_value = key
        result = vault_service.get_value(vault_url, name, mode)
        assert expected in result

    elif mode == "certificates":
        cert = mocker.Mock()
        cert.cer = b"DER"
        client_mock.get_certificate.return_value = cert
        mocker.patch(
            "akv_tui.services.helpers.convert_der_to_pem",
            return_value=expected,
        )
        result = vault_service.get_value(vault_url, name, mode)
        assert result == expected


def test_get_items_invalid_mode(mocker: MockerFixture, vault_service: VaultService):
    mocker.patch("akv_tui.services.VaultService._get_client")
    with pytest.raises(ValueError, match="Unsupported mode: invalid"):
        vault_service.get_items("https://vault.vault.azure.net/", "invalid")


def test_get_value_invalid_mode(mocker: MockerFixture, vault_service: VaultService):
    mocker.patch("akv_tui.services.VaultService._get_client")
    with pytest.raises(ValueError, match="Unsupported mode: invalid"):
        vault_service.get_value("https://vault.vault.azure.net/", "name", "invalid")


def _get_client_class_name(mode: str) -> str:
    return {
        "secrets": "SecretClient",
        "keys": "KeyClient",
        "certificates": "CertificateClient",
    }[mode]
