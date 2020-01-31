""" Configuration settings for Cylleneus """

import os
import sys
from appdirs import user_data_dir
from .utils import DEBUG_HIGH, DEBUG_MEDIUM, DEBUG_LOW, DEBUG_OFF
from . import __path__

# Debugging settings
DEBUG = DEBUG_HIGH

# Package settings
ROOT_DIR = os.path.dirname(os.path.abspath(__path__[0]))

# Corpus settings
CORPUS_DIR = user_data_dir("corpus", "Cylleneus")
DEFAULT_CORPUS = 'lasla'

# Search settings
LINES_OF_CONTEXT = 2
CHARS_OF_CONTEXT = LINES_OF_CONTEXT * 70

# Miscellaneous settings
LONG_DATE_FORMAT = '%A, %B %d, %Y %I:%M%p'
SHORT_DATE_FORMAT = '%m/%d/%Y %H:%M'

# Platform
PLATFORM = sys.platform
