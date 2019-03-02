"""
Support for Volkswagen Carnet platform.
Customized for VW T-ROC.
"""
import logging
from custom_components.volkswagencarnet import VolkswagenEntity, RESOURCES
from homeassistant.helpers.icon import icon_for_battery_level

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up the Volkswagen sensors."""
    if discovery_info is None:
        return
    add_devices([VolkswagenSensor(hass, *discovery_info)])


class VolkswagenSensor(VolkswagenEntity):
    """Representation of a Volkswagen Carnet Sensor."""
    @property
    def state(self):
        """Return the state of the sensor."""
        _LOGGER.debug('Getting state of %s sensor' % self._attribute)

        val = getattr(self.vehicle, self._attribute)
        if val is None:
            return val
        if self._attribute in ['last_connected', 'service_inspection', 'oil_inspection']:
            return str(val)
        else:
            return int(float(val))

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return RESOURCES[self._attribute][3]

    @property
    def icon(self):
        """Return the icon."""
        return RESOURCES[self._attribute][2]

    @property
    def available(self):
        """Return True if entity is available."""
        return True

