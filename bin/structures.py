"""
mpd.MPDClient wrapper for mpdevil
"""

import collections
import logging
from gettext import gettext as _, ngettext
from typing import Union
import datetime
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
        if key == 'duration':
            self.data[key] = float(value)
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
        elif key == 'human_duration':
            if self.get('duration') is None:
                value = "––∶––"
            else:
                value = Song.seconds_to_display_time(self['duration'])
            self.data[key] = value  # cache this
        else:
            value = ""

        return value

    @staticmethod
    def seconds_to_display_time(seconds : Union[int, str, float]):
        """
        Convert seconds to [D day[s], ][H]H:MM]
        Similar to str(datetime.timedelta()) but is localized
        and anything after minutes is truncated
        """
		# discard fractional part
        delta=datetime.timedelta(seconds=int(seconds))
        if delta.days > 0:
            days=ngettext("{days} day", "{days} days", delta.days).format(days=delta.days)
            time_string=f"{days}, {str(delta - datetime.timedelta(delta.days))}"
        else:
            time_string=str(delta).lstrip("0").lstrip(":")
        return time_string.replace(":", "∶")  # use 'ratio' as delimiter
