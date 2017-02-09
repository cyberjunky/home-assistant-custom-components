"""
Support for reading Solar Inverter data from various portals.

configuration.yaml

sensor:
  - platform: solarportal
    host: www.omnikportal.com
    port: 10000
    username: PORTAL_LOGIN
    password: PORTAL_PASSWORD
    scan_interval: 30
    resources:
      - actualpower
      - energytoday
      - energytotal
      - incometoday
      - incometotal
"""
import logging
from datetime import timedelta
import voluptuous as vol
from urllib.request import urlopen
from xml.etree import ElementTree as ET
import hashlib

from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
        CONF_USERNAME, CONF_PASSWORD, CONF_HOST, CONF_PORT,
        CONF_RESOURCES
    )
from homeassistant.util import Throttle
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)

BASE_URL = 'http://{0}:{1}{2}'
MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

SENSOR_PREFIX = 'Solar '
SENSOR_TYPES = {
    'actualpower': ['Actual Power', 'Watt', 'mdi:weather-sunny'],
    'energytoday': ['Energy Today', 'kWh', 'mdi:flash'],
    'energytotal': ['Energy Total', 'kWh', 'mdi:flash'],
    'incometoday': ['Income Today', 'EUR', 'mdi:cash-100'],
    'incometotal': ['Income Total', 'EUR', 'mdi:cash-100'],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_RESOURCES, default=[]):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
    vol.Optional(CONF_PORT, default=10000): cv.positive_int,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the Solar Portal sensors."""
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)

    try:
        data = SolarPortalData(host, port, username, password)
    except RunTimeError:
        _LOGGER.error("Unable to connect fetch data from Solar Portal %s:%s",
                      host, port)
        return False

    entities = []

    for resource in config[CONF_RESOURCES]:
        sensor_type = resource.lower()

        if sensor_type not in SENSOR_TYPES:
            SENSOR_TYPES[sensor_type] = [
                sensor_type.title(), '', 'mdi:flash']

        entities.append(SolarPortalSensor(data, sensor_type))

    add_entities(entities)


# pylint: disable=abstract-method
class SolarPortalData(object):
    """Representation of a Solar Portal."""

    def __init__(self, host, port, username, password):
        """Initialize the portal."""
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self.data = None

        mdhash = hashlib.md5()
        mdhash.update(self._password.encode('utf-8'))
        pwhash = mdhash.hexdigest()

        # get token
        requesturl = BASE_URL.format(
                   self._host, self._port,
                   '/serverapi/?method=Login&username='
                   + self._username + '&password=' + pwhash +
                   '&key=apitest&client=iPhone'
        )
        root = ET.parse(urlopen(requesturl)).getroot()
        self.token = root.find('token').text

        # get (only first) station
        stationlisturl = BASE_URL.format(
                    self._host, self._port,
                    '/serverapi/?method=Powerstationslist&username='
                    + self._username + '&token=' + self.token + '&key=apitest'
        )

        stationroot = ET.parse(urlopen(stationlisturl)).getroot()
        for elem in stationroot.findall('power'):
            self.stationid = elem.find('stationID').text

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Update the data from the portal."""
        dataurl = BASE_URL.format(
                self._host, self._port,
                '/serverapi/?method=Data&username=' + self._username +
                '&stationid=' + str(self.stationid) + '&token=' +
                self.token + '&key=apitest'
        )
        self.data = ET.parse(urlopen(dataurl)).getroot()
        _LOGGER.debug("Data = %s", self.data)


class SolarPortalSensor(Entity):
    """Representation of a SolarPortal sensor from the portal."""

    def __init__(self, data, sensor_type):
        """Initialize the sensor."""
        self.data = data
        self.type = sensor_type
        self._name = SENSOR_PREFIX + SENSOR_TYPES[self.type][0]
        self._unit_of_measurement = SENSOR_TYPES[self.type][1]
        self._icon = SENSOR_TYPES[self.type][2]
        self._state = None
        self.update()

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
        return self._unit_of_measurement

    def update(self):
        """Get the latest data and use it to update our sensor state."""
        self.data.update()

        income = self.data.data.find('income')
        if self.type == 'actualpower':
            self._state = income.find('ActualPower').text
        elif self.type == 'energytoday':
            self._state = income.find('etoday').text
        elif self.type == 'energytotal':
            self._state = income.find('etotal').text
        elif self.type == 'incometoday':
            self._state = income.find('TodayIncome').text
        elif self.type == 'incometotal':
            self._state = income.find('TotalIncome').text
