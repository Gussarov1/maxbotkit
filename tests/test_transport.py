from __future__ import annotations

from maxbotkit.client.transport import UrllibTransport


def test_unverified_ssl_context_can_be_built() -> None:
    transport = UrllibTransport(verify_ssl=False)

    context = transport._build_ssl_context()

    assert context.check_hostname is False
    assert context.verify_mode == 0


def test_custom_ca_file_is_stored() -> None:
    transport = UrllibTransport(ca_file="/tmp/company-ca.pem")

    assert transport.ca_file == "/tmp/company-ca.pem"
