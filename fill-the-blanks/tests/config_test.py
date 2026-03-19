import pytest

from src.config import ConfigService, ConfigKey, DEFAULT_CONFIG


class TestConfigKey:

    def test_all_keys_present_in_defaults(self):
        for attr in dir(ConfigKey):
            if attr.isupper():
                key = getattr(ConfigKey, attr)
                assert key in DEFAULT_CONFIG, f"ConfigKey.{attr} missing from DEFAULT_CONFIG"

    def test_default_values_types(self):
        for key, value in DEFAULT_CONFIG.items():
            assert isinstance(value, bool), f"DEFAULT_CONFIG[{key}] should be bool"


class TestConfigServiceRead:

    def setup_method(self):
        self._orig = ConfigService.load_config

    def teardown_method(self):
        ConfigService.load_config = self._orig

    def test_read_returns_value_from_loader(self):
        ConfigService.load_config = lambda key: True
        assert ConfigService.read(ConfigKey.IGNORE_CASE, bool) is True

    def test_read_returns_default_on_wrong_type(self):
        ConfigService.load_config = lambda key: "not a bool"
        result = ConfigService.read(ConfigKey.IGNORE_CASE, bool)
        assert result == DEFAULT_CONFIG[ConfigKey.IGNORE_CASE]

    def test_read_returns_default_on_exception(self):
        ConfigService.load_config = lambda key: (_ for _ in ()).throw(RuntimeError("fail"))
        result = ConfigService.read(ConfigKey.FEEDBACK_ENABLED, bool)
        assert result == DEFAULT_CONFIG[ConfigKey.FEEDBACK_ENABLED]

    def test_read_returns_default_on_none(self):
        ConfigService.load_config = lambda key: None
        result = ConfigService.read(ConfigKey.IGNORE_CASE, bool)
        assert result == DEFAULT_CONFIG[ConfigKey.IGNORE_CASE]

    def test_read_each_default(self):
        """Verify every key returns its default when loader is not configured."""
        for key, expected in DEFAULT_CONFIG.items():
            result = ConfigService.read(key, bool)
            assert result == expected, f"Default for {key} should be {expected}"
