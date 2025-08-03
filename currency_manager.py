from tvDatafeed import TvDatafeed, Interval
import requests

class CurrencyManager:
    def __init__(self, nobitexCurrencies, cryptoSymbols):
        self.nobitexCurrencies = [x.lower() for x in nobitexCurrencies]
        self.cryptoSymbols = cryptoSymbols
        self.tv = TvDatafeed()
        self.exchangeRates = {}
        self.prices = {}

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
            raise ValueError("❌ خطا در دریافت داده از نوبیتکس:", e)

    def fetchCryptoPricesFromTv(self):
        for symbol in self.cryptoSymbols:
            try:
                df = self.tv.get_hist(symbol=symbol[:-4], exchange='BINANCE', interval=Interval.in_1_hour, n_bars=1)
                if not df.empty:
                    last_close = float(df['close'].iloc[-1])
                    self.prices[symbol] = {"usd": last_close, "irr": None}

            except Exception as e:
                raise ValueError(f"❌ خطا در دریافت {symbol} از tvDatafeed:", e)

    def convertUsdToIrr(self):
        usd_to_irr = self.exchangeRates.get("USD", 0)
        if usd_to_irr == 0:
            raise ValueError("❌ نرخ USD موجود نیست برای تبدیل")


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
