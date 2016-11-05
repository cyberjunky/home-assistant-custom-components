"""
Support for Eneco's Toon thermostats.
Only the rooted version.

configuration.yaml

climate:
  - platform: toon
    name: <Name of Toon> (default = 'Toon Thermostat')
    host: <IP address of Toon>
    port: <Port used by Toon> (default is 10080)
    scan_interval: 10

"""
import voluptuous as vol
import logging

from homeassistant.components.climate import (
    STATE_HEAT, STATE_IDLE, ClimateDevice, PLATFORM_SCHEMA, ATTR_OPERATION_MODE)
from homeassistant.const import (
    CONF_NAME, CONF_HOST, CONF_PORT, CONF_SCAN_INTERVAL, TEMP_CELSIUS, ATTR_TEMPERATURE)
import homeassistant.helpers.config_validation as cv

from urllib.request import urlopen
import json

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'Toon Thermostat'
BASE_URL = 'http://{0}:{1}{2}'

ATTR_MODE = 'mode'
STATE_MANUAL = 'manual'
STATE_UNKNOWN = 'unknown'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PORT, default=10800): cv.positive_int,
    vol.Optional(CONF_SCAN_INTERVAL, default=10): cv.positive_int,
})


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the Toon thermostats."""
    scan_interval = config.get(CONF_SCAN_INTERVAL)

    add_devices([ToonThermostat(config.get(CONF_NAME), config.get(CONF_HOST), config.get(CONF_PORT))])


# pylint: disable=abstract-method
class ToonThermostat(ClimateDevice):
    """Representation of a Toon thermostat."""

    def __init__(self, name, host, port):
        """Initialize the thermostat."""
        self._name = name
        self._host = host
        self._port = port
        self._current_temp = 0
        self._current_setpoint = 0
        self._current_state = -1
        self._current_operation = ''
        self._set_state = 0
        self._operation_list = ['Comfort', 'Home', 'Sleep', 'Away', 'Holiday']
        self.update()

    def get_json_data(self, url):
        response = urlopen(url)
        data = response.read().decode("utf-8")
        return json.loads(data)

    @property
    def should_poll(self):
        """Polling needed for thermostat."""
        return True

    def update(self):
        """Update the data from the thermostat."""
        self._data = self.get_json_data(BASE_URL.format(self._host, self._port, '/happ_thermstat?action=getThermostatInfo'))
        self._current_setpoint = int(self._data['currentSetpoint'])/100
        self._current_temp = int(self._data['currentTemp'])/100
        self._current_state = int(self._data['activeState'])
         
    @property
    def name(self):
        """Return the name of the thermostat."""
        return self._name

    @property
    def device_state_attributes(self):
        """Return the device specific state attributes."""
        return {
            ATTR_MODE: self._current_state
        }

    @property
    def current_operation(self):
        """Return the current operation mode."""
        return self._current_operation

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temp

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._current_setpoint

    @property
    def current_operation(self):
        """Return the current state of the thermostat."""
        state = self._current_state
        if state in (0, 1, 2, 3, 4):
            return self._operation_list[state]  
        elif state == -1:
            return STATE_MANUAL
        else:
            return STATE_UNKNOWN

    @property
    def operation_list(self):
        """List of available operation modes."""
        return self._operation_list

    def set_operation_mode(self, operation_mode):
        """Set HVAC mode (comfort, home, sleep, away, holiday)."""
        if operation_mode == "Comfort":
            mode = 0
        elif operation_mode == "Home":
            mode = 1
        elif operation_mode == "Sleep":
            mode = 2
        elif operation_mode == "Away":
            mode = 3
        elif operation_mode == "Holiday":
            mode = 4

        self._data = self.get_json_data(BASE_URL.format(self._host, self._port, '/happ_thermstat?action=changeSchemeState&state=2&temperatureState='+str(mode)))
        _LOGGER.debug("set_operation_mode=%s", str(operation_mode))
        _LOGGER.debug("set_operation_mode=%s", str(mode))

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)*100
        if temperature is None:
            return
        else:
            self._data = self.get_json_data(BASE_URL.format(self._host, self._port, '/happ_thermstat?action=setSetpoint&Setpoint='+str(temperature)))
            _LOGGER.debug("set_temperature=%s", str(temperature))
