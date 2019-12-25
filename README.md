[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.me/cyberjunkynl/)

# My Home-Assistant Custom Components

Some of my custom components for home-assistant. (http://www.home-assistant.io)

## Moved to it's own repository and made HACS compatible:
  * [TOON Thermostat Climate Component](https://github.com/cyberjunky/home-assistant-toon_climate)
  * [TOON Smart Meter Sensor Component](https://github.com/cyberjunky/home-assistant-toon_smartmeter)
  * [TOON Boiler Status Sensor Component](https://github.com/cyberjunky/home-assistant-toon_boilerstatus)
  * [P2000 Emergency Services Component](https://github.com/cyberjunky/home-assistant-p2000)
  * [Arpscan Device Tracker Component](https://github.com/cyberjunky/home-assistant-arpscan_tracker)
  * [Plugwise Component](https://github.com/cyberjunky/home-assistant-plugwise)
  * [HVC Groep Garbage Collect Sensor Component](https://github.com/cyberjunky/home-assistant-hvcgroep)
  * [TheThingsNetwork Gateway Status Sensor Component](https://github.com/cyberjunky/home-assistant-ttn_gateway)
  * [Google Fit Sensor Component](https://github.com/cyberjunky/home-assistant-google_fit)

## To be worked on:

  * [Fritzbox_callmonitor Notification example](#fritzbox_callmonitor-notification-example)
  * [Remarks component](#remarks-component)
  * [Volkswagen Carnet component](#volkswagen-carnet-component)
  
## Deprecated:

  * [SolarPortal sensor component](#solarportal-sensor-component)
  * [Battefield1 Stats component](#battefield1-stats-component)

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


## Battefield1 Stats component

NOTE: Network is shutdown.

> As of October 27, 2019 the P-Stats Network has shutdown.


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
