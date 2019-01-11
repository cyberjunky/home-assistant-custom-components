"""
Support for reading trash pickup data for HVC groep.

configuration.yaml

sensor:
  - platform: hvcgroep
    postcode: 1234AB
    huisnummer: 1
    resources:
      - gft
      - plastic
      - papier
      - restafval
"""

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_NAME, CONF_SCAN_INTERVAL, CONF_RESOURCES)
from homeassistant.util import Throttle

import voluptuous as vol
from datetime import timedelta
from datetime import datetime

import requests
import json
import logging

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=10)
#timedelta(hours=1)

DEFAULT_NAME = 'HVC Groep'
ICON = 'mdi:delete-empty'
CONST_POSTCODE = "postcode"
CONST_HUISNUMMER = "huisnummer"

# Predefined types and id's
TRASH_TYPES = {
    'gft': [5, 'Groene Bak GFT', 'mdi:delete-empty'],
    'plastic': [6, 'Plastic en Verpakking', 'mdi:delete-empty'],
    'papier': [3, 'Blauwe Bak Papier', 'mdi:delete-empty'],
    'restafval': [2, 'Grijze Bak Restafval', 'mdi:delete-empty'],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONST_POSTCODE): cv.string,
    vol.Required(CONST_HUISNUMMER): cv.string,
    vol.Required(CONF_RESOURCES, default=[]):
        vol.All(cv.ensure_list, [vol.In(TRASH_TYPES)]),
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Setup the HVCGroep sensors."""
    scan_interval = config.get(CONF_SCAN_INTERVAL)
    postcode = config.get(CONST_POSTCODE)
    huisnummer = config.get(CONST_HUISNUMMER)
    name = config.get(CONF_NAME)

    try:
        data = TrashData(postcode, huisnummer)
    except requests.exceptions.HTTPError as error:
        _LOGGER.error(error)
        return False

    entities = []
    for resource in config[CONF_RESOURCES]:
        trash_type = resource.lower()
        
        entities.append(TrashSensor(data, name, trash_type))
    add_entities(entities, True)


# pylint: disable=abstract-method
class TrashData(object):
    """Fetch data from HVCGroep API."""

    def __init__(self, postcode, huisnummer):
        """Initialize."""
        self._postcode = postcode
        self._huisnummer = huisnummer
        self._bagId = None
        self.data = None
        trashschedule = []

        """Get the bagId using the postcode and huisnummer."""
        try:
            json_data = requests.get(("https://apps.hvcgroep.nl/rest/adressen/{0}-{1}").format(self._postcode, self._huisnummer), timeout=5).json()
            _LOGGER.debug("Get bagId data = %s", json_data)
            self._bagId = json_data[0]["bagId"]
            _LOGGER.debug("Parsed bagId = %s", self._bagId)
        except requests.exceptions.RequestException:
            _LOGGER.error("Cannot fetch the bagId %s.", err.args)
            self.data = None
            return False


    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the afvalstromen data."""
        trashschedule = []
        try:
            json_data = requests.get(("https://apps.hvcgroep.nl/rest/adressen/{0}/afvalstromen").format(self._bagId), timeout=5).json()
            _LOGGER.debug("Get afvalstromen data = %s", json_data)
        except requests.exceptions.RequestException:
            _LOGGER.error("Cannot fetch afvalstromen %s.", err.args)
            self.data = None
            return False

        """Parse the afvalstromen data."""
        try:
            for afval in json_data:
               if afval['ophaaldatum'] != None:
                  _LOGGER.debug(" Afvalstromen id: %s Type: %s Datum: %s", afval['id'], afval['title'], afval['ophaaldatum'])
                  trash = {}
                  trash['id'] = afval['id']
                  trash['title'] = afval['title']
                  trash['date'] = datetime.strptime(afval['ophaaldatum'], '%Y-%m-%d')
                  trashschedule.append(trash)
            self.data = trashschedule
        except ValueError as err:
            _LOGGER.error("Cannot parse the bagId %s", err.args)
            self.data = None
            return False


class TrashSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, data, name, trash_type):
        """Initialize the sensor."""
        self.data = data
        self._trash_type = trash_type
        self._name = name + "_" + self._trash_type
        self._id =  TRASH_TYPES[self._trash_type][0]
        self._icon = TRASH_TYPES[self._trash_type][2]
        self._day = None
        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def device_state_attributes(self):
        """Return the state attributes of this device."""
        return {
            "day": self._day,
        }

    def update(self):
        """Fetch new state data for the sensor."""
        self.data.update()
        _LOGGER.debug("Update = %s", self.data.data)

        today = datetime.today()
        for d in self.data.data:
           pickupdate = d['date']
           datediff = (pickupdate - today).days + 1
           if d['id'] == self._id:
              if datediff > 1:
                 self._state = pickupdate.strftime('%d-%m-%Y')
                 self._day = None
              elif datediff == 1:
                 self._state = pickupdate.strftime('Morgen %d-%m-%Y')
                 self._day = "Morgen"
              elif datediff <= 0:
                 self._state = pickupdate.strftime('Vandaag %d-%m-%Y')
                 self._day = "Vandaag"
              else:
                 self._state = None
                 self._day = None
