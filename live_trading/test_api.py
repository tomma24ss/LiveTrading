# -*- coding: utf-8 -*-
import ccxt


exchange = ccxt.binance({
    'apiKey': 'W6ExGwLORN6bhkQGobceWZbs2blozgXG8oI5PAlJDmOV3gKg6Rx0LOdskBDb3EqV',
    'secret': '631UzythueU17d2GSuUc3KBPSRjnR9ADiRejkpm2KUBjkj6oA96V99VAe3GOLOJo',
})

symbol = 'ETH/BTC'
type = 'limit'  # or 'market'
side = 'sell'  # or 'buy'
amount = 1.0
price = 0.060154  # or None

# extra params and overrides if needed
params = {
    'test': True,  # test if it's valid, but don't actually place it
}

order = exchange.create_order(symbol, type, side, amount, price, params)

print(order)