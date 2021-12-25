import asyncio
import os
import csv
from dotenv import load_dotenv
from bscscan import BscScan
from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Coin:
    symbol: str
    amount: int
    usd_amount: int
    is_stable: bool
    
load_dotenv()

KEYS = {
    "BSCSCAN_API_KEY" : os.getenv('BSCSCAN_API_KEY'),
    "CMC_API_KEY" : os.getenv('CMC_API_KEY'),
    "ADDRESS": os.getenv('ADDRESS'),
    "vUSDT": "0xfd5840cd36d94d7229439859c0112a4185bc0255",
    "vBUSD": "0x95c78222b3d6e262426483d42cfa53685a67ab9d",
    "vBNB": "0xa07c5b74c9b40447a954e1466938b865b6bbea36"
}
MULTIPLIER = 100000000


wallet = [Coin("vBNB",0,0, False), Coin("vUSDT",0,0, True), Coin("vBUSD",0,0, True)]

def write_to_excel(wallet):
    with open('history.csv', 'a', newline='') as f:
        csv.writer(f).writerow(
            [datetime.now().strftime('%Y-%m-%d %H:%M:%S')] + \
            [float("{:.2f}".format(coin.usd_amount)) for coin in wallet] + \
            [float("{:.2f}".format(sum([coin.usd_amount for coin in wallet if coin.is_stable == True])))]
            )
    

async def main():
    async with BscScan(KEYS["BSCSCAN_API_KEY"]) as bsc:
        cmc = CoinMarketCapAPI(KEYS["CMC_API_KEY"])
        for coin in wallet:
            coin.amount = await getAccountAmount(bsc, coin.symbol)
            r = cmc.tools_priceconversion(symbol=coin.symbol, amount=coin.amount)
            coin.usd_amount = r.data['quote']['USD']['price']
        write_to_excel(wallet)
        print(coin)
        
async def getAccountAmount(bsc, currency: str):
    amount = int(await bsc.get_acc_balance_by_token_contract_address(address=KEYS["ADDRESS"], contract_address=KEYS[currency])) / MULTIPLIER
    print(f"{currency}: {amount}")
    return amount

if __name__ == "__main__":
  asyncio.run(main())
