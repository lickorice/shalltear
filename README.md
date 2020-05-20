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
### `v0.1.0b` (Items and Auction Update)
- **Add new prestige currency 💎 Materia which can only be obtained after resetting.** Materia can be used to purchase roles, items, etc.
- **Add new Farm Prestige system.** When max plots have been reached, you can do command `s!farmprestige` to fully reset your farm. When this happens, your **Farm Prestige level will increase**, and you will gain **1 💎 Materia** per **100 million gil** you have on-hand.
- **Add new Profile system.** `s!profile` will show your stats, including your 💎 Materia count, prestige levels, among others.
- Add command `s!declarebankruptcy` which would reset your current farm instance and gil balance (in case of farm failure).
- Plot system fully revamped and optimized.
- Miscellaneous administration tools:
    - Add manual backup command of the database.
    - Add automated midnight backup routine of the database.
### `v0.0.5b revised` (Quality of Life and Balancing updates)
- Introduce new plants Lettuce, Pineapple, Pepper, Mango, and Passionfruit.
- Buff longer term plants like Watermelon, Pumpkin, Grapes, Sugarcane, and Coconut.
- **Add plant price logging.** To view statistics of your crop, you can use the command `s!pstats <plant_name>`.
- Add comma separation in gil display.
- Add en-masse purchasing of plots and silos, through `s!plotbuy <plot_count>`, or `s!silobuy <silo_count>`. The same can be done with `s!plotprice` and `s!siloprice`, respectively.
- Add a hard limit to plots, which is currently set to `1000`. Further progression will be introduced in following updates.
### `v0.0.4b`
- Introduce new plants Wheat, Tomato, Sugarcane, Coconut, Banana, Lemon, and Hops.
- Adjust demand calculation system to consider past demand in factoring in the influence of the soon-to-be calculated demand.
- **Introduce a new crop storage system.** All farms will start with 100 storage, and each new storage upgrade will add an additional 100 storage to your farm. Storage upgrade prices scale (much like plot prices, but are more forgiving) as you purchase new upgrades.
- Add new commands `s!siloprice [s!silo$]` and `s!silobuy`, to check the price of your next storage upgrade and to buy it, respectively. `s!silobuy`, however, has a cooldown of 1 second.
- Add new commands `s!farmtop [s!ftop]` to view top farms globally.
- Add new command `s!trashplots` to discard crops planted in your plots.
    - `s!trashplots` on its own will scrap **ALL your plots**.
    - `s!trashplots 5` will scrap **Plot #0005 only**.
    - `s!trashplots 5-13` (no spaces!) will scrap **Plot #0005 to Plot #0013**.
- The command `s!farmharvest` can now **selectively harvest plots**. The mechanics used will be the same as above, in `s!trashplots`.
- `s!farmplots [page]` now sends an Embed, and is paginated.
- `s!showharvests` now sends an Embed.
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