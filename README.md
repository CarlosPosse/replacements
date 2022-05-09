# Replacements

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/carlosposse/Replacements)](https://github.com/carlosposse/Replacements/releases)
![GitHub Release Date](https://img.shields.io/github/release-date/carlosposse/Replacements)
[![GitHub](https://img.shields.io/github/license/carlosposse/Replacements)](LICENSE)

[![Maintenance](https://img.shields.io/badge/Maintained%3F-Yes-brightgreen.svg)](https://github.com/carlosposse/Replacements/graphs/commit-activity)
[![GitHub issues](https://img.shields.io/github/issues/carlosposse/Replacements)](https://github.com/carlosposse/Replacements/issues)

The 'replacements' component is a Home Assistant custom sensor which counts down to a regular interval action, such as replacing the filter on a cat fountain.

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
   [latest release](https://github.com/carlosposse/replacements/releases/latest).
2. Unpack the release and copy the `custom_components/replacements` directory
   into the `custom_components` directory of your Home Assistant
   installation.
3. Configure the `replacements` sensor.
4. Restart Home Assistant.

### INSTALLATION VIA HACS

1. Ensure that [HACS](https://custom-components.github.io/hacs/) is installed.
2. Search for and install the "replacements" integration.
3. Configure the `replacements` sensor.
4. Restart Home Assistant.

## Configuration

Replacements can be configured on the integrations menu or in configuration.yaml

### Config Flow

In Configuration/Integrations click on the + button, select Replacements and configure the options on the form.

### configuration.yaml

Add `replacements` sensor in your `configuration.yaml`. The following example adds two sensors - cat fountain filter replacement and heart pills buy!

```yaml
# Example configuration.yaml entry

replacements:
  sensors:
  - name: Cat fountain filter
    weeks_interval: 2
  - name: Heart pills
    days_interval: 16
```

### CONFIGURATION PARAMETERS

|Parameter |Optional|Description
|:----------|----------|------------
| `name` | No | Friendly name
|`days_interval` | Either `days_interval` or `weeks_interval` MUST be included | number of days between each replacement
|`weeks_interval` | Either `days_interval` or `weeks_interval` MUST be included | number of weeks between each replacement
| `unit_of_measurement` | Yes | Your choice of label N.B. The sensor always returns Days, but this option allows you to express this in the language of your choice without needing a customization
| `id_prefix` | Yes | Your choice of prefix for the entity_id **Default**: `replace_` NB. the entity_id cannot be changed from within the integration once it has been created.  You must either delete your entity and re-create it or manually rename the entity_id on the configuration -> entities page
| `days_as_soon` | Yes | Days in advance to display the icon defined in `icon_soon` **Default**: 3
| `icon_normal` | Yes | Default icon **Default**:  `mdi:calendar-blank`
| `icon_soon` | Yes | Icon if the replacement is 'soon' **Default**: `mdi:calendar`
| `icon_today` | Yes | Icon if the replacement is today **Default**: `mdi:calendar-star`
| `icon_expired` | Yes | Icon if the replacement is already due **Default**: `mdi:calendar-remove`

## State and Attributes

### State

* The number of days/weeks/months remaining to the next occurance, or days elapsed since the action was due.

### Attributes

* date: the date of the next occurence
* stock: the existing stock, i.e., the number of replacements parts available
* weeks_remaining: The number of weeks until the replacement action
* unit_of_measurement: 'Days' By default, this is displayed after the state. _this is NOT translate-able.  See below for work-around_

### Notes about unit of measurement

Unit_of_measurement is *not* translate-able.
You can, however, change the text for unit of measurement in the configuration.  NB the sensor will always report in days, this just allows you to represent this in your own language.
