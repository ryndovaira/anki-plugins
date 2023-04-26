# -*- coding: utf-8 -*-
# Handles Configuration reading, saving and the integration with the config UI
# Contains model, service and view controller for Config
#
# This files is part of fill-the-blanks addon
# @author ricardo saturnino
# -------------------------------------------------------

# from .core import Feedback

import os

currentLocation = os.path.dirname(os.path.realpath(__file__))


# ---------------------------------- Model ------------------------------

class ConfigKey:

    FEEDBACK_ENABLED = 'feedback-enabled'
    IGNORE_CASE = 'feedback-ignore-case'
    IGNORE_ACCENTS = 'feedback-ignore-accents'
    LEN_MULTIPLIER = 'input-len-times'
    ASIAN_CHARS = 'experimental-asian-chars'
    ENABLE_NEW_FILTER = 'enable-new-filter'
    OVERRIDE_TYPE_CLOZE = 'override-type-cloze'

# ------------------------------ Service class --------------------------


DEFAULT_CONFIG = {
    ConfigKey.FEEDBACK_ENABLED: True,
    ConfigKey.IGNORE_CASE: False,
    ConfigKey.IGNORE_ACCENTS: False,
    ConfigKey.LEN_MULTIPLIER: 62,
    ConfigKey.ASIAN_CHARS: False,
    ConfigKey.ENABLE_NEW_FILTER: False,
    ConfigKey.OVERRIDE_TYPE_CLOZE: True
}

class ConfigService:
    """
        Responsible for reading and storing configurations
    """
    
    @staticmethod
    def load_config(key):
        raise NotImplementedError()

    @classmethod
    def read(clz, key: str, expectedType):
        try:
            value = clz.load_config(key)
            if not (type(value) == expectedType):
                raise TypeError()
        except Exception as e:
            # print(e)
            value = None

        return value if (value is not None) else DEFAULT_CONFIG[key]
