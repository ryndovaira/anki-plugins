# Handles Configuration reading and the integration with Anki's config system
#
# This file is part of fill-the-blanks addon
# @author ricardo saturnino


class ConfigKey:
    FEEDBACK_ENABLED = 'feedback-enabled'
    IGNORE_CASE = 'feedback-ignore-case'
    IGNORE_ACCENTS = 'feedback-ignore-accents'
    ASIAN_CHARS = 'experimental-asian-chars'


DEFAULT_CONFIG = {
    ConfigKey.FEEDBACK_ENABLED: True,
    ConfigKey.IGNORE_CASE: True,
    ConfigKey.IGNORE_ACCENTS: False,
    ConfigKey.ASIAN_CHARS: False,
}


class ConfigService:
    """Responsible for reading and storing configurations."""

    @staticmethod
    def load_config(key):
        raise NotImplementedError()

    @classmethod
    def read(cls, key: str, expected_type: type):
        try:
            value = cls.load_config(key)
            if not isinstance(value, expected_type):
                value = None
        except Exception:
            value = None

        return value if value is not None else DEFAULT_CONFIG[key]
