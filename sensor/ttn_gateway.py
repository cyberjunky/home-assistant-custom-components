"""
Support for reading The Things Network gateway status.

configuration.yaml

sensor:
  - platform: ttn_gateway
    host: IP_ADDRESS
    scan_interval: 10
    resources:
      - gateway
      - hwversion
      - blversion
      - fwversion
      - uptime
      - connected
      - interface
      - ssid
      - activationlocked
      - configured
      - region
      - gwcard
      - brokerconnected
      - packetsup
      - packetsdown
      - estore
"""
import logging
from datetime import timedelta
import requests
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_HOST, CONF_SCAN_INTERVAL, CONF_RESOURCES)
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

BASE_URL = 'http://{0}{1}'
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=10)

SENSOR_PREFIX = 'TTN_GW '

SENSOR_TYPES = {
    'gateway': ['Gateway', '', 'mdi:router-wireless'],
    'hwversion': ['Hardware Version', '', 'mdi:file-document-box'],
    'blversion': ['Bootloader Version', '', 'mdi:file-document-box'],
    'fwversion': ['Firmware Version', '', 'mdi:file-document-box'],
    'uptime': ['Uptime', 'Sec.', 'mdi:timer-sand'],
    'connected': ['Connected', '', 'mdi:power-plug'],
    'interface': ['Interface', '', 'mdi:ethernet-cable'],
    'ssid': ['SSID', '', 'mdi:access-point'],
    'activationlocked': ['Activation Locked', '', 'mdi:lock-outline'],
    'configured': ['Configured', '', 'mdi:settings'],
    'region': ['Region', '', 'mdi:map-marker-radius'],
    'gwcard': ['Gateway Card', '', 'mdi:radio-tower'],
    'brokerconnected': ['Broker Connected', '', 'mdi:forum-outline'],
    'packetsup': ['Packets Up', '', 'mdi:gauge'],
    'packetsdown': ['Packets Down', '', 'mdi:gauge'],
    'estore': ['External Storage', '', 'mdi:sd'],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_RESOURCES, default=[]):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the TTN gateway sensors."""
    scan_interval = config.get(CONF_SCAN_INTERVAL)
    host = config.get(CONF_HOST)

    try:
        data = TTNGatewayData(host)
    except requests.exceptions.HTTPError as error:
        _LOGGER.error(error)
        return False

    entities = []

    for resource in config[CONF_RESOURCES]:
        sensor_type = resource.lower()

        if sensor_type not in SENSOR_TYPES:
            SENSOR_TYPES[sensor_type] = [
                sensor_type.title(), '', 'mdi:flash']

        entities.append(TTNGatewayStatusSensor(data, sensor_type))

    add_entities(entities)


# pylint: disable=abstract-method
class TTNGatewayData(object):
    """Representation of a TTN gateway status."""

    def __init__(self, host):
        """Initialize the data."""
        self._host = host
        self.data = None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Update the data from the gateway."""
        try:
            self.data = requests.get(BASE_URL.format(self._host, '/status.cgi'), timeout=5).json()
            _LOGGER.debug("Data = %s", self.data)
        except requests.exceptions.RequestException:
            _LOGGER.error("Error occurred while fetching data.")
            self.data = None
            return False

 
class TTNGatewayStatusSensor(Entity):
    """Representation of a TTN gateway data."""

    def __init__(self, data, sensor_type):
        """Initialize the sensor."""
        self.data = data
        self.type = sensor_type
        self._name = SENSOR_PREFIX + SENSOR_TYPES[self.type][0]
        self._unit = SENSOR_TYPES[self.type][1]
        self._icon = SENSOR_TYPES[self.type][2]
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit

    @property
    def device_state_attributes(self):
        """Return the state attributes of this device."""
        attr = {}
        return attr

    def update(self):
        """Get the latest data and use it to update our sensor state."""
        self.data.update()
        status = self.data.data

        if self.type == 'gateway':
            if 'gateway' in status:
                self._state = status["gateway"]

        elif self.type == 'hwversion':
            if 'hwversion' in status:
                self._state = status["hwversion"]

        elif self.type == 'blversion':
            if 'blversion' in status:
                self._state = status["blversion"]

        elif self.type == 'fwversion':
            if 'fwversion' in status:
                self._state = status["fwversion"]

        elif self.type == 'uptime':
            if 'uptime' in status:
                self._state = status["uptime"]

        elif self.type == 'connected':
            if 'connected' in status:
                self._state = status["connected"]

        elif self.type == 'interface':
            if 'interface' in status:
                self._state = status["interface"]

        elif self.type == 'ssid':
            if 'ssid' in status:
                self._state = status["ssid"]

        elif self.type == 'activationlocked':
            if 'activation_locked' in status:
                self._state = status["activation_locked"]

        elif self.type == 'configured':
            if 'configured' in status:
                self._state = status["configured"]

        elif self.type == 'region':
            if 'region' in status:
                self._state = status["region"]

        elif self.type == 'gwcard':
            if 'gwcard' in status:
                self._state = status["gwcard"]

        elif self.type == 'brokerconnected':
            if 'connbroker' in status:
                self._state = status["connbroker"]

        elif self.type == 'packetsup':
            if 'pup' in status:
                self._state = status["pup"]

        elif self.type == 'packetsdown':
            if 'pdown' in status:
                self._state = status["pdown"]

        elif self.type == 'estore':
            if 'estor' in status:
                self._state = status["estor"]
