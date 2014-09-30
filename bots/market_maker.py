##  This bot is not suitable for trading real money.


MEDIAN_EDGE_MULTIPLE = 1.001

class MarketMaker():
    def __init__(self, client, feeds, bot_config, log):
        self.log = log
        self.client = client
        if not "usd_per_btsx" in feeds:
            raise Exception("Missing required feed 'usd_per_btsx' for market maker bot")
        self.feeds = feeds
        if not "bot_type" in bot_config or bot_config["bot_type"] != "market_maker":
            raise Exception("Bad bot configuration object")
        self.config = bot_config
        self.name = self.config["account_name"]
        self.quote_symbol = bot_config["asset_pair"][0]
        self.base_symbol = bot_config["asset_pair"][1]


    def execute(self):
        self.log("Executing bot:  %s" % self.name)
        tolerance = self.config["external_price_tolerance"]
        spread = self.config["spread_percent"]
        min_balance = self.config["min_balance"]
        min_order_size = self.config["min_order_size"]
        quote = self.quote_symbol
        base = self.base_symbol


        true_usd_per_btsx = self.feeds["usd_per_btsx"].fetch()
        median = self.client.get_median(self.quote_symbol)
        new_usd_per_btsx = true_usd_per_btsx

        if median > new_usd_per_btsx:
            new_usd_per_btsx = median * MEDIAN_EDGE_MULTIPLE

        canceled = []
        quote_freed = 0
        base_freed = 0
        
        result = self.client.get_asks_out_of_range(self.name, quote, base, new_usd_per_btsx * (1+spread), tolerance)
        canceled.extend( result[0] )
        base_freed += result[1]
        
        result = self.client.get_bids_less_than(self.name, quote, base, median)
        canceled.extend( result[0] )
        quote_freed += result[1]
        
        result = self.client.get_bids_out_of_range(self.name, quote, base, new_usd_per_btsx, tolerance)
        canceled.extend( result[0] )
        quote_freed += result[1]

        usd_balance = self.client.get_balance(self.name, quote) + quote_freed
        btsx_balance = self.client.get_balance(self.name, base) + base_freed
        available_btsx_balance = btsx_balance - min_balance
        available_usd_buy_quantity = (usd_balance / new_usd_per_btsx) - min_balance;
        
        new_orders = []

        if available_usd_buy_quantity > min_order_size:
            self.log("Submitting a bid...")
            new_orders.append(["bid_order", [self.name, available_usd_buy_quantity, base, new_usd_per_btsx, self.quote_symbol]])
        else:
            self.log("Skipping bid - %s balance of %d is too low" % (self.quote_symbol, available_usd_buy_quantity))

        if available_btsx_balance > min_order_size:
            self.log("submitting an ask...")
            new_orders.append(["ask_order", [self.name, available_btsx_balance, base, new_usd_per_btsx * (1+spread), self.quote_symbol]])
        else:
            self.log("Skipping ask - %s balance of %d is too low" % (self.base_symbol, available_btsx_balance))
        
        if len(canceled) > 0 or len(new_orders) > 0:
            self.log("Committing orders.")
            trx = self.client.request("wallet_market_batch_update", [canceled, new_orders, True]).json()

