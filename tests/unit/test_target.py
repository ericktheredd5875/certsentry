from dataclasses import FrozenInstanceError

import pytest

from certsentry.target import InvalidTargetError, Target


@pytest.mark.parametrize(
    ("host", "port", "expected_host"),
    [
        ("example.com", 443, "example.com"),
        ("ExAmPlE.CoM", 443, "example.com"),
        ("192.168.1.1", 443, "192.168.1.1"),
    ],
)
def test_valid_target(host: str, port: int, expected_host: str) -> None:
    target = Target(host, port)
    assert target.host == expected_host
    assert target.port == port


@pytest.mark.parametrize(
    ("host", "port", "expected_str"),
    [
        ("example.com", 443, "example.com:443"),
        ("example.com", 8443, "example.com:8443"),
        ("example.com", 1, "example.com:1"),
        ("example.com", 65535, "example.com:65535"),
    ],
)
def test_str_includes_host_and_port(host: str, port: int, expected_str: str) -> None:
    target = Target(host, port)
    assert str(target) == expected_str


@pytest.mark.parametrize(
    ("host", "reason_fragment"),
    [
        ("", "empty"),
        ("example.com ", "whitespace"),
        ("example.com\n", "whitespace"),
        ("example.com\t", "whitespace"),
        ("http://example.com", "scheme"),
        ("example.com/path", "path"),
        ("example.com?query", "query"),
        ("example.com#fragment", "fragment"),
        ("example.com:8080", "contains a port"),
        ("user@example.com", "userinfo"),
        (".example.com", "starts"),
        ("example.com.", "ends"),
        ("stuff..example.com", "consecutive dots"),
    ],
)
def test_invalid_target(host: str, reason_fragment: str) -> None:
    with pytest.raises(InvalidTargetError, match=reason_fragment):
        Target(host)


@pytest.mark.parametrize(
    ("host", "port", "reason_fragment"),
    [
        ("example.com", 70000, "out of range"),
        ("example.com", "not-a-port", "integer"),
        ("example.com", -1, "out of range"),
        ("example.com", 0, "out of range"),
        ("example.com", 65536, "out of range"),
        ("example.com", True, "not an integer"),
    ],
)
def test_invalid_port(host: str, port: int, reason_fragment: str) -> None:
    with pytest.raises(InvalidTargetError, match=reason_fragment):
        Target(host, port)


def test_target_host_is_normalized_to_lowercase() -> None:
    target = Target("ExAmPlE.CoM", 443)
    assert target.host == "example.com"


def test_target_host_not_assigned_directly() -> None:
    target = Target("example.com", 443)
    with pytest.raises(FrozenInstanceError):
        target.host = "newhost.com"  # type: ignore[misc]


def test_target_port_not_assigned_directly() -> None:
    target = Target("example.com", 443)
    with pytest.raises(FrozenInstanceError):
        target.port = 8443  # type: ignore[misc]


def test_targets_equal_after_normalization() -> None:
    target1 = Target("example.com", 443)
    target2 = Target("Example.com", 443)
    assert target1 == target2
    assert hash(target1) == hash(target2)
    assert len({target1, target2}) == 1  # They should be considered the same in a set


def test_error_exposes_text_and_reason() -> None:
    with pytest.raises(InvalidTargetError) as exc_info:
        Target("invalid host", 443)
    assert "whitespace" in exc_info.value.reason
    assert exc_info.value.text == "invalid host"


def test_target_default_port() -> None:
    target = Target("example.com")
    assert target.port == 443
