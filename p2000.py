"""
Support for fetching emergency services events near your location.
Dutch P2000 based.

"""
from logging import getLogger
import datetime
from geopy.distance import vincenty 
import feedparser

import voluptuous as vol

from homeassistant.helpers.event import track_utc_time_change
import homeassistant.util as util
import homeassistant.helpers.config_validation as cv

_LOGGER = getLogger(__name__)
_RESOURCE = 'http://feeds.livep2000.nl?r={}&d={}'

CONF_REGIOS = 'regios'
CONF_DISCIPLINES = 'disciplines'
CONF_INTERVAL = 'interval'
CONF_DISTANCE = 'distance'

DEFAULT_DISCIPLINES = '1,2,3,4'
DEFAULT_INTERVAL = 10
DEFAULT_DISTANCE = 5000

ATTR_TEXT = 'text'
ATTR_URL = 'url'

DOMAIN = 'p2000'
EVENT_P2000 = 'p2000'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_REGIOS): cv.string,
        vol.Optional(CONF_DISCIPLINES, default=DEFAULT_DISCIPLINES): cv.string,
        vol.Optional(CONF_INTERVAL, default=DEFAULT_INTERVAL): cv.positive_int,
        vol.Optional(CONF_DISTANCE, default=DEFAULT_DISTANCE): cv.positive_int,
    }),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up the P2000 component."""

    regios = config.get(DOMAIN)[CONF_REGIOS]
    disciplines = config.get(DOMAIN)[CONF_DISCIPLINES]
    distance = config.get(DOMAIN)[CONF_DISTANCE]
    interval = config.get(DOMAIN)[CONF_INTERVAL]

    if None in (hass.config.latitude, hass.config.longitude):
        _LOGGER.error("Lat and/or longitude not set in Home Assistant config")
        return False

    latitude = util.convert(hass.config.latitude, float)
    longitude = util.convert(hass.config.longitude, float)

    url = _RESOURCE.format(regios, disciplines)
    P2000Manager(url, distance, latitude, longitude, interval, hass)

    return True


class P2000Manager(object):  # pylint: disable=too-few-public-methods
    """Get data from P2000 feed."""

    # pylint: disable=too-many-instance-attributes
    # pylint: disable=too-many-arguments
    # Seven is reasonable in this case.
    def __init__(self, url, distance, latitude, longitude, interval, hass):
        """Initialize the data object."""
        self._url = url
        self._maxdist = distance
        self._feed = None
        self._lastmsg_time = None
        self._restart = True
        self._hass = hass
        self._lat = latitude
        self._lon = longitude

        track_utc_time_change(hass, lambda now: self._update(),
                              second=range(1, 59, interval))

    @staticmethod
    def _convert_time(time):
        return datetime.datetime.strptime(time.split(",")[1][:-6],
                                          " %d %b %Y %H:%M:%S")

    def _update(self):
        """Update the feed and publish new entries to the event bus."""

        _LOGGER.debug('Fetching data from feed "%s"', self._url)
        self._feed = feedparser.parse(self._url,
                                      etag=None if not self._feed
                                      else self._feed.get('etag'),
                                      modified=None if not self._feed
                                      else self._feed.get('modified'))

        if not self._feed:
            _LOGGER.debug('Error fetching feed data from "%s"', self._url)
        else:
            if self._feed.bozo != 0:
                _LOGGER.debug('Error parsing feed "%s"', self._url)
            # Using etag and modified, if there's no new data available,
            # the entries list will be empty
            elif len(self._feed.entries) > 0:
                _LOGGER.debug('%s entries available in feed "%s"',
                              len(self._feed.entries),
                              self._url)
                self._publish_new_entries()
            else:
                _LOGGER.debug('No new entries found in feed "%s"', self._url)

        _LOGGER.debug('Fetch from feed "%s" completed.', self._url)

    def _publish_new_entries(self):
        """Parse XML and publish entries to the event bus."""

        if self._restart:
            pubdate = self._feed.entries[0]['published']
            self._lastmsg_time = self._convert_time(pubdate)
            self._restart = False
            _LOGGER.info('Restarted, last datestamp %s.', self._lastmsg_time)
            return

        for item in reversed(self._feed.entries):
            msgtext = ''
            lat_event = 0.0
            lon_event = 0.0
            dist = 0

            if 'published' in item:
                pubdate = item.published
                lastmsg_time = self._convert_time(pubdate)

            if lastmsg_time < self._lastmsg_time:
                _LOGGER.debug('Message is older %s than last sent %s'
                              ', skipping.', lastmsg_time, self._lastmsg_time)
                continue

            self._lastmsg_time = lastmsg_time

            if 'geo_lat' in item:
                lat_event = float(item.geo_lat)
            else:
                continue

            if 'geo_long' in item:
                lon_event = float(item.geo_long)
            else:
                continue

            if lat_event and lon_event:
                p1 = (self._lat, self._lon)
                p2 = (lat_event, lon_event)
                dist = vincenty(p1, p2).meters

            msgtext = item.title.replace("~", "")+'\n'+pubdate+'\n'
            _LOGGER.debug(msgtext)
            _LOGGER.debug('Calculated distance is %d meters, max. range is %d meters', dist, self._maxdist)

            if dist > self._maxdist:
                msgtext = ''
                continue

        if msgtext != "":
            self._hass.bus.fire(EVENT_P2000, {ATTR_TEXT: msgtext})

