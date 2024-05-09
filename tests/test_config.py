from pathlib import Path
from typing import Any

import pytest

from gafm.config import Config, load_config

ENV_FILE = Path(__file__).parent / "test.env"


def test_defaults():
    config = Config()

    # Test one or two defaults, but this test should raise an exception on
    # failure.
    assert config.hot_reload is False
    assert config.port == 8080
    assert config.ssl_certfile is None
    assert config.ssl_keyfile is None


def test_out_of_bounds_cache_size():
    with pytest.raises(ValueError):
        Config(max_cache_size=-1)


@pytest.mark.parametrize("min_subdirs, max_subdirs", [[0, 0], [-1, -1], [5, 4097], [4097, 4098]])
def test_out_of_bounds_subdirs(min_subdirs, max_subdirs):
    with pytest.raises(ValueError):
        Config(min_subdirs=min_subdirs, max_subdirs=max_subdirs)


def test_inverted_min_max_subdirs():
    with pytest.raises(ValueError):
        Config(min_subdirs=10, max_subdirs=5)


@pytest.mark.parametrize("cert_file, key_file", [[None, Path("key.pem")], [Path("cert.pem"), None]])
def test_mismatched_cert_and_key_file(cert_file: Path | None, key_file: Path | None):
    with pytest.raises(ValueError):
        Config(ssl_certfile=cert_file, ssl_keyfile=key_file)


def test_load_environment_variables(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("GAFM_PORT", "42")

    config = Config()

    assert config.port == 42


def test_env_file_load():
    config = load_config(ENV_FILE)

    assert config.port == 1984
    assert config.redis.port == 1234


def test_environment_overloads_envfile(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("GAFM_PORT", "99")
    config = load_config(ENV_FILE)

    assert config.port == 99


@pytest.mark.parametrize(
    "environment_value, expected_value",
    [
        ("true", True),
        ("True", True),
        ("TRUE", True),
        ("tRuE", True),
        ("t", True),
        ("T", True),
        ("1", True),
        (1, True),
        ("false", False),
        ("False", False),
        ("FALSE", False),
        ("fAlSe", False),
        ("f", False),
        ("F", False),
        ("0", False),
        (0, False),
    ],
)
def test_environment_variable_interprets_booleans(
    monkeypatch: pytest.MonkeyPatch, environment_value: Any, expected_value: bool
):
    monkeypatch.setenv("GAFM_HOT_RELOAD", environment_value)

    config = Config()

    assert config.hot_reload is expected_value


def test_redis_port(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("GAFM_REDIS_PORT", "1234")

    config = Config()

    assert config.redis.port == 1234
