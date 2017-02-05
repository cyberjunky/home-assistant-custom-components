"""
Support for publishing random remarks on eventbus to be used in automation.
    file: 1100tags.txt
    hour: 21
    minute: 0
    outside_temp_sensor: sensor.pws_temp_c
    cold_threshold: 5
    freeze_threshold: -5
    temp_hour: 6
    temp_minute: 30
"""
import random
from logging import getLogger

import voluptuous as vol

from homeassistant.helpers.event import track_time_change
import homeassistant.helpers.config_validation as cv

_LOGGER = getLogger(__name__)

CONF_FILE = 'file'
CONF_OUTSIDE_T_SENSOR = 'outside_temp_sensor'
CONF_COLD_THRESHOLD = 'cold_threshold'
CONF_FREEZE_THRESHOLD = 'freeze_threshold'
CONF_HOUR = 'hour'
CONF_MINUTE = 'minute'
CONF_TEMP_HOUR = 'temp_hour'
CONF_TEMP_MINUTE = 'temp_minute'

DEFAULT_INTERVAL = 6
DEFAULT_OUTSIDE_T_SENSOR = 'sensor.pws_feelslike_c'
DEFAULT_COLD_THRESHOLD = 15
DEFAULT_FREEZE_THRESHOLD = 4
DEFAULT_FILE = '1100tags.txt'
DEFAULT_HOUR = 9
DEFAULT_MINUTE = 0
DEFAULT_TEMP_HOUR = 6
DEFAULT_TEMP_MINUTE = 30

ATTR_TEXT = 'text'

DOMAIN = 'remarks'
EVENT_REMARKS = 'remarks'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(CONF_FILE, default=DEFAULT_FILE): cv.string,
        vol.Optional(CONF_HOUR, default=DEFAULT_HOUR): vol.Any(
            vol.Coerce(int),
            vol.Coerce(str)),
        vol.Optional(CONF_MINUTE, default=DEFAULT_MINUTE): vol.Any(
            vol.Coerce(int),
            vol.Coerce(str)),
        vol.Optional(CONF_OUTSIDE_T_SENSOR,
                     default=DEFAULT_OUTSIDE_T_SENSOR): cv.entity_id,
        vol.Optional(CONF_COLD_THRESHOLD,
                     default=DEFAULT_COLD_THRESHOLD): vol.Coerce(float),
        vol.Optional(CONF_FREEZE_THRESHOLD,
                     default=DEFAULT_FREEZE_THRESHOLD): vol.Coerce(float),
        vol.Optional(CONF_TEMP_HOUR, default=DEFAULT_TEMP_HOUR): vol.Any(
            vol.Coerce(int),
            vol.Coerce(str)),
        vol.Optional(CONF_TEMP_MINUTE, default=DEFAULT_TEMP_MINUTE): vol.Any(
            vol.Coerce(int),
            vol.Coerce(str)),
    }),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up the remarks component."""

    remarksfile = config.get(DOMAIN)[CONF_FILE]
    outside_temp_sensor = config.get(DOMAIN)[CONF_OUTSIDE_T_SENSOR]
    cold_threshold = config.get(DOMAIN)[CONF_COLD_THRESHOLD]
    freeze_threshold = config.get(DOMAIN)[CONF_FREEZE_THRESHOLD]
    hour = config.get(DOMAIN)[CONF_HOUR]
    minute = config.get(DOMAIN)[CONF_MINUTE]
    temp_hour = config.get(DOMAIN)[CONF_TEMP_HOUR]
    temp_minute = config.get(DOMAIN)[CONF_TEMP_MINUTE]

    RemarksManager(remarksfile, outside_temp_sensor, cold_threshold,
                   freeze_threshold, hour, minute, temp_hour,
                   temp_minute, hass)
    return True


# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods
class RemarksManager(object):
    """Get data from remarks files."""

    # pylint: disable=too-many-arguments
    def __init__(self, remarksfile, temp_sensor,
                 cold_threshold, freeze_threshold, hour, minute,
                 temp_hour, temp_minute, hass):
        """Initialize the data object."""
        self._hass = hass
        self._cfgdir = self._hass.config.config_dir
        self._remarksfile = self._cfgdir+'/remarks/'+remarksfile
        self._temp_sensor = temp_sensor
        self._cold_threshold = cold_threshold
        self._cold_temp_file = self._cfgdir+'/remarks/list_temp_below_20.txt'
        self._freeze_threshold = freeze_threshold
        self._freeze_temp_file = self._cfgdir+'/remarks/list_temp_below_0.txt'
        self._remark = None
        self._hour = hour
        self._minute = minute
        self._temp_hour = temp_hour
        self._temp_minute = temp_minute

        track_time_change(hass, lambda now: self._get_remark(),
                          hour=self._hour, minute=self._minute, second=0)

        track_time_change(hass, lambda now: self._get_temp_remark(),
                          hour=self._temp_hour, minute=self._temp_minute,
                          second=0)

    def _get_remark(self):
        """Grab random remark from file and publish it to the event bus."""

        _LOGGER.debug('Fetching remark from file "%s"', self._remarksfile)

        lines = open(str(self._remarksfile)).read().splitlines()
        self._remark = random.choice(lines)

        _LOGGER.debug('Fire event for new remark')
        self._hass.bus.fire(EVENT_REMARKS, {ATTR_TEXT: self._remark})

    def _get_temp_remark(self):
        """Grab random tempremark from file and publish it on event bus."""

        sensor = self._hass.states.get(self._temp_sensor)
        unit = sensor.attributes.get('unit_of_measurement')

        if float(sensor.state) < float(self._freeze_threshold):
            _LOGGER.debug('Fetching remark from "%s"', self._freeze_temp_file)
            lines = open(str(self._freeze_temp_file)).read().splitlines()
            self._remark = 'It is currently ' + sensor.state + unit +\
                           ' outside. ' + random.choice(lines)
            _LOGGER.debug('Event for freezetemp remark, temp is %s%s',
                          sensor.state, unit)
            self._hass.bus.fire(EVENT_REMARKS, {ATTR_TEXT: self._remark})
        elif float(sensor.state) < float(self._cold_threshold):
            _LOGGER.debug('Fetching remark from "%s"', self._cold_temp_file)
            lines = open(str(self._cold_temp_file)).read().splitlines()
            self._remark = 'It is currently ' + sensor.state + unit +\
                           ' outside. '+random.choice(lines)
            _LOGGER.debug('Event for coldtemp remark, temp is%s%s',
                          sensor.state, unit)
            self._hass.bus.fire(EVENT_REMARKS, {ATTR_TEXT: self._remark})
