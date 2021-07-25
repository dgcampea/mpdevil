"""
mpd.MPDClient wrapper for mpdevil
"""

import collections
import logging
from gettext import gettext as _
import mpd


class MPDClient(mpd.MPDClient): # pylint: disable=too-few-public-methods
    """mpdevil wrapper for MPDClient
    """

    def search(self, *args):
        """override MPDClient song representation
        """
        x = super().search(*args)
        if isinstance(x, list):
            return [Song(s) for s in x]
        else:
            return Song(x)


class Song(collections.UserDict): # pylint: disable=too-many-ancestors
    """dict representing a MPD Song for mpdevil usage
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
