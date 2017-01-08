"""
Support for fetching emergency services events near your location (Dutch P2000 based).

"""
import feedparser
import gpxpy.geo
import datetime
from logging import getLogger

import voluptuous as vol

from homeassistant.const import EVENT_HOMEASSISTANT_START
from homeassistant.helpers.event import track_utc_time_change
import homeassistant.util as util
import homeassistant.helpers.config_validation as cv

_LOGGER = getLogger(__name__)
_RESOURCE = 'http://feeds.livep2000.nl?r={}&d={}'

CONF_REGIOS = 'regios'
CONF_DISCIPLINES = 'disciplines'
CONF_INTERVAL = 'interval'
CONF_MESSAGES = 'messages'
CONF_DISTANCE = 'distance'

DEFAULT_DISCIPLINES = '1,2,3,4'
DEFAULT_INTERVAL = 1
DEFAULT_MESSAGES = 5
DEFAULT_DISTANCE = 5000

ATTR_TEXT = 'text'

DOMAIN = 'p2000'
EVENT_P2000 = 'p2000'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_REGIOS): cv.string,
        vol.Optional(CONF_DISCIPLINES, default=DEFAULT_DISCIPLINES): cv.string,
        vol.Optional(CONF_INTERVAL, default=DEFAULT_INTERVAL): cv.positive_int,
        vol.Optional(CONF_MESSAGES, default=DEFAULT_MESSAGES): cv.positive_int,
        vol.Optional(CONF_DISTANCE, default=DEFAULT_DISTANCE): cv.positive_int,
    }),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up the P2000 component."""

    regios = config.get(DOMAIN)[CONF_REGIOS]
    disciplines = config.get(DOMAIN)[CONF_DISCIPLINES]
    messages = config.get(DOMAIN)[CONF_MESSAGES]
    distance = config.get(DOMAIN)[CONF_DISTANCE]
    interval = config.get(DOMAIN)[CONF_INTERVAL]

    if None in (hass.config.latitude, hass.config.longitude):
        _LOGGER.error("Latitude or longitude not set in Home Assistant config")
        return False

    latitude = util.convert(hass.config.latitude, float)
    longitude = util.convert(hass.config.longitude, float)

    url = _RESOURCE.format(regios, disciplines)
    feeds = P2000Manager(url, messages, distance, latitude, longitude, interval, hass)

    return True


class P2000Manager(object):
    """Get data from P2000 feed."""

    def __init__(self, url, messages, distance, latitude, longitude, interval, hass):
        """Initialize the data object."""
        self._url = url
        self._maxmsgs = messages
        self._maxdist = distance

        self._feed = None
        self._msg = None
        self._msg_prev = None
        self._hass = hass

        self._lat = latitude
        self._lon = longitude

        track_utc_time_change(hass, lambda now: self._update(),
                             minute=range(1, 59, interval), second=0)


    def _log_no_entries(self):
        """Send no entries log at debug level."""
        _LOGGER.debug('No new entries found in feed "%s"', self._url)


    def _update(self):
        """Update the feed and publish new entries to the event bus."""
        _LOGGER.info('Fetching new data from feed "%s"', self._url)
        self._feed = feedparser.parse(self._url,
                                      etag=None if not self._feed
                                      else self._feed.get('etag'),
                                      modified=None if not self._feed
                                      else self._feed.get('modified'))

        if not self._feed:
            _LOGGER.info('Error fetching feed data from "%s"', self._url)
        else:
            if self._feed.bozo != 0:
                _LOGGER.info('Error parsing feed "%s"', self._url)
            # Using etag and modified, if there's no new data available,
            # the entries list will be empty
            elif len(self._feed.entries) > 0:
                _LOGGER.info('%s entries available in feed "%s"',
                              len(self._feed.entries),
                              self._url)
                self._publish_new_entries()
            else:
                self._log_no_entries()
        _LOGGER.debug('Fetch from feed "%s" completed', self._url)


    def _publish_new_entries(self):
        """Parse XML and publish entries to the event bus."""

        msgno = 1
        msglist = []
        lat2 = 0
        lon2 = 0
        map = ''
        dist = 0

        self._msg_prev = self._msg

        for item in self._feed.entries:
          if item.has_key('geo_lat'):
            lat2 = float(item.geo_lat)
          if item.has_key('geo_long'):
            lon2 = float(item.geo_long)
          if item.has_key('published'):
            pubdate = item.published
          if item.has_key('link'):
            link = item.link

          if lat2 and lon2:
            dist = gpxpy.geo.haversine_distance(self._lat, self._lon, lat2, lon2)
#            map = '<a href>https://maps.google.com/?q='+str(lat2)+','+str(lon2)+'>Location</a>'

          if dist <= self._maxdist:
#            self._update_and_fire_entry(item.title.replace("~","")+'\n'+pubdate+'\n'+map+'\n')
            msglist.append(item.title.replace("~","")+'\n'+pubdate+'\n'+map+'\n')
            msgno += 1

          if msgno > self._maxmsgs:
            break

        self._msg = ''.join(msglist)

        if self._msg == self._msg_prev:
          _LOGGER.info('Message is the same as previous, skipping.')
        else:
          self._hass.bus.fire(EVENT_P2000, { ATTR_TEXT: self._msg })
