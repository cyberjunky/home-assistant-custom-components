# original from https://gist.github.com/Sanderhuisman/e609a99682854d9f880f8334b7194558

import logging
from datetime import timedelta

import os
import threading
import time

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    CONF_HOST,
    CONF_MONITORED_CONDITIONS,
    EVENT_HOMEASSISTANT_STOP
)
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

REQUIREMENTS = ['docker==3.7.0']

_LOGGER = logging.getLogger(__name__)

DEFAULT_HOST        = 'unix://var/run/docker.sock'
CONF_CONTAINERS     = 'containers'

CONF_ATTRIBUTION    = 'Data provided by Docker'
ATTR_ONLINE_CPUS    = 'online_cpus'

PRECISION           = 2

UTILISATION_MONITOR_VERSION         = 'utilization_version'

CONTAINER_MONITOR_STATUS            = 'container_status'
CONTAINER_MONITOR_MEMORY_USAGE      = 'container_memory_usage'
CONTAINER_MONITOR_MEMORY_PERCENTAGE = 'container_memory_percentage_usage'
CONTAINER_MONITOR_CPU_PERCENTAGE    = 'container_cpu_percentage_usage'
CONTAINER_MONITOR_NETWORK_UP        = 'container_network_up'
CONTAINER_MONITOR_NETWORK_DOWN      = 'container_network_down'

_UTILISATION_MON_COND = {
    UTILISATION_MONITOR_VERSION         : ['Version'                , None      , 'mdi:memory'],
}

_CONTAINER_MON_COND = {
    CONTAINER_MONITOR_STATUS            : ['Status'                 , None      , 'mdi:checkbox-marked-circle-outline'  ],
    CONTAINER_MONITOR_MEMORY_USAGE      : ['Memory use'             , 'bytes'   , 'mdi:memory'                          ],
    CONTAINER_MONITOR_MEMORY_PERCENTAGE : ['Memory use (percent)'   , '%'       , 'mdi:memory'                          ],
    CONTAINER_MONITOR_CPU_PERCENTAGE    : ['CPU use'                , '%'       , 'mdi:chip'                            ],
    CONTAINER_MONITOR_NETWORK_UP        : ['Network Up'             , 'Bytes'   , 'mdi:upload'                          ],
    CONTAINER_MONITOR_NETWORK_DOWN      : ['Network Down'           , 'Bytes'   , 'mdi:download'                        ],
}

