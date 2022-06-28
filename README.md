# Replacements

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/carlosposse/Replacements)](https://github.com/carlosposse/Replacements/releases)
![GitHub Release Date](https://img.shields.io/github/release-date/carlosposse/Replacements)
[![GitHub](https://img.shields.io/github/license/carlosposse/Replacements)](LICENSE)

[![Maintenance](https://img.shields.io/badge/Maintained%3F-Yes-brightgreen.svg)](https://github.com/carlosposse/Replacements/graphs/commit-activity)
[![GitHub issues](https://img.shields.io/github/issues/carlosposse/Replacements)](https://github.com/carlosposse/Replacements/issues)

The `Replacements` component is a Home Assistant custom sensor which counts down to a regular interval action, such as replacing the filter on a cat fountain or the battery on the smoke detectors. The sensor can be configured in interval of days or interval of weeks. You can also configure the number of days or weeks that qualify the replacement should happen soon.

## Table of Contents

* [Installation](#installation)
  * [Manual Installation](#manual-installation)
  * [Installation via HACS](#installation-via-hacs)
* [Configuration](#configuration)
  * [Configuration Parameters](#configuration-parameters)
* [State and Attributes](#state-and-attributes)
  * [State](#state)
  * [Attributes](#attributes)
  * [Notes about unit of measurement](#notes-about-unit-of-measurement)

## Installation

### MANUAL INSTALLATION

1. Download the `replacements.zip` file from the
   [latest release](https://github.com/carlosposse/Replacements/releases/latest).
2. Unpack the release and copy the `custom_components/replacements` directory
   into the `custom_components` directory of your Home Assistant
   installation.
3. Configure the `replacements` sensor.
4. Restart Home Assistant.

### INSTALLATION VIA HACS

1. Ensure that [HACS](https://custom-components.github.io/hacs/) is installed.
2. Search for and install the "Replacements" integration.
3. Configure the `replacements` sensor.
4. Restart Home Assistant.


## Configuration

Go to `Configuration`/`Devices & Services`, click on the `+ ADD INTEGRATION` button, select `Replacements` and configure the integration.

The configuration happens in a single step. The `add another` box can be checked to add more replacements.

The configuration via `configuration.yaml` is not used.


### CONFIGURATION PARAMETERS

|Parameter |Optional|Description
|:----------|----------|------------
| `name` | Yes | Sensor friendly name
| `prefix` | Yes | Sensor entity prefix
| `days_interval` | Either `days_interval` or `weeks_interval` MUST be included | number of days between each replacement
| `weeks_interval` | Either `days_interval` or `weeks_interval` MUST be included | number of weeks between each replacement
| `soon_interval` | Yes | Days/weeks in advance to display the icon defined in `icon_soon`. It will be used as days if `days_interval` is used, or as weeks if `weeks_interval` is used. **Default**: 1
| `unit_of_measurement` | Yes | Your choice of label N.B. The sensor always returns Days, but this option allows you to express this in the language of your choice without needing a customization
| `icon_normal` | Yes | Default icon **Default**:  `mdi:calendar-blank`
| `icon_soon` | Yes | Icon if the replacement is 'soon' **Default**: `mdi:calendar`
| `icon_today` | Yes | Icon if the replacement is today **Default**: `mdi:calendar-star`
| `icon_expired` | Yes | Icon if the replacement is already due **Default**: `mdi:calendar-remove`
| `add_another` | Yes | Repeat the configuration for a new sensor

## State and Attributes

### State

* The number of days remaining to the next occurrence, or days elapsed since the action was due.

### Attributes

* date: the date of the next occurrence
* stock: the existing stock, i.e., the number of replacements parts available
* unit_of_measurement: 'Days' By default, this is displayed after the state. _this is NOT translate-able.  See below for work-around_

### Notes about unit of measurement

Unit_of_measurement is *not* translate-able.
You can, however, change the text for unit of measurement in the configuration.  NB the sensor will always report in days, this just allows you to represent this in your own language.

## Services

### replacements.new_date

Set a new next date for replacement. It will replace the replacement date even if the interval is higher than what is configured.

| Attribute | Description
|:----------|------------
| `entity_id` | The replacement entity id (e.g. `sensor.replace_car_door_battery`)
| `new_date` | The new replacement date (e.g. `2022-12-23`)


### replacements.new_stock

Set the new number of available units for replacement. It will set the `stock` attribute to the provided value, as long as it is not negative.

| Attribute | Description
|:----------|------------
| `entity_id` | The replacement entity id (e.g. `sensor.replace_car_door_battery`)
| `stock` | The new number of replacements units (e.g. `10`)

### replacements.replace_action

Signal a replacement action, i.e., the replacement has been performed today. It will reduce the stock by 1, if above 0, and set the new replacement date as `today + configured interval`.

| Attribute | Description
|:----------|------------
| `entity_id` | The replacement entity id (e.g. `sensor.replace_car_door_battery`)
