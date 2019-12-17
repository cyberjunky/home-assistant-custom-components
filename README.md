[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)  [![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/cyberjunkynl/)

# My Home-Assistant Custom Components

Some of my custom components for home-assistant. (http://www.home-assistant.io)

Component Overview
------------------
  * [TOON Thermostat climate component](#toon-thermostat-climate-component)
  * [TOON Smart Meter sensor component](#toon-smart-meter-sensor-component)
  * [TOON Boiler Status sensor component](#toon-boiler-status-sensor-component)
  * [SolarPortal sensor component](#solarportal-sensor-component)
  * [Battefield1 Stats component](#battefield1-stats-component)
  * [P2000 Emergency Services component](#p2000-emergency-services-component)
  * [Fritzbox_callmonitor Notification example](#fritzbox_callmonitor-notification-example)
  * [Remarks component](#remarks-component)
  * [Arpscan Device Tracker component](#arpscan-device-tracker-component)
  * [Plugwise component](#plugwise-component)
  * [TheThingsNetwork Gateway status component](#thethingsnetwork-gateway-status-component)
  * [HVCGroep Garbage Collect sensor component](#hvcgroep-garbage-collect-sensor-component)
  * [Volkswagen Carnet component](#volkswagen-carnet-component)
 
## TOON Thermostat climate component
This component provides a climate device for rooted TOON thermostats.
It lives in it's own HACS compatible repository now.
https://github.com/cyberjunky/home-assistant-toon_climate


## TOON Smart Meter sensor component

NOTE: This component only works with rooted TOON devices.

It reads Smart Meter data from your TOON, gathered by the meteradapter.

### Installation

- Copy directory `toon_smartmeter` to your `<config dir>/custom_components` directory.
- Configure with config below.
- Restart Home-Assistant.

### Usage
To use this component in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry

sensor:
  - platform: toon_smartmeter
    host: IP_ADDRESS
    port: 10080
    scan_interval: 10
    resources:
      - gasused
      - gasusedcnt
      - elecusageflowpulse
      - elecusagecntpulse
      - elecusageflowlow
      - elecusagecntlow
      - elecusageflowhigh
      - elecusagecnthigh
      - elecprodflowlow
      - elecprodcntlow
      - elecprodflowhigh
      - elecprodcnthigh
      - elecsolar
      - elecsolarcnt
      - heat
```

Configuration variables:

- **host** (*Required*): The hostname or IP address on which the TOON can be reached.
- **port** (*Optional*): Port used by your TOON. (default = 10080)
- **scan_interval** (*Optional*): Number of seconds between polls. (default = 10)
- **resources** (*Required*): This section tells the component which values to display, you can leave out the elecprod values if your don't generate power and the elecusage*pulse types if you use the P1 connection.

![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/toon-smartmeter-badges.png "Toon SmartMeter Badges")

If you want them grouped instead of having the separate sensor badges, you can use this in your `groups.yaml`:

```yaml
# Example groups.yaml entry

Smart meter:
  - sensor.toon_gas_used_last_hour
  - sensor.toon_gas_used_cnt
  - sensor.toon_power_use_cnt
  - sensor.toon_power_use
  - sensor.toon_p1_power_prod_low
  - sensor.toon_p1_power_prod_high
  - sensor.toon_p1_power_prod_cnt_low
  - sensor.toon_p1_power_prod_cnt_high
  - sensor.toon_p1_power_use_cnt_pulse
  - sensor.toon_p1_power_use_cnt_low
  - sensor.toon_p1_power_use_cnt_high
  - sensor.toon_p1_power_use_low
  - sensor.toon_p1_power_use_high
  - sensor.toon_p1_power_solar
  - sensor.toon_p1_power_solar_cnt
  - sensor.toon_p1_heat
```

### Screenshots

![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/toon-smartmeter.png "Screenshot Toon SmartMeter")
![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/toon-smartmeter-graph-gasused.png "Graph Gas Used")
![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/toon-smartmeter-graph-poweruselow.png "Graph Power Use Low")


## TOON Boiler Status sensor component

NOTE: This component only works with rooted TOON devices. And installed BoilerStatus app via ToonStore.  

It reads OpenTherm Boiler data from your TOON, gathered by the thermostat adapter.

### Installation

- Copy directory `toon_boilerstatus` to your `<config dir>/custom_components` directory.
- Configure with config below.
- Restart Home-Assistant.

### Usage
To use this component in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry

sensor:
  - platform: toon_boilerstatus
    host: IP_ADDRESS
    port: 10080
    scan_interval: 10
    resources:
      - boilersetpoint
      - boilerintemp
      - boilerouttemp
      - boilerpressure
      - boilermodulationlevel
      - roomtemp
      - roomtempsetpoint
```

Configuration variables:

- **host** (*Required*): The hostname or IP address on which the TOON can be reached.
- **port** (*Optional*): Port used by your TOON. (default = 10080)
- **scan_interval** (*Optional*): Number of seconds between polls. (default = 10)
- **resources** (*Required*): This section tells the component which values to display and monitor.

By default the values are displayed as badges.

If you want them grouped instead of having the separate sensor badges, you can use this in your `groups.yaml`:

```yaml
# Example groups.yaml entry

Boiler Status:
  - sensor.toon_boiler_intemp
  - sensor.toon_boiler_outtemp
  - sensor.toon_boiler_setpoint
  - sensor.toon_boiler_pressure
  - sensor.toon_boiler_modulation
  - sensor.toon_room_temp
  - sensor.toon_room_temp_setpoint
```

### Screenshots

![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/toon-boilerstatus.png "Screenshot Toon Boiler Status")


## SolarPortal sensor component

NOTE: API seem to have changed, need new reverse engineering!

> Dear Customers,

> Omnik old version APP has removed,and no running anymore. Please 
> download new APP version (Omnik Portal) from the App Store.

> If you use Android system, please go to Google play download:
> "Omnik Portal" 
> https://play.google.com/store/apps/details?id=com.jialeinfo.omniksolar&hl=en

> If you use iOS system, please go to iOS App store download:
> "Omnik Portal" 
> https://itunes.apple.com/cn/app/id1246117091

> Thank you so much for your notice.

> Omnik Team

There are several solarpower portals storing you power generation data using the same API.
You can query the information uploaded by your solarpanels.
I have a Omnik inverter and so I'm using it with omnikportal, only one I tested it with.

### Installation

- Copy directory `solarportal` to your `<config dir>/custom_components` directory.
- Configure with config below.
- Restart Home-Assistant.

### Usage
To use this component in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry

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
```

Configuration variables:

- **host** (*Required*): The website url of the portal to query for the list below.
 * [www.omnikportal.com](http://www.omnikportal.com)
 * [www.ginlongmonitoring.com](http://www.ginlongmonitoring.com)
 * [log.trannergy.com](http://log.trannergy.com)
 * [www.solarmanpv.com](http://www.solarmanpv.com)
- **port** (*Optional*): Port in use by the portal API. (default = 10000)
- **username** (*Required*): The login name for the website, normally this is an email address.
- **password** (*Required*): Your password for the website.
- **scan_interval** (*Optional*): Number of seconds between polls. (default = 30)
- **resources** (*Required*): This section tells the component which values to display.

![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/solarportal-badges.png "SolarPortal Badges")

If you want them grouped instead of having the separate sensor badges, you can use this in your `groups.yaml`:

```yaml
# Example groups.yaml entry

OmnikPortal Solar:
  - sensor.solar_actual_power
  - sensor.solar_energy_today
  - sensor.solar_energy_total
  - sensor.solar_income_today
  - sensor.solar_income_total
```

### Screenshots

![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/solarportal.png "Screenshot SolarPortal")

![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/solarportal-graph.png "Graph Actual Power")
![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/solarportal-graph-income.png "Graph Total Income")


## Battefield1 Stats component

I'm playing BF1 sometimes, and notices there was an bf1stats api available, so I wrote a small component to query and log the number of online players.
I could have done this with a few rest sensor type sensors, but I didn't find out a way to calculate a total count this way, from all the different platform counters.
So this is what this component does and combine them into one sensor.

### Installation

- Copy directory `bf1stats` to your `<config dir>/custom_components` directory.
- Configure with config below.
- Restart Home-Assistant.

### Usage
To use this component in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry

sensor:
  - platform: bf1stats
```

Configuration variables:

- **None**

![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/bf1stats-badge.png "BF1Stats Badge")
![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/bf1stats-graph.png "BF1Stats Graph")


## P2000 Emergency Services component
This component tracks P2000 emergency events in The Netherlands.
It lives in it's own HACS compatible repository now.
https://github.com/cyberjunky/home-assistant-p2000


## Fritzbox_callmonitor Notification example

This is not a new component but an example automation config useable together with the fritzbox_callmonitor component.
The example below will generate several messages depending on status of the event.

```yaml
# Example configuration.yaml entry

- platform: fritzbox_callmonitor
```

```yaml
# Example automation.yaml entry

- alias: 'Phone Status'
  trigger:
    platform: state
    entity_id: sensor.phone
  action:
    - service: notify.pushover
      data:
        title: "Phone"
        message: >
          {% if is_state( "sensor.phone", "ringing" ) %}
            {% if states.sensor.phone.attributes.from %}
              Ringing on incoming call from {{ states.sensor.phone.attributes.from }}.
            {% else %}
              Ringing on incoming call from an Unknown or Hidden number.
            {% endif %}
          {%-elif is_state( "sensor.phone", "talking" ) %}
            Call answered.
          {%-elif is_state( "sensor.phone", "dialing" ) %}
            Calling {{ states.sensor.phone.attributes.to }} with {{ states.sensor.phone.attributes.device }}.
          {%-elif is_state( "sensor.phone", "idle" ) %}
            {% if states.sensor.phone.attributes.duration | int > 59 %}
              Phone call ended, duration was {{ (float(states.sensor.phone.attributes.duration) / 60) | round }} Minute(s).
            {% else %}
              Phone call ended, duration was {{ states.sensor.phone.attributes.duration }} Second(s).
            {% endif %}
          {% endif %}
```


## Remarks component

This component fetches random tags from files to be tweeted.
The data files are taken from misterhouse, so al courtesy goes to that project.
Currently there are two types of remarks implemented, random daily one taken from file specified in config.
And outside temperature based.

### Installation

- Copy file `remarks.py` to your `<config dir>/custom_components` directory.
- Copy the data directory `remarks` to your `<config dir>` directory.
- Configure with config below.
- Restart Home-Assistant.

### Usage
To use this component in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry

remarks:
   file: 1100tags.txt
   hour: 9
   minute: 0
   outside_temp_sensor: sensor.pws_temp_c
   cold_threshold: 5
   freeze_threshold: -5
   temp_hour: 6
   temp_minute: 30
```

Configuration variables:

- **file** (*Optional*): The file we want to pick a random tag from, one from the `remarks` directory. (default = 1100tags.txt)
- **hour** (*Optional*): The hour on which we want to generate a random tag. (default = 9)
- **minute** (*Optional*): The minute on which we want to generate a random tag. (default = 0)
- **outside_temp_sensor** (*Optional*): Sensor device to use to get the outside temperature. (default = sensor.pws_temp_c)
- **cold_threshold** (*Optional*): Below this temperature a tag will be picked from the `list_temp_below_20.txt`. (default = 5)
- **freeze_threshold** (*Optional*): Below this temperature a tag will be picked from the file `list_temp_below_0.txt`. (default = -5)
- **temp_hour** (*Optional*): The hour on which we want to generate a temperature remark if it is below thresholds. (default = 6)
- **temp_minute** (*Optional*): The minute on which we want to generate a temperature remark. (default = 30)

Now for both tags an event will be fired.

You can trigger on this with automation rules.
For example you can send them as tweets, to do so place this in your `automation.yaml`

```yaml
# Example automation.yaml entry

- alias: Tweeting Remarks
  trigger:
    platform: event
    event_type: remarks
  action:
  - service_template: notify.twitter
    data_template:
      message: "{{ trigger.event.data.text }}"
```


## Arpscan Device Tracker component

This component tracks devices using the arp-scan command, it's very fast, and reasonably accurate.
It lives in it's own HACS compatible repository now.
https://github.com/cyberjunky/home-assistant-arpscan_tracker


## Plugwise component

This component can read values from and control Plugwise circles and plugs.
It lives in it's own HACS compatible repository now.
https://github.com/cyberjunky/home-assistant-plugwise


## TheThingsNetwork Gateway status component

This component can read status values from a local TTN Gateway.

### Installation

- Copy directory `ttn_gateway` to your `<config dir>/custom-components` directory.
- Configure with config below.
- Restart Home-Assistant.

### Usage
To use this component in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry

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
```

Configuration variables:

- **host** (*Required*): The IP address of the gateway you want to monitor.
- **scan_interval** (*Optional*): Number of seconds between polls. (default = 30)
- **resources** (*Required*): This section tells the component which values to monitor.

If you want them grouped instead of having the separate sensor badges, you can use this in your `groups.yaml`:

```yaml
# Example groups.yaml entry

TTN Gateway:
  - sensor.ttn_gw_hardware_version
  - sensor.ttn_gw_bootloader_version
  - sensor.ttn_gw_firmware_version
  - sensor.ttn_gw_uptime
  - sensor.ttn_gw_connected
  - sensor.ttn_gw_interface
  - sensor.ttn_gw_gateway
  - sensor.ttn_gw_ssid
  - sensor.ttn_gw_activation_locked
  - sensor.ttn_gw_configured
  - sensor.ttn_gw_region
  - sensor.ttn_gw_gateway_card
  - sensor.ttn_gw_broker_connected
  - sensor.ttn_gw_packets_up
  - sensor.ttn_gw_packets_down
  - sensor.ttn_gw_external_storage
```

### Screenshots

![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/ttn-gw-badges.png "Screenshot TTN Gateway Badges")
![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/ttn-gw-status.png "Screenshot TTN Gateway Status")


## HVCGroep Garbage Collect sensor component

Gets garbage pickup dates straight from HVC Groep's rest API.
It lives in it's own HACS compatible repository now.
https://github.com/cyberjunky/home-assistant-hvcgroep


## Volkswagen Carnet component

Cloned from https://github.com/robinostlund/homeassistant-volkswagencarnet

So all credits to Robin Ostlund.

I stripped out non supported stuff to get it to work with my VW T-ROC.

This also needs a modified volkswagencarnet python module!

```yaml
# Example configuration.yaml entry

volkswagencarnet:
    username: your@email.address
    password: yourpassword
    update_interval: 
      minutes: 5
    resources:
      - last_connected
      - position
      - distance
      - fuel_level
      - service_inspection
      - oil_inspection
      - parking_light
      - doors_locked
      - trunk_locked
      - combined_range
```

Configuration variables:

- **username** (*Required*): Your email address for carnet portal.
- **password** (*Required*): Your password for carnet portal.
- **minutes** (*Required*): Update every x minutes, minimum is 3.
- **resources** (*Required*): Values to fetch.

## TODO for most of above components
- Make the components work async.
