# Home-Assistant Custom Components

Custom components for home-assistant (http://www.home-assistant.io)
Part of small a POC, currently I am too lazy to integrate into upstream at the moment.

## Climate/Toon Thermostat component

NOTE: This component only works with rooted Toon devices.
More information can be found here: [Eneco Toon as Domotica controller](http://www.domoticaforum.eu/viewforum.php?f=87)
It reads Toon's Mode, Current Temperature and it's Setpoint.
You can also control the thermostat Mode and Setpoint (target temperature)

### Install

Copy climate/toon.py into ha_config_dir/custom-components/climate

Configuration:

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

![alt text](https://github.com/cyberjunky/ha-custom-components/screenshots/toon.png "Screenshot"
