# currency_manager.py

from tvDatafeed import TvDatafeed, Interval
import requests


class CurrencyManager:
    def __init__(self, nobitexCurrencies, cryptoSymbols):
        self.nobitexCurrencies = [x.lower() for x in nobitexCurrencies]  # ['usd', 'eur', ...]
        self.cryptoSymbols = cryptoSymbols                                # ['BTCUSDT', 'TRUMPUSDT', ...]
        self.tv = TvDatafeed()
        self.exchangeRates = {}  # {'USD': 65000, 'EUR': ...}
        self.prices = {}         # {'BTCUSDT': {'usd': 50000, 'irr': 3250000000}, 'usd': {'usd': 1, 'irr': 65000}}

    def fetchNobitexPrices(self):
        url = "https://api.nobitex.ir/market/stats"
        try:
            response = requests.get(url)
            data = response.json().get("global", {})
            for currency in self.nobitexCurrencies:
                pair = f"{currency}-rls"
                if pair in data:
                    price_irr = float(data[pair]['lastTradePrice'])
                    self.exchangeRates[currency.upper()] = price_irr
                    self.prices[currency.upper()] = {"usd": 1.0, "irr": price_irr}
        except Exception as e:
            print("❌ خطا در دریافت داده از نوبیتکس:", e)

    def fetchCryptoPricesFromTv(self):
        for symbol in self.cryptoSymbols:
            try:
                df = self.tv.get_hist(symbol=symbol[:-4], exchange='BINANCE', interval=Interval.in_1_hour, n_bars=1)
                if not df.empty:
                    last_close = float(df['close'].iloc[-1])
                    self.prices[symbol] = {"usd": last_close, "irr": None}
            except Exception as e:
                print(f"❌ خطا در دریافت {symbol} از tvDatafeed:", e)

    def convertUsdToIrr(self):
        usd_to_irr = self.exchangeRates.get("USD", 0)
        if usd_to_irr == 0:
            print("❌ نرخ USD موجود نیست برای تبدیل")
            return

        for symbol, val in self.prices.items():
            if val.get("irr") is None and val.get("usd") is not None:
                self.prices[symbol]["irr"] = round(val["usd"] * usd_to_irr)

    def updateAll(self):
        self.fetchNobitexPrices()
        self.fetchCryptoPricesFromTv()
        self.convertUsdToIrr()

    def getPriceDict(self):
        return self.prices

    def printPrices(self):
        for symbol, price in self.prices.items():
            print(f"🔹 {symbol}: {price['usd']} USD  |  {price['irr']} IRR")


# 🎯 استفاده
if __name__ == "__main__":
    nobitexCurrencies = ['usd', 'eur', 'cny', 'jpy']
    cryptoSymbols = ['BTCUSDT', 'ETHUSDT', 'TRUMPUSDT']

    cm = CurrencyManager(nobitexCurrencies, cryptoSymbols)
    cm.updateAll()
    cm.printPrices()p