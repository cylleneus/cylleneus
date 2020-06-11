""" Configuration settings for Cylleneus """

import os
import sys
from appdirs import user_data_dir
from .utils import Debug
from . import __path__

# Debugging settings
DEBUG_LEVEL = Debug.OFF

# Package settings
ROOT_DIR = os.path.dirname(os.path.abspath(__path__[0]))

# Corpus settings
CORPUS_DIR = user_data_dir("corpus", "Cylleneus")

# Search settings
LINES_OF_CONTEXT = 2
CHARS_OF_CONTEXT = LINES_OF_CONTEXT * 70

# Miscellaneous settings
LONG_DATE_FORMAT = "%A, %B %d, %Y %I:%M%p"
SHORT_DATE_FORMAT = "%m/%d/%Y %H:%M"
DURATION_FORMAT = "%H:%M:%S"

# Platform
PLATFORM = sys.platform
