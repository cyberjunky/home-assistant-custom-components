# Home-Assistant Custom Components

Some of my custom components for home-assistant. (http://www.home-assistant.io)

Part of a small Proof of Concept, currently I am too lazy to integrate into upstream at the moment.
Still learning to program in python3 and how to make home-assistant components.

## Toon Thermostat climate component

NOTE: This component only works with rooted Toon devices.
Toon's are Thermostats sold by Eneco a Dutch energy company.

More information about preparing for usage with this component can be found here:
[Eneco Toon as Domotica controller](http://www.domoticaforum.eu/viewforum.php?f=87)

This component reads the Thermostat Mode, Current Temperature and it's Setpoint.
You can also control the thermostat Mode and Setpoint. (target temperature)

### Installation

- Copy file `climate/toon.py` to your `ha_config_dir/custom_components/climate` directory.
- Configure with config below.
- Restart Home-Assistant.

## Usage
To use this component in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry

climate:
  - platform: toon
    name: Toon Thermostat
    host: IP_ADDRESS
    port: 10080
    scan_interval: 10
```

Configuration variables:

- **name** (*Optional*): Name of the device. (default = 'Toon Thermostat')
- **host** (*Required*): The hostname or IP address on which the Toon can be reached.
- **port** (*Optional*): Port used by your Toon. (default = 10080)
- **scan_interval** (*Optional*): Number of seconds between polls. (default = 60)

### Screenshot

![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/toon.png "Screenshot")

## Toon Smart Meter sensor component

NOTE: This component only works with rooted Toon devices.

It reads Smart Meter data from your Toon, gathered by the meteradapter.

### Installation

- Copy file `sensor/toon_smartmeter.py`s to your `ha_config_dir/custom_components/sensor` directory.
- Configure with config below.
- Restart Home-Assistant.

## Usage
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
```

Configuration variables:

- **host** (*Required*): The hostname or IP address on which the Toon can be reached.
- **port** (*Optional*): Port used by your Toon. (default = 10080)
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
```

### Screenshots

![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/toon-smartmeter.png "Screenshot Toon SmartMeter")
![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/toon-smartmeter-graph-gasused.png "Graph Gas Used")
![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/toon-smartmeter-graph-poweruselow.png "Graph Power Use Low")


## SolarPortal sensor component

There are several solarpower portals storing you power generation data using the same API.
You can query the information uploaded by your solarpanels.
I have a Omnik inverter and so I'm using it with omnikportal, only one I tested it with.

### Installation

- Copy file `sensor/solarportal.py` to your `ha_config_dir/custom_components/sensor` directory.
- Configure with config below.
- Restart Home-Assistant.

## Usage
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

- Copy file `sensor/bf1stats.py` to your `ha_config_dir/custom_components/sensor` directory.
- Configure with config below.
- Restart Home-Assistant.

## Usage
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

This component queries the portal http://feeds.livep2000.nl every interval minutes, and check it's output against the parameters set in the config.
It's only based on Dutch services.
When matched service calls are found an event is triggered, which you can use in automation rule. (see example below)

 
### Installation
- Install required python libraries

```
$ pip3 install gpxpy
$ pip3 install feedparser
```
- Copy file `p2000.py` to your `ha_config_dir/custom_components` directory.
- Configure with config below.
- Restart Home-Assistant.

## Usage
To use this component in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry

p2000:
    regios: 18
    disciplines: 1,2,3
    distance: 5000
    interval: 30
```

Configuration variables:

- **regios** (*Required*): You have to specify at least one, if you want more seperate them by commas.
 * 1 = Groningen
 * 2 = Friesland
 * 3 = Drenthe
 * 4 = IJsselland
 * 5 = Twente
 * 6 = Noord en Oost Gelderland
 * 7 = Gelderland Midden
 * 8 = Gelderland Zuid
 * 9 = Utrecht
 * 10 = Noord Holland Noord
 * 11 = Zaanstreek-Waterland
 * 12 = Kennemerland
 * 13 = Amsterdam-Amstelland
 * 14 = Gooi en Vechtstreek
 * 15 = Haaglanden
 * 16 = Hollands Midden
 * 17 = Rotterdam Rijnmond
 * 18 = Zuid Holland Zuid
 * 19 = Zeeland
 * 20 = Midden- en West-Brabant
 * 21 = Brabant Noord
 * 22 = Brabant Zuid en Oost
 * 23 = Limburg Noord
 * 24 = Limburg Zuid
 * 25 = Flevoland
- **disciplines** (*Optional*): Disciplines to display, separate them by commas. (default = 1,2,3,4)
 * 1 = Brandweer
 * 2 = Ambulance
 * 3 = Politie
 * 4 = KNRM
- **distance** (*Optional*): Only display on calls within this range in meters, it uses the lat/lon from your home-assistant.conf file as center. (default = 5000)
- **interval** (*Optional*): Check every x minutes. (default = 5)

It triggers only on new messages, at a home-assistant restart, old messages are skipped.

You can use the triggered event to send a push notification like this:
```yaml
# Example automation.yaml entry

- alias: P2000 Notify
  trigger:
    platform: event
    event_type: p2000
  action:
  - service_template: notify.pushover
    data_template:
      title: "P2000"
      message: "{{ trigger.event.data.text }}"
```

### Screenshot

![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/p2000-notify.png "Screenshot")


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

- Copy file `remarks.py` to your `ha_config_dir/custom_components` directory.
- Copy the data directory `remarks` to your `ha_config_dir` directory.
- Configure with config below.
- Restart Home-Assistant.

## Usage
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


## arp-scan Device Tracker component

This component tracks devices using the arp-scan command, it's very fast, and reasonably accurate.

### Installation

- Copy file `device_tracker/arpscan_tracker.py` to your `ha_config_dir/custom_components/device_tracker` directory.
- Install the arp-scan command and set it's sticky bit, so it can be run as root.
```
$ sudo apt-get install arp-scan
$ sudo chmod +s /usr/bin/arp-scan
```
- Configure with config below.
- Restart Home-Assistant.

## Usage
To use this component in your installation, add the following to your `configuration.yaml` file:

```yaml
# Example configuration.yaml entry

device_tracker:
  - platform: arpscan_tracker
    interval_seconds: 15
    consider_home: 60
    track_new_devices: true
    exclude:
      - 192.168.178.1
      - 192.168.178.3
```

Configuration variables:

- **interval_seconds** (*Optional*) Seconds between each scan for new devices. (default = 12)
- **consider_home** (*Optional*): Seconds to marking device as 'not home' after not being seen (default = 180)
- **track_new_device** (*Optional*): If new discovered devices are tracked by default. (default = True)
- **exclude** (*Optional*): List of IP addresses to skip tracking for.
- **scan_options** (*Optional*): Configurable scan options for arp-scan. (default is `-l -g -t1 -q`)


## TODO
- Implement better input checks.
- Add more error handling.
- Make the components work async.
