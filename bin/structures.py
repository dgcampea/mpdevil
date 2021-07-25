"""
data structures for MPD
"""

import collections
import logging
from gettext import gettext as _


class Song(collections.UserDict): # pylint: disable=too-many-ancestors
    """dict representing a MPD Song
    """
    def __setitem__(self, key, value):
        if isinstance(value, list):
            self.data[key] = ", ".join(value)
        else:
            self.data[key] = value

    def __missing__(self, key):
        if key == 'title':
            value = _("Unknown Title")
            self.data[key] = value  # cache this
        elif key == 'duration':
            logging.warning("Duration not found for track: %s", self['file'])
            value = 0.0
        elif key == 'track':
            value = "0"
        else:
            value = ""
        return value
