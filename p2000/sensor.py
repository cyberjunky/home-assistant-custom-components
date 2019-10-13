"""
Support for fetching emergency services events near your location.
Dutch P2000 based.

"""
import logging
import datetime
import requests
import voluptuous as vol
import feedparser
from geopy.distance import vincenty

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_NAME, STATE_UNKNOWN, ATTR_ATTRIBUTION,
     ATTR_LONGITUDE, ATTR_LATITUDE, CONF_LONGITUDE, CONF_LATITUDE,
     CONF_RADIUS)

from homeassistant.helpers.entity import Entity
import homeassistant.util as util
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['geopy','feedparser']

_LOGGER = logging.getLogger(__name__)
_RESOURCE = 'https://feeds.livep2000.nl?r={}&d={}'

CONF_REGIOS = 'regios'
CONF_DISCIPLINES = 'disciplines'
CONF_ATTRIBUTION = 'Data provided by feeds.livep2000.nl'

DEFAULT_NAME = 'P2000'
ICON = 'mdi:ambulance'
DEFAULT_DISCIPLINES = '1,2,3,4'
DEFAULT_RADIUS_IN_MTR = 5000
MIN_TIME_BETWEEN_UPDATES = datetime.timedelta(seconds=10)
SCAN_INTERVAL = datetime.timedelta(seconds=30)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
        vol.Required(CONF_REGIOS): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_DISCIPLINES, default=DEFAULT_DISCIPLINES): cv.string,
        vol.Optional(CONF_RADIUS, default=DEFAULT_RADIUS_IN_MTR): vol.Coerce(float),
        vol.Optional(CONF_LATITUDE): cv.latitude,
        vol.Optional(CONF_LONGITUDE): cv.longitude,
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the P2000 sensor."""

    name = config.get(CONF_NAME)
    regios = config.get(CONF_REGIOS)
    disciplines = config.get(CONF_DISCIPLINES)
    latitude = util.convert(config.get(CONF_LATITUDE, hass.config.latitude), float)
    longitude = util.convert(config.get(CONF_LONGITUDE, hass.config.longitude), float)
    radius_in_mtr = config[CONF_RADIUS]
    url = _RESOURCE.format(regios, disciplines)

    try:
        data = P2000Data(hass, latitude, longitude, url, radius_in_mtr)
        data.update()
    except requests.exceptions.HTTPError as error:
        _LOGGER.error(error)
        return False

    add_devices([P2000Sensor(data, name)])


class P2000Sensor(Entity):
    """Representation of a P2000 Sensor."""

    def __init__(self, data, name):
        """Initialize a P2000 sensor."""
        self.data = data
        self._name = name
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self.data.data

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {}
        if self.data:
            attrs[ATTR_LONGITUDE] = self.data.longitude
            attrs[ATTR_LATITUDE] = self.data.latitude
            attrs['distance'] = self.data.distance
            attrs['time'] = self.data.msgtime
            attrs[ATTR_ATTRIBUTION] = CONF_ATTRIBUTION
            return attrs

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return ICON

    def update(self):
        """Update current values."""
        self.data.update()
        _LOGGER.debug("State updated to %s", self.data.data)


class P2000Data(object):
    """Get data from P2000 feed."""

    def __init__(self, hass, latitude, longitude, url, radius_in_mtr):
        """Initialize the data object."""
        self._url = url
        self._maxdist = radius_in_mtr
        self._feed = None
        self._lastmsg_time = None
        self._restart = True
        self._hass = hass
        self._lat = latitude
        self._lon = longitude
        self._msgtxt = None
        self.data = None
        self.latitude = 0.0
        self.longitude = 0.0
        self.distance = None
        self.msgtime = None

    @staticmethod
    def _convert_time(time):
        return datetime.datetime.strptime(time.split(",")[1][:-6],
                                          " %d %b %Y %H:%M:%S")

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):

        _LOGGER.debug('Fetching data from feed "%s"', self._url)
        try:
            self._feed = feedparser.parse(self._url,
                                      etag=None if not self._feed
                                      else self._feed.get('etag'),
                                      modified=None if not self._feed
                                      else self._feed.get('modified'))
            _LOGGER.debug('Feed: "%s"', self._feed)

            if not self._feed:
                _LOGGER.debug('Error fetching feed data from "%s"', self._url)
            else:
                msgtext = ''
                if self._feed.bozo != 0:
                    _LOGGER.debug('Error parsing feed "%s"', self._url)
                # Using etag and modified, if there's no new data available,
                # the entries list will be empty
                elif len(self._feed.entries) > 0:
                    _LOGGER.debug('%s entries available in feed "%s"',
                              len(self._feed.entries),
                              self._url)
                              
                    if self._restart:
                        pubdate = self._feed.entries[0]['published']
                        self._lastmsg_time = self._convert_time(pubdate)
                        self._restart = False
                        _LOGGER.info('Restarted, last datestamp %s.', self._lastmsg_time)
                        return
                      
                    for item in reversed(self._feed.entries):
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
                            _LOGGER.debug('Calculated distance is %d meters, max. range is %d meters', dist, self._maxdist)

                        if dist > self._maxdist:
                            msgtext = ''
                            continue

                if msgtext != "":
                    self.data = msgtext
                    self.latitude = lat_event
                    self.longitude = lon_event
                    self.distance = int(round(dist))
                    self.msgtime = lastmsg_time
                else:
                    _LOGGER.debug('No new entries found in feed "%s"', self._url)
            _LOGGER.debug('Fetch from feed "%s" completed.', self._url)

        except ValueError as err:
            _LOGGER.error("Check P2000 %s", err.args)
            self.data = None
