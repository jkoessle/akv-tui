import base64

from pytest_mock import MockerFixture

from akv_tui import helpers


def test_convert_der_to_pem():
    der_bytes = b"test-certificate-bytes"
    expected_base64 = base64.b64encode(der_bytes).decode("ascii")
    expected_pem = (
        "-----BEGIN CERTIFICATE-----\n"
        + "\n".join(
            [expected_base64[i : i + 64] for i in range(0, len(expected_base64), 64)],
        )
        + "\n-----END CERTIFICATE-----"
    )

    result = helpers.convert_der_to_pem(der_bytes)
    assert result == expected_pem


def test_get_authenticated_credential_default_success(mocker: MockerFixture):
    mock_cred = mocker.Mock()
    mock_sub_client = mocker.patch("akv_tui.helpers.SubscriptionClient")
    mock_sub_client.return_value.subscriptions.list.return_value = ["fake-sub"]

    mocker.patch("akv_tui.helpers.DefaultAzureCredential", return_value=mock_cred)

    cred = helpers.get_authenticated_credential()

    assert isinstance(cred, mocker.Mock)
    mock_sub_client.assert_called_once_with(mock_cred)


def test_get_authenticated_credential_fallback_to_interactive(mocker: MockerFixture):
    mock_cred = mocker.Mock()
    mock_sub_client = mocker.patch("akv_tui.helpers.SubscriptionClient")
    mock_sub_client.return_value.subscriptions.list.side_effect = Exception(
        "auth failure",
    )

    mocker.patch("akv_tui.helpers.DefaultAzureCredential", return_value=mock_cred)

    mock_browser_cred = mocker.Mock()
    mocker.patch(
        "akv_tui.helpers.InteractiveBrowserCredential",
        return_value=mock_browser_cred,
    )

    cred = helpers.get_authenticated_credential()

    assert cred == mock_browser_cred
