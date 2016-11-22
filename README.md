# Home-Assistant Custom Components

Some of my custom components for home-assistant (http://www.home-assistant.io)

Part of a small Proof of Concept, currently I am too lazy to integrate into upstream at the moment.
Still learning to program in python3 and how to make home-assistant components.

## Toon Thermostat climate component

NOTE: This component only works with rooted Toon devices.
Toon's are Thermostats sold by Eneco a Dutch energy company.

More information about preparing for usage with this component can be found here:
[Eneco Toon as Domotica controller](http://www.domoticaforum.eu/viewforum.php?f=87)

This component reads the Thermostat Mode, Current Temperature and it's Setpoint.
You can also control the thermostat Mode and Setpoint (target temperature)

### Installation

- Copy file climate/toon.py to your ha_config_dir/custom-components/climate directory.
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

- **name** (*Optional*): Name of the device (default = 'Toon Thermostat')
- **host** (*Required*): The hostname or IP address on which the Toon can be reached
- **port** (*Optional*): Port used by your Toon (default = 10080)
- **scan_interval** (*Optional*): Number of seconds between polls (default = 10)

### Screenshot

![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/toon.png "Screenshot")

## Toon Smart Meter sensor component

NOTE: This component only works with rooted Toon devices.

It reads Smart Meter data from your Toon, gathered by the meteradapter.

### Installation

- Copy file sensor/toon_smartmeter.py to your ha_config_dir/custom-components/sensor directory.
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

- **host** (*Required*): The hostname or IP address on which the Toon can be reached
- **port** (*Optional*): Port used by your Toon (default = 10080)
- **scan_interval** (*Optional*): Number of seconds between polls (default = 10)
- **resources** (*Required*): This section tells the component which values to display, you can leave out the prod values if your don't generate power.

![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/toon-smartmeter-badges.png "Toon SmartMeter Badges")

If you want them grouped instead of having the separate sensor badges, you can use this in your `groups.yaml`:

```yaml
Smart meter:
  - sensor.p1_gas_used_last_hour
  - sensor.p1_gas_used_cnt
  - sensor.p1_power_prod_low
  - sensor.p1_power_prod_high
  - sensor.p1_power_prod_cnt_low
  - sensor.p1_power_prod_cnt_high
  - sensor.p1_power_use_cnt_low
  - sensor.p1_power_use_cnt_high
  - sensor.p1_power_use_low
  - sensor.p1_power_use_high
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

- Copy file sensor/solarportal.py to your ha_config_dir/custom-components/sensor directory.
- Configure with config below
- Restart Home-Assistant.

## Usage
To use this component in your installation, add the following to your `configuration.yaml` file:

```yaml
#Example configuration.yaml entry

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

- **host** (*Required*): The website url of the portal to query for the list below
 * [www.omnikportal.com](http://www.omnikportal.com)
 * [www.ginlongmonitoring.com](http://www.ginlongmonitoring.com)
 * [log.trannergy.com](http://log.trannergy.com)
 * [www.solarmanpv.com](http://www.solarmanpv.com)
- **port** (*Optional*): Port in use by the portal api (default = 10000)
- **username** (*Required*): The login name for the website, normally this is an email address
- **password** (*Required*): Your password for the website
- **scan_interval** (*Optional*): Number of seconds between polls (default = 30)
- **resources** (*Required*): This section tells the component which values to display

![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/solarportal-badges.png "SolarPortal Badges")

If you want them grouped instead of having the separate sensor badges, you can use this in your `groups.yaml`:

```yaml
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

- Copy file sensor/bf1stats.py to your ha_config_dir/custom-components/sensor directory.
- Configure with config below
- Restart Home-Assistant.

## Usage
To use this component in your installation, add the following to your `configuration.yaml` file:

```yaml
#Example configuration.yaml entry

sensor:
  - platform: bf1stats
```

Configuration variables:

- **None**

![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/bf1stats-badge.png "BF1Stats Badge")
![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/bf1stats-graph.png "BF1Stats Graph")


## TODO
- Implement better input checks.
- Add more error handling.
- Make the components work async.
