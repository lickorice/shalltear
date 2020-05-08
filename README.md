# Shalltear
This is the current updated repository of Shalltear.

## Installation
To install dependencies of the bot, you may opt to [activate a virtual environment](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/) before doing so.

Make sure to open the terminal in the project's root directory, then, install the dependencies in `requirements.txt` like so:

```bash
$ pip install -r requirements.txt
```

### Running on Windows / Git Bash

```cmd
> py - 3 run.py
```

### Running on Linux

```bash
$ python3 run.py
```

## Changelog
### `v0.0.3b`
- **The Economy simulation engine has been revamped.** Every time the market refreshes, the demand is also recalculated. At full demand, the current sale price will be at **double**, and at zero demand, the current sale price will be at **half**.
    - For example, if Turnip sells for 0.75 gil, at full demand (freshly refreshed market) it will be sold at **1.50 gil**, however, at zero demand, Turnip will sell for **0.375 gil**.
- `s!plantprices` message now shows time before next interval.
- `s!farm` now sends an Embed.
- `s!plantprices` now sends an Embed.
- Add crop shorthands, such as `TRNP` for Turnip, `PMKN` for Pumpkin, etc. These shorthands can be used to refer to the crops in command usage.
- Add `s!setfarmname` command, which changes the farm's name if you pay a set price (default is 100 gil).
### `v0.0.2b`
- Introduce new plants Potato, Pumpkin, and Grapes.
- Introduce scaled plot purchasing.
- Add PriceLog object that logs the hourly changes in Plant prices.
- Allow `farmplant` command to plant on multiple plots at once.
- Fix `help` command.
- Add `info`, `kill`, commands.
- Balance existing Plant prices.
### `v0.0.1b`
- Add base functionalities for Admin, Core, Economy, and Farm cogs.
- Introduce plants Turnip, Rice, Strawberry, and Watermelon.