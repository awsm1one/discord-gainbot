# discord-stock-ticker

Props to https://github.com/rssnyder/discord-stock-ticker for the instructions.

### Hosting

Install python for your target operating system.

Clone down the repo locally:

```
git clone git@github.com:awsm1one/discord-gainbot.git && cd discord-gainbot
```

Register a new application in the discord developer portal and copy the bot token:

```
export DISCORD_BOT_TOKEN=<token>
```

If you are watching a stock, enter the ticker symbol, and optionally you can set a custom name to appear instead of the symbol:

```
export TICKER=GME
export STOCK_NAME=GameStop
```

You can optionally give your bot "change nickname" permissions to get around discord's limit on changing names only twice per two hours. Then you can set a custom amount of time between price updates (in seconds):

You must also make sure your bot has `Change Nickname` permissions to your server.

```
export SET_NICKNAME=1
export FREQUENCY=3
```

To enable color changing on price change, there is some setup needed. First you must create a new role to place the bots in. You need to check the `Display role members seperatly from other online members` option for this role, and **do not** assign a custom color for this role, leave it default.

Next you must create two roles called `tickers-green` and `tickers-red `. **Do not** check the `Display role members seperatly from other online members` option, but do set the colors for these roles to be `green` and `red` accordingly (or choose your own colors). These two new roles must appear **below** the general ticker role you created in the first step in the roles list.

You must also make sure your bot has `Manage Roles` permissions to your server.

Lastly, to enable the color changing, set `SET_COLOR=1` in your environment:

```
export SET_COLOR=1
```

Other options:

```
export LOG_FILE=log.log  # log to file instead of stdout
export POST_MARKET_PRICE=3  # display post market price instead of difference
```

Once all your options are set, simply install the dependencies and run the bot (virtual environments might be a smart idea):

```
pip3 install -r requirements.txt
python3 main.py
```

### Docker

You can also run these bots using docker. This can make running multiple bots esier. Here is an example docker compose file for the basic feature set (please check for the latest release and update the tags accordingly):

```
---
version: "2"
services:
  ticker-pfg:
    image: ghcr.io/rssnyder/discord-stock-ticker:1.6.0
    container_name: discord-stock-ticker
    environment:
      - DISCORD_BOT_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
      - TICKER=PFG
    restart: unless-stopped
  ticker-aapl:
    image: ghcr.io/rssnyder/discord-stock-ticker:1.6.0
    container_name: discord-stock-ticker
    environment:
      - DISCORD_BOT_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
      - TICKER=GME
    restart: unless-stopped
```

And here is an example of enabling faster updates with color changes:

```
---
version: "2"
services:
  ticker-pfg:
    image: ghcr.io/rssnyder/discord-stock-ticker:1.6.0
    container_name: discord-stock-ticker
    environment:
      - DISCORD_BOT_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
      - TICKER=PFG
      - SET_NICKNAME=1
      - SET_COLOR=1
      - FREQUENCY=10
    restart: unless-stopped
  ticker-aapl:
    image: ghcr.io/rssnyder/discord-stock-ticker:1.6.0
    container_name: discord-stock-ticker
    environment:
      - DISCORD_BOT_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
      - TICKER=AAPL
      - SET_NICKNAME=1
      - SET_COLOR=1
      - FREQUENCY=10
    restart: unless-stopped
```

```
docker-compose-up -d
```

## Support

If you have a request for a new ticker or issues with a current one, please open a github issue or find me on discord at `jonesbooned#1111` or [join the support server](https://discord.gg/CQqnCYEtG7).

Love these bots? Maybe [buy the original author a coffee](https://ko-fi.com/rileysnyder)! Or send some crypto to help keep the original bots running:

eth: 0x27B6896cC68838bc8adE6407C8283a214ecD4ffE

doge: DTWkUvFakt12yUEssTbdCe2R7TepExBA2G

bch: qrnmprfh5e77lzdpalczdu839uhvrravlvfr5nwupr

btc: 1N84bLSVKPZBHKYjHp8QtvPgRJfRbtNKHQ
