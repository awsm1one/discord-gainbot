'''discord-stock-ticker'''
from os import getenv
import logging

import asyncio
import discord
from redis import Redis, exceptions

from utils.yahoo import get_stock_price

CURRENCY = 'usd'

class Ticker(discord.Client):
    '''
    Discord client for watching stock prices
    '''


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ticker = getenv("TICKER")
        stock_name = getenv("STOCK_NAME", ticker)

        # Check that at least a ticker is set
        if not ticker:
            logging.error('TICKER not set!')
            return

        # Use different updates based on security type

        logging.info('stock ticker')

        self.bg_task = self.loop.create_task(
            self.stock_update_activity(
                ticker.upper(),
                stock_name.upper(),
                getenv('SET_NICKNAME'),
                getenv('SET_COLOR'),
                getenv('FLASH_CHANGE'),
                getenv('FREQUENCY', 60)
            )
        )

    async def on_ready(self):
        '''
        Log that we have successfully connected
        '''

        logging.info('logged in')

        # We want to know some stats
        servers = [x.name for x in list(self.guilds)]

        redis_server = getenv('REDIS_URL')
        if redis_server:

            # Use redis to store stats
            r = Redis(host=redis_server, port=6379, db=0)

            try:
                for server in servers:
                    r.incr(server)
            except exceptions.ConnectionError:
                logging.info('No redis server found, not storing stats')

        logging.info('servers: ' + str(servers))

    async def stock_update_activity(self, ticker: str, name: str, change_nick: bool = False, change_color: bool = False, flash_change: bool = False, frequency: int = 60):
        '''
        Update the bot activity based on stock price
        ticker = stock symbol
        name = override for symbol as shown on bot
        change_nick = flag for changing nickname
        frequency = how often to update in seconds
        '''

        old_price = 0.0
        change_up = True

        await self.wait_until_ready()
        logging.info('starting stock activity update job...')

        # Loop as long as the bot is running
        while not self.is_closed():

            logging.info('fetching stock price...')

            data = get_stock_price(ticker)
            price_data = data.get('quoteSummary', {}).get('result', []).pop().get('price', {})
            
            # Determine market state

            if price_data.get('marketState') == 'POST':
                state = 'postMarketPrice'
                change = 'postMarketChange'
                activity = 'After Hours'
            elif price_data.get('marketState') == 'REGULAR':
                state = 'regularMarketPrice'
                change = 'regularMarketChange'
                activity = 'Day'
            elif price_data.get('marketState') == 'PRE':
                state = 'preMarketPrice'
                change = 'preMarketChange'
                activity = 'Pre-Market'
            elif price_data.get('marketState') == 'PREPRE':
                state = 'postMarketPrice'
                change = 'postMarketChange'
                activity = 'Pre-Market Wait'
            else:
                state = 'postMarketPrice'
                change = 'postMarketChange'
            
            # Grab current price data

            price = price_data.get(state, {}).get('raw', 0.00)

            # Grab current diff

            raw_diff = price_data.get(change, {}).get('raw', 0.00)
            diff = round(raw_diff, 2)

            if diff >= 0.0:
                change_up = True
                diff = '+' + str(diff)
            else:
                change_up = False

            activity_content = f'${price} {activity} {diff}'
            logging.info(f'stock {activity} price retrieved: {activity_content}')

            # Change name via nickname if set
            if change_nick:
                for server in self.guilds:

                    green = discord.utils.get(server.roles, name="tickers-green")
                    red = discord.utils.get(server.roles, name="tickers-red")

                    try:
                        if price == old_price:
                            await server.me.edit(
                                nick=f'{name} - ${price}'
                            )
                        elif price > old_price:
                            await server.me.edit(
                                nick=f'{name} ↗ ${price}'
                            )
                        elif price < old_price:
                            await server.me.edit(
                                nick=f'{name} ↘ ${price}'
                            )
                        
                        if change_color:
                            if flash_change:
                                # Flash price change
                                if price > old_price:
                                    await server.me.add_roles(green)
                                    await server.me.remove_roles(red)
                                elif price < old_price:
                                    await server.me.add_roles(red)
                                    await server.me.remove_roles(green)

                            # Stay on day change
                            if change_up:
                                await server.me.add_roles(green)
                                await server.me.remove_roles(red)
                            else:
                                await server.me.add_roles(red)
                                await server.me.remove_roles(green)

                    except discord.HTTPException as e:
                        logging.error(f'updating nick failed: {e.status}: {e.text}')
                    except discord.Forbidden as f:
                        logging.error(f'lacking perms for changing nick: {f.status}: {f.text}')

                    logging.info(f'stock updated nick in {server.name}')
                
                activity_content = f'{activity}: {diff}'

            # Change activity
            try:
                await self.change_presence(
                    activity=discord.Activity(
                        type=discord.ActivityType.watching,
                        name=activity_content
                    )
                )

                logging.info(f'stock activity updated: {activity_content}')

            except discord.InvalidArgument as e:
                logging.error(f'updating activity failed: {e.status}: {e.text}')

            old_price = price

            logging.info(f'stock sleeping for {frequency}s')
            await asyncio.sleep(int(frequency))
            logging.info('stock sleep ended')


if __name__ == "__main__":

    logging.basicConfig(
        filename=getenv('LOG_FILE'),
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
        format='%(asctime)s %(levelname)-8s %(message)s',
    )

    token = getenv('DISCORD_BOT_TOKEN')
    if not token:
        logging.error('DISCORD_BOT_TOKEN not set!')

    client = Ticker()
    client.run(token)
