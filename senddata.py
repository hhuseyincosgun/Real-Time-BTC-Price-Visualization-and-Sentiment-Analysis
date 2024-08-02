import asyncio
import aiomysql
from binance import AsyncClient, BinanceSocketManager
from binance.enums import *
from datetime import datetime, timezone

# Define the AWS RDS endpoint and database credentials
RDS_ENDPOINT = 'your_rds_endpoint'
RDS_USER = 'your_rds_user'
RDS_PASSWORD = 'your_rds_password'
RDS_DB = 'your_rds_db'
RDS_PORT = 3306

async def save_to_rds(event_time, open_price, high_price, low_price, close_price, volume):
    conn = await aiomysql.connect(host=RDS_ENDPOINT, port=RDS_PORT, user=RDS_USER, password=RDS_PASSWORD, db=RDS_DB)
    async with conn.cursor() as cur:
        await cur.execute(
            "INSERT INTO your_table (Event_Time, Open, High, Low, Close, Volume) VALUES (%s, %s, %s, %s, %s, %s)",
            (event_time, open_price, high_price, low_price, close_price, volume)
        )
        await conn.commit()
    conn.close()

async def main():
    # Initialize the Binance client
    client = await AsyncClient.create()
    bm = BinanceSocketManager(client)

    # Create a kline socket for the BTCUSDT trading pair with a 1-minute interval
    ks = bm.kline_socket('BTCUSDT', interval=KLINE_INTERVAL_1MINUTE)

    # Open the kline socket and process incoming messages
    async with ks as stream:
        while True:
            res = await stream.recv()
            # Check if the kline is closed
            if res['k']['x']:
                # Extract kline data
                kline = res['k']
                open_time = kline['t']
                open_price = float(kline['o'])
                high_price = float(kline['h'])
                low_price = float(kline['l'])
                close_price = float(kline['c'])
                volume = float(kline['v'])

                # Convert the timestamp to a readable format
                event_time = datetime.fromtimestamp(open_time / 1000, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

                # Send data to RDS
                await save_to_rds(event_time, open_price, high_price, low_price, close_price, volume)

                # Print the data (for debugging purposes)
                print(f"{event_time} {open_price} {high_price} {low_price} {close_price} {volume}")

    # Close the Binance client
    await client.close_connection()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
