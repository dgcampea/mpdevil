"""
mpd.MPDClient wrapper for mpdevil
"""

import collections
import logging
import locale
from gettext import gettext as _, ngettext
from typing import Union
import datetime
import mpd


class MPDClient(mpd.MPDClient):
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

    def currentsong(self, *args):
        """override MPDClient song representation
        """
        return Song(super().currentsong(*args))


class Song(collections.UserDict): # pylint: disable=too-many-ancestors
    """dict representing a MPD Song for mpdevil usage
    """
    def __setitem__(self, key, value):
        if isinstance(value, list):
            self.data[key] = ", ".join(value)
        elif key == 'duration':
            self.data[key] = float(value)
        elif key == 'disc':
            self.data[key] = int(value)
        else:
            self.data[key] = value

    def __missing__(self, key):
        # Some keys are cached for performance
        cache = False

        if key == 'title':
            cache = True
            value = _("Unknown Title")
        elif key == 'duration':
            logging.warning("Duration not found for track: %s", self['file'])
            value = 0.0
        elif key == 'track':
            value = "0"
        elif key == 'human_duration':
            cache = True
            if self.get('duration') is None:
                value = "––∶––"
            else:
                value = Song.seconds_to_display_time(self['duration'])
        elif key == 'human_format':
            cache = True
            value = Song.convert_audio_format(self['format'])
        elif key == 'human_last-modified':
            cache = True
            value = Song.format_last_modified(self['last-modified'])
        elif key == "disc":
            value = 1
        else:
            value = ""

        if cache:
            self.data[key] = value
        return value

    @staticmethod
    def seconds_to_display_time(seconds : Union[int, str, float]):
        """
        Convert seconds to [D day[s], ][H]H:MM]
        Similar to str(datetime.timedelta()) but is localized
        and anything after minutes is truncated
        """
        # discard fractional part
        delta=datetime.timedelta(seconds=int(float(seconds)))
        if delta.days > 0:
            days=ngettext("{days} day", "{days} days", delta.days).format(days=delta.days)
            time_string=f"{days}, {str(delta - datetime.timedelta(delta.days))}"
        else:
            time_string=str(delta).lstrip("0").lstrip(":")
        return time_string.replace(":", "∶")  # use 'ratio' as delimiter

    @staticmethod
    def convert_audio_format(audio_format : str) -> str:
        """
        Pretty-fy MPD audio_format data
        see: https://www.musicpd.org/doc/html/user.html#audio-output-format
        """
        # see: https://www.musicpd.org/doc/html/user.html#audio-output-format
        samplerate, bits, channels=audio_format.split(":")
        try:
            freq=locale.str(int(samplerate)/1000)
        except ValueError:
            freq=samplerate

        if bits == "f":
            bits="32fp"

        try:
            chan_qty=int(channels)
        except ValueError:
            chan_qty=0
        channels=ngettext("{channels} channel", "{channels} channels",
            chan_qty).format(channels=chan_qty)

        return f"{freq} kHz • {bits} bit • {channels}"

    @staticmethod
    def format_last_modified(date : str) -> str:
        """
        Pretty-fy MPD last-modified data
        """
        time = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")  # read MPD date format
        return time.strftime("%a %d %B %Y, %H∶%M UTC")
