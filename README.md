# Home-Assistant Custom Components

Custom components for home-assistant (http://www.home-assistant.io)

Part of small a POC, currently I am too lazy to integrate into upstream at the moment.

## Climate/Toon Thermostat component

NOTE: This component only works with rooted Toon devices.

More information can be found here: [Eneco Toon as Domotica controller](http://www.domoticaforum.eu/viewforum.php?f=87)

It reads Toon's Mode, Current Temperature and it's Setpoint.
You can also control the thermostat Mode and Setpoint (target temperature)

### Install

Copy file climate/toon.py to your ha_config_dir/custom-components/climate directory.

Example of the Configuration:

```
configuration.yaml

climate:
  - platform: toon
    name: <Name of your Toon> (default = 'Toon Thermostat')
    host: <IP address of your Toon>
    port: <Port used by your Toon> (default is 10080)
    scan_interval: 10
```

### Screenshot

![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/toon.png "Screenshot")


## Toon Smart Meter component

NOTE: This component only works with rooted Toon devices.

It reads Smart Meter data from your Toon, gathered by the meteradapter.

### Install

Copy file sensor/toon_smartmeter.py to your ha_config_dir/custom-components/sensor directory.

Example of the Configuration:

```
configuration.yaml

sensor:
  - platform: toon_smartmeter
    host: <IP address of your Toon>
    port: <Port used by your Toon> (default is 10080)
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

The resources section tells the component which values to gather and display, you can leave out the prod values if your don't generate power.

![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/toon-smartmeter-badges.png "Toon SmartMeter Badges")

If you want them grouped instead of having the separate sensor badges, you can use this in your groups.yaml:

```
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

### Screenshot

![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/toon-smartmeter.png "Screenshot Toon SmartMeter")


## SolarPortal component

There are several solarpower portals storing you power generation data using the same api. So you can query the information uploaded by your solarpanels.
I have a Omnik inverted and so I'm using it with omnikportal

### Install

Copy file sensor/solarportal.py to your ha_config_dir/custom-components/sensor directory.

Example of the Configuration:

```
configuration.yaml

sensor:
  - platform: solarportal
    host: www.omnikportal.com
    port: 10000
    username: <Your portal username>
    password: <Your portal password>
    scan_interval: 30
    resources:
      - actualpower
      - energytoday
      - energytotal
      - incometoday
      - incometotal
```

Supported portals for host entry:
..* www.omnikportal.com
..* www.ginlongmonitoring.com
..* log.trannergy.com
..* www.solarmanpv.com


The resources section tells the component which values to display.

![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/solarportal-badges.png "SolarPortal Badges")

If you want them grouped instead of having the separate sensor badges, you can use this in your groups.yaml:

```
OmnikPortal Solar:
  - sensor.solar_actual_power
  - sensor.solar_energy_today
  - sensor.solar_energy_total
  - sensor.solar_income_today
  - sensor.solar_income_total
```

![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/solarportal.png "Screenshot SolarPortal")

### Some graphs

![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/solarportal-graph.png "Graph Actual Power")
![alt text](https://raw.githubusercontent.com/cyberjunky/home-assistant-custom-components/master/screenshots/solarportal-graph-income.png "Graph Total Income")

