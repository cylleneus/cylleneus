""" Configuration settings for Cylleneus """

import os
import sys

# Version settings
__version__ = "0.0.8"

# Platform
PLATFORM = sys.platform

# Debugging settings
DEBUG = False

# Package settings
ROOT_DIR = os.path.dirname(os.path.abspath(__path__[0]))

# Corpus settings
DEFAULT_CORPUS = 'lasla'

# Search settings
LINES_OF_CONTEXT = 2
CHARS_OF_CONTEXT = LINES_OF_CONTEXT * 70

# Miscellaneous settings
LONG_DATE_FORMAT = '%A, %B %d, %Y %I:%M%p'
SHORT_DATE_FORMAT = '%m/%d/%Y %H:%M'
