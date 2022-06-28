# Replacements

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/carlosposse/Replacements)](https://github.com/carlosposse/Replacements/releases)
![GitHub Release Date](https://img.shields.io/github/release-date/carlosposse/Replacements)
[![GitHub](https://img.shields.io/github/license/carlosposse/Replacements)](LICENSE)

[![Maintenance](https://img.shields.io/badge/Maintained%3F-Yes-brightgreen.svg)](https://github.com/carlosposse/Replacements/graphs/commit-activity)
[![GitHub issues](https://img.shields.io/github/issues/carlosposse/Replacements)](https://github.com/carlosposse/Replacements/issues)

The `Replacements` component is a Home Assistant custom sensor which counts down to a regular interval action, such as replacing the filter on a cat fountain or the battery on the smoke detectors. The sensor can be configured in interval of days or interval of weeks. You can also configure the number of days or weeks that qualify the replacement should happen soon.

## Configuration

Go to `Configuration`/`Devices & Services`, click on the `+ ADD INTEGRATION` button, select `Replacements` and configure the integration.

The configuration via `configuration.yaml` is not used.

For the configuration documentation check the <a href="https://github.com/carlosposse/Replacements/blob/master/README.md">repository</a> file

## State and Attributes

The state is the number of days remaining to the next occurrence, or days elapsed since the action was due.

Attributes:

* date: the date of the next occurrence
* stock: the existing stock, i.e., the number of replacements parts available
* unit_of_measurement: 'Days' By default, this is displayed after the state. _this is NOT translate-able.  See below for work-around_

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
