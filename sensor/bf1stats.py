"""
Support for getting information about BattleField 1 online player counts.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.bf1stats/
"""
import datetime
import logging
import requests

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_NAME, STATE_UNKNOWN, ATTR_ATTRIBUTION)
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle
import homeassistant.helpers.config_validation as cv

_RESOURCE = 'http://api.bf1stats.com/api/onlinePlayers'
_LOGGER = logging.getLogger(__name__)

CONF_ATTRIBUTION = 'Data provided by bf1stats.com'

DEFAULT_NAME = 'Battlefield 1 Stats'
ICON = 'mdi:gamepad-variant'
UNIT = 'Players'

MIN_TIME_BETWEEN_UPDATES = datetime.timedelta(seconds=30)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the BF1Stats sensor."""
    rest = BF1StatsData(hass)
    name = config.get(CONF_NAME)

    try:
        rest.update()
    except ValueError as err:
        _LOGGER.error("Received error from BF1Stats: %s", err)
        return False

    add_devices([BF1StatsSensor(rest, name)])

    return False


class BF1StatsSensor(Entity):
    """Representation of a BF1Stats sensor."""

    def __init__(self, rest, name):
        """Initialize a BF1Stats sensor."""
        self.rest = rest
        self._name = name

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        if self.rest.data:
            return int(self.rest.data['pc']['count'])\
                + int(self.rest.data['xone']['count'])\
                + int(self.rest.data['ps4']['count'])
        else:
            return STATE_UNKNOWN

    @property
    def device_state_attributes(self):
        """Return the state attributes of this device."""
        attr = {}
        attr['PC'] = int(self.rest.data['pc']['count'])
        attr['XBOX'] = int(self.rest.data['xone']['count'])
        attr['PS4'] = int(self.rest.data['ps4']['count'])
        attr[ATTR_ATTRIBUTION] = CONF_ATTRIBUTION
        return attr

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return UNIT

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return ICON

    def update(self):
        """Update current values."""
        self.rest.update()


# pylint: disable=too-few-public-methods
class BF1StatsData(object):
    """Get data from BF1Stats API."""

    def __init__(self, hass):
        """Initialize the data object."""
        self._hass = hass
        self.data = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from BF1Stats API."""
        try:
            self.data = requests.get(_RESOURCE, timeout=10).json()
        except ValueError as err:
            _LOGGER.error("Check BF1Stats %s", err.args)
            self.data = None
            raise
