##  This bot is not suitable for trading real money.
import statistics

MEDIAN_EDGE_MULTIPLE = 1.001

class MarketMaker():
    def __init__(self, client, exchanges, bot_config, log):
        self.log          = log
        self.client       = client
        self.exchanges    = exchanges
        self.config       = bot_config
        self.name         = self.config["account_name"]
        self.quote_symbol = bot_config["asset_pair"][0]
        self.base_symbol  = bot_config["asset_pair"][1]

    def execute(self):
        self.log.info("Executing bot:  %s" % self.name)
        tolerance = self.config["external_price_tolerance"]
        spread = self.config["spread_percent"]
        min_balance = self.config["min_balance"]
        min_order_size = self.config["min_order_size"]
        quote = self.quote_symbol
        base = self.base_symbol

        # FIXME add weights
        true_price_per_btsx = statistics.median(self.exchanges.price_inbtsx[self.quote_symbol])
        median = self.client.get_median(self.quote_symbol)
        new_price_per_btsx = true_price_per_btsx

        if median > new_price_per_btsx:
            new_price_per_btsx = median * MEDIAN_EDGE_MULTIPLE

        canceled = []
        quote_freed = 0
        base_freed = 0
        
        result = self.client.get_asks_out_of_range(self.name, quote, base, new_price_per_btsx * (1+spread), tolerance)
        canceled.extend( result[0] )
        base_freed += result[1]
        
        result = self.client.get_bids_less_than(self.name, quote, base, median)
        canceled.extend( result[0] )
        quote_freed += result[1]
        
        result = self.client.get_bids_out_of_range(self.name, quote, base, new_price_per_btsx, tolerance)
        canceled.extend( result[0] )
        quote_freed += result[1]

        asset_balance = self.client.get_balance(self.name, quote) + quote_freed
        btsx_balance = self.client.get_balance(self.name, base) + base_freed
        available_btsx_balance = btsx_balance - min_balance
        available_asset_buy_quantity = (asset_balance / new_price_per_btsx) - min_balance;
        
        new_orders = []

        if available_asset_buy_quantity > min_order_size:
            self.log.info("Submitting a bid...")
            new_orders.append(["bid_order", [self.name, available_asset_buy_quantity, base, new_price_per_btsx, self.quote_symbol]])
        else:
            self.log.info("Skipping bid - %s balance of %d is too low" % (self.quote_symbol, available_asset_buy_quantity))

        if available_btsx_balance > min_order_size:
            self.log.info("submitting an ask...")
            new_orders.append(["ask_order", [self.name, available_btsx_balance, base, new_price_per_btsx * (1+spread), self.quote_symbol]])
        else:
            self.log.info("Skipping ask - %s balance of %d is too low" % (self.base_symbol, available_btsx_balance))

        if len(canceled) > 0 or len(new_orders) > 0:
            self.log.info("Committing orders.")
            trx = self.client.request("wallet_market_batch_update", [canceled, new_orders, True]).json()
