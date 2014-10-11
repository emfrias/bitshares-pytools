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
        canceled.extend( self.client.cancel_asks_out_of_range(self.name, quote, base, new_price_per_btsx * (1+spread), tolerance) )
        canceled.extend( self.client.cancel_bids_less_than(self.name, quote, base, median) )
        canceled.extend( self.client.cancel_bids_out_of_range(self.name, quote, base, new_price_per_btsx, tolerance) )

        if len(canceled) > 0:
            self.log.info("canceled some orders, waiting...")
            return # wait for a block if we canceled anything

        asset_balance                = self.client.get_balance(self.name, quote)
        btsx_balance                 = self.client.get_balance(self.name, base)
        available_btsx_balance       = btsx_balance - min_balance
        available_asset_buy_quantity = (asset_balance / new_price_per_btsx) - min_balance;

        if available_asset_buy_quantity > min_order_size:
            self.log.info("Submitting a bid...")
            #self.client.submit_bid(self.name, available_asset_buy_quantity, base, new_price_per_btsx, self.quote_symbol)
        else:
            self.log.info("Skipping bid - %s balance too low" % self.quote_symbol)

        if available_btsx_balance > min_order_size:
            self.log.info("submitting an ask...")
            #self.client.submit_ask(self.name, available_btsx_balance, base, new_price_per_btsx * (1+spread), self.quote_symbol)
        else:
            self.log.info("Skipping ask - BTSX balance too low")