_MONITORED_CONDITIONS = list(_UTILISATION_MON_COND.keys()) + \
    list(_CONTAINER_MON_COND.keys())

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_HOST, default=DEFAULT_HOST): cv.string,
    vol.Optional(CONF_MONITORED_CONDITIONS):
        vol.All(cv.ensure_list, [vol.In(_MONITORED_CONDITIONS)]),
    vol.Optional(CONF_CONTAINERS): cv.ensure_list,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Docker Sensor."""
    import docker

    host                    = config.get(CONF_HOST)
    monitored_conditions    = config.get(CONF_MONITORED_CONDITIONS)

    try:
        api = docker.DockerClient(base_url=host)
    except:
        _LOGGER.info("Error setting up Docker sensor")
        return

    version = dockerVersion(api)
    _LOGGER.info("Docker version: {}".format(version.get('version', None)))

    threads = {}

    sensors = [DockerUtilSensor(api, variable) for variable in monitored_conditions if variable in _UTILISATION_MON_COND]

    containers      = api.containers.list(all=True) or []
    container_names = [x.name for x in containers]
    for container in containers:
        _LOGGER.debug("Found container: {}".format(container.name))

    for container_name in config.get(CONF_CONTAINERS, container_names):
        thread = DockerContainerApi(container_name, api)
        threads[container_name] = thread
        thread.start()

        sensors += [DockerContainerSensor(api, thread, variable) for variable in monitored_conditions if variable in _CONTAINER_MON_COND]

    if sensors:
        def monitor_stop(_service_or_event):
            """Stop the monitor thread."""
            _LOGGER.info("Stopping threads for Docker monitor")
            for t in threads.values():
                t.stop()

        add_entities(sensors, True)
        hass.bus.listen_once(EVENT_HOMEASSISTANT_STOP, monitor_stop)

def dockerVersion(api):
    raw_stats = api.version()
    return {
        'version'       : raw_stats.get('Version'   , None),
        'api_version'   : raw_stats.get('ApiVersion', None),
        'os'            : raw_stats.get('Os'        , None),
        'arch'          : raw_stats.get('Arch'      , None),
    }

class DockerContainerApi(threading.Thread):

    def __init__(self, container_name, api):
        self._container_name    = container_name
        self._api               = api

        self._container = self._api.containers.get(self._container_name)
        super(DockerContainerApi, self).__init__()

        self._stopper = threading.Event()
        self._stats = {}
        self._stats_stream = self._container.stats(stream=True, decode=True)

        _LOGGER.debug("Create thread for container {}".format(self._container.name))

    def run(self):
        for i in self._stats_stream:
            self._setStats(i)
            time.sleep(1)
            if self.stopped():
                break

    def stats(self):
        """Stats getter."""
        return self._stats

    def getContainerName(self):
        """Container name getter."""
        return self._container_name

    def stop(self, timeout=None):
        """Stop the thread."""
        _LOGGER.debug("Close thread for container {}".format(self._container.name))
        self._stopper.set()

    def stopped(self):
        """Return True is the thread is stopped."""
        return self._stopper.isSet()

    def _setStats(self, raw_stats):
        stats                   = {}
        stats['id']             = self._container.id
        stats['image']          = self._container.image.tags
        stats['status']         = self._container.attrs['State']['Status']

        if stats['status'] in ('running', 'paused'):
            stats['cpu']            = self._get_docker_cpu(raw_stats)
            stats['memory']         = self._get_docker_memory(raw_stats)
            stats['io']             = self._get_docker_io(raw_stats)
            stats['network']        = self._get_docker_network(raw_stats)

            stats['cpu_percent']    = stats['cpu'].get('total', None)
            stats['memory_usage']   = stats['memory'].get('usage', None)
            stats['memory_percent'] = stats['memory'].get('usage_percent', None)
            stats['io_r']           = stats['io'].get('ior', None)
            stats['io_w']           = stats['io'].get('iow', None)
            stats['network_up']     = stats['network'].get('tx', None)
            stats['network_down']   = stats['network'].get('rx', None)
        else:
            stats['cpu']            = {}
            stats['memory']         = {}
            stats['io']             = {}
            stats['network']        = {}

            stats['cpu_percent']    = None
            stats['memory_usage']   = None
            stats['memory_percent'] = None
            stats['io_r']           = None
            stats['io_w']           = None
            stats['network_up']     = None
            stats['network_down']   = None

        self._stats = stats

    def _get_docker_cpu(self, raw_stats):
        ret = {}
        cpu_new = {}

        try:
            cpu_new['total']    = raw_stats['cpu_stats']['cpu_usage']['total_usage']
            cpu_new['system']   = raw_stats['cpu_stats']['system_cpu_usage']

            if 'online_cpus' in raw_stats['cpu_stats']:
                ret['online_cpus'] = raw_stats['cpu_stats']['online_cpus']
            else:
                ret['online_cpus'] = len(raw_stats['cpu_stats']['cpu_usage']['percpu_usage'] or [])
        except KeyError as e:
            # raw_stats do not have CPU information
            _LOGGER.error("Cannot grab CPU usage for container {} ({})".format(self._container.id, e))
            _LOGGER.debug(raw_stats)
        else:
            if not hasattr(self, 'cpu_old'):
                # First call, we init the cpu_old variable
                try:
                    self.cpu_old = cpu_new
                except (IOError, UnboundLocalError):
                    pass

            cpu_delta       = float(cpu_new['total']  - self.cpu_old['total'])
            system_delta    = float(cpu_new['system'] - self.cpu_old['system'])
            if cpu_delta > 0.0 and system_delta > 0.0:
                ret['total'] = round((cpu_delta / system_delta) * float(ret['online_cpus']) * 100.0, PRECISION)
            else:
                ret['total'] = round(0.0, PRECISION)

            self.cpu_old = cpu_new

        return ret

    def _get_docker_memory(self, raw_stats):
        ret = {}

        try:
            ret['usage'] = raw_stats['memory_stats']['usage']
            ret['limit'] = raw_stats['memory_stats']['limit']
            ret['max_usage'] = raw_stats['memory_stats']['max_usage']
        except (KeyError, TypeError) as e:
            # raw_stats do not have MEM information
            _LOGGER.error("Cannot grab MEM usage for container {} ({})".format(self._container.id, e))
            _LOGGER.debug(raw_stats)
        else:
            ret['usage_percent'] = round(float(ret['usage']) / float(ret['limit']) * 100.0, PRECISION)

        return ret

    def _get_docker_network(self, raw_stats):
        network_new = {}

        try:
            netcounters = raw_stats["networks"]
        except KeyError as e:
            # raw_stats do not have NETWORK information
            _LOGGER.error("Cannot grab NET usage for container {} ({})".format(self._container.id, e))
            _LOGGER.debug(raw_stats)
        else:
            if not hasattr(self, 'inetcounters_old'):
                # First call, we init the network_old var
                try:
                    self.netcounters_old = netcounters
                except (IOError, UnboundLocalError):
                    pass

            try:
                network_new['rx'] = netcounters['eth0']['rx_bytes'] - self.netcounters_old['eth0']['rx_bytes']
                network_new['tx'] = netcounters['eth0']['tx_bytes'] - self.netcounters_old['eth0']['tx_bytes']
                network_new['cumulative_rx'] = netcounters['eth0']['rx_bytes']
                network_new['cumulative_tx'] = netcounters['eth0']['tx_bytes']
            except KeyError as e:
                _LOGGER.debug("Cannot grab network interface usage for container {} ({})".format(self._container.id, e))
                _LOGGER.debug(raw_stats)

            self.netcounters_old = netcounters

        return network_new

    def _get_docker_io(self, raw_stats):
        io_new = {}

        try:
            iocounters = raw_stats['blkio_stats']
        except KeyError as e:
            # raw_stats do not have io information
            _LOGGER.error("Cannot grab block IO usage for container {} ({})".format(self._container.id, e))
            _LOGGER.debug(raw_stats)
            return io_new
        else:
            if not hasattr(self, 'iocounters_old'):
                # First call, we init the io_old var
                try:
                    self.iocounters_old = iocounters
                except (IOError, UnboundLocalError):
                    pass

            try:
                # Read IOR and IOW value in the structure list of dict
                ior = [i for i in iocounters['io_service_bytes_recursive'] if i['op'] == 'Read'][0]['value']
                iow = [i for i in iocounters['io_service_bytes_recursive'] if i['op'] == 'Write'][0]['value']
                ior_old = [i for i in self.iocounters_old['io_service_bytes_recursive'] if i['op'] == 'Read'][0]['value']
                iow_old = [i for i in self.iocounters_old['io_service_bytes_recursive'] if i['op'] == 'Write'][0]['value']
            except (TypeError, IndexError, KeyError) as e:
                _LOGGER.debug("Cannot grab block IO usage for container {} ({})".format(self._container.id, e))
            else:
                io_new['ior'] = ior - ior_old
                io_new['iow'] = iow - iow_old
                io_new['cumulative_ior'] = ior
                io_new['cumulative_iow'] = iow

            self.iocounters_old = iocounters

        return io_new


class DockerUtilSensor(Entity):
    """Representation of a Docker Sensor."""

    def __init__(self, api, variable):
        """Initialize the sensor."""
        self._api           = api

        self._var_id        = variable
        self._var_name      = _UTILISATION_MON_COND[variable][0]
        self._var_unit      = _UTILISATION_MON_COND[variable][1]
        self._var_icon      = _UTILISATION_MON_COND[variable][2]

        self._state         = None
        self._attributes    = {
            ATTR_ATTRIBUTION:   CONF_ATTRIBUTION
        }

        _LOGGER.info("Initializing utilization sensor \"{}\"".format(self._var_id))

    @property
    def name(self):
        """Return the name of the sensor, if any."""
        return "docker_{}".format(self._var_name.lower())

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._var_icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._var_unit

    def update(self):
        """Get the latest data for the states."""
        if self._var_id == UTILISATION_MONITOR_VERSION:
            version = dockerVersion(self._api)
            self._state                         = version.get('version', None)
            self._attributes['api_version']     = version.get('api_version', None)
            self._attributes['os']              = version.get('os', None)
            self._attributes['arch']            = version.get('arch', None)

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

class DockerContainerSensor(Entity):
    """Representation of a Docker Sensor."""

    def __init__(self, api, container_thread, variable):
        """Initialize the sensor."""
        self._api           = api
        self._thread        = container_thread

        self._var_id        = variable
        self._var_name      = _CONTAINER_MON_COND[variable][0]
        self._var_unit      = _CONTAINER_MON_COND[variable][1]
        self._var_icon      = _CONTAINER_MON_COND[variable][2]

        self._state         = None
        self._attributes    = {
            ATTR_ATTRIBUTION:   CONF_ATTRIBUTION
        }

        self._name          = self._thread.getContainerName()

        _LOGGER.info("Initializing Docker sensor \"{}\" with parameter: {}".format(self._name, self._var_name))

    @property
    def name(self):
        """Return the name of the sensor, if any."""
        return "docker_{}_{}".format(self._name, self._var_name)

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._var_icon

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._var_unit

    def update(self):
        """Get the latest data for the states."""
        stats = self._thread.stats()
        if self._var_id == CONTAINER_MONITOR_STATUS:
            self._state                         = stats.get('status', None)
        elif self._var_id == CONTAINER_MONITOR_MEMORY_USAGE:
            self._state                         = stats.get('memory_usage', None)
        elif self._var_id == CONTAINER_MONITOR_CPU_PERCENTAGE:
            self._state                         = stats.get('cpu_percent', None)
            if 'cpu' in stats:
                self._attributes[ATTR_ONLINE_CPUS]  = stats['cpu'].get('online_cpus', None)
        elif self._var_id == CONTAINER_MONITOR_MEMORY_PERCENTAGE:
            self._state                         = stats.get('memory_percent', None)
        # Network
        elif self._var_id == CONTAINER_MONITOR_NETWORK_UP:
            self._state                         = round(stats.get('network_up', None) / 1024.0, PRECISION)
        elif self._var_id == CONTAINER_MONITOR_NETWORK_DOWN:
            self._state                         = round(stats.get('network_down', None) / 1024.0, PRECISION)

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes