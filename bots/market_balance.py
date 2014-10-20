## This is a very simple asset agnostic bot based on the Market Maker bot for

class MarketBalance():
    def __init__(self, client, exchanges, bot_config, log):
        self.log               = log
        self.client            = client
        self.config            = bot_config
        self.name              = self.config["account_name"]
        self.quote_symbol      = bot_config["asset_pair"][0]
        self.base_symbol       = bot_config["asset_pair"][1]
        self.min_base_balance  = self.config["min_base_balance"]
        self.min_quote_balance = self.config["min_quote_balance"]
        self.spread            = self.config["spread_percent"]

    def execute(self):
        self.log.debug("Executing bot:  %s" % self.name)

        # Some variavles
        SPREAD          = self.spread
        base_precision  = self.client.get_precision(self.base_symbol)
        quote_precision = self.client.get_precision(self.quote_symbol)
        median          = self.client.get_median(self.quote_symbol)

        # Get the ratio of the last filled order
        last_price = self.client.get_last_fill(self.quote_symbol, self.base_symbol)
        last_price = last_price * (base_precision / quote_precision)

        # Get balances
        quote_balance = self.client.get_balance(self.name, self.quote_symbol) 
        base_balance  = self.client.get_balance(self.name, self.base_symbol) 

        # The market has moved?
        open_orders = self.client.get_all_orders(self.name, self.quote_symbol, self.base_symbol)

        ## Inappropriate number of open orders - canceling all, freeing up funds
        if len(open_orders[0])!=0 and len(open_orders[0])!=2: # no order available? all set to continue below!
            self.log.info("%d open orders -> Market has moved and order was executed! Canceling the other!"%len(open_orders[0]))
            freed_base  = 0
            freed_quote = 0
            for o in open_orders[ 1 ] :
                if o[ "type" ] == "bid_order" :
                    freed_base += float(o["state"]["balance"]) / quote_precision
                elif o[ "type" ] == "ask_order" :
                    freed_quote += float(o["state"]["balance"]) / base_precision
                else :
                    raise Exception( "This bot only runs with a separate account name!" )
            self.log.info( "freeing up %.8f %5s" % (freed_base, self.base_symbol))
            self.log.info( "freeing up %.8f %5s" % (freed_quote, self.quote_symbol))
            # cancel order
            self.client.cancel_all_orders(self.name, self.quote_symbol, self.base_symbol)
            # Wait for 3 blocks just in case the client needs more time for
            # transmission! or a delegate misses its block
            self.client.wait_for_block()
            self.client.wait_for_block()
            self.client.wait_for_block()
            # go back!
            return
        elif len(open_orders[0]) == 0 :
            ask_price       = last_price * (1 + SPREAD)
            bid_price       = last_price * (1 - SPREAD)
            #quote_amount    = (quote_balance + freed_base  - self.min_base_balance )
            #base_amount     = (base_balance  + freed_quote - self.min_quote_balance)
            quote_amount    = float(quote_balance - self.min_base_balance )
            base_amount     = float(base_balance  - self.min_quote_balance)
            ask_amount_base = float(base_amount             * ((last_price*(SPREAD))/2.0) / ask_price)
            bid_amount_base = float(quote_amount/bid_price  * ((last_price*(SPREAD))/2.0) / bid_price)
            feed_price      = float(self.client.get_centerprice(self.quote_symbol, self.base_symbol))

            ## Initial balancing ... buying at market rate! (thus asks for confirmation)
            if (quote_amount/base_amount) > ask_price*2 or (quote_amount/base_amount) < bid_price/2  :
                print("Assets not balances.")
                print("Balances: %20.5f %s and %20.5f %s -> ratio: %.5f (feed: %.5f)" % (quote_amount,self.quote_symbol,base_amount,self.base_symbol,(quote_amount/base_amount),feed_price))
                print("Setting orders to balance the amounts!")
                if quote_balance/base_balance < feed_price : ## buy quote -> sell base
                    ask_amount_base = (quote_balance*feed_price+base_balance)/2.0 - quote_balance*feed_price
                    print("Trying to sell %f %s at market to balance account" % (ask_amount_base, self.base_symbol))
                    self.client.ask_at_market_price(self.name, ask_amount_base, self.base_symbol, self.quote_symbol, True)
                else : ### sell quote -> buy base
                    bid_amount_base = (quote_balance*feed_price+base_balance)/2.0 - base_balance
                    print("Trying to buy %f %s at market to balance account" % (bid_amount_base, self.base_symbol))
                    self.client.bid_at_market_price(self.name, bid_amount_base, self.base_symbol, self.quote_symbol, True)
                ## Wait for 3 blocks
                self.client.wait_for_block()
                self.client.wait_for_block()
                self.client.wait_for_block()
                return

            self.log.info( "available: %15.8f %5s            and          %15.8f %5s" %( base_amount, self.base_symbol, quote_amount, self.quote_symbol ) )
            self.log.info( "buy:       %15.8f %5s for price %15.8f -- pay %15.8f %5s" %( bid_amount_base, self.base_symbol, bid_price, bid_amount_base*bid_price, self.quote_symbol ))
            self.log.info( "sell:      %15.8f %5s for price %15.8f -- get %15.8f %5s" %( ask_amount_base, self.base_symbol, ask_price, ask_amount_base*ask_price, self.quote_symbol ))
            self.log.info( "submitting orders!" )

            new_orders = []
            self.client.submit_bid(self.name, bid_amount_base, self.base_symbol, bid_price, self.quote_symbol)
            self.client.submit_ask(self.name, ask_amount_base, self.base_symbol, ask_price, self.quote_symbol)

            # Wait for 3 blocks just in case the client needs more time for
            # transmission! or a delegate misses its block
            self.client.wait_for_block()
            self.client.wait_for_block()
            self.client.wait_for_block()

            ## Obsolete Code ###############
            #default (unlocked) >>> wallet_market_submit_bid bytemaster 20 XTS 1.1 USD        // buying 20 XTS @ 1.1 USD per XTS 
            # default (unlocked) >>> wallet_market_submit_ask bytemaster 20 XTS 1.1 USD        // selling 20 XTS @ 1.1 USD per XTS 
            #self.log.info(            ["bid_order", [self.name, bid_amount_base, self.base_symbol, bid_price, self.quote_symbol]])
            #self.log.info(            ["ask_order", [self.name, ask_amount_base, self.base_symbol, ask_price, self.quote_symbol]])
            #new_orders.append(["ask_order", [self.name, ask_amount_base, self.base_symbol, ask_price, self.quote_symbol]])
            #new_orders.append(["bid_order", [self.name, bid_amount_base, self.base_symbol, bid_price, self.quote_symbol]])
            #trx = self.client.request("wallet_market_batch_update", [open_orders[0], new_orders, False]).json()
        else :
            # wait
            return
