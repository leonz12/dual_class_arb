import ib_insync as ib
from stock import Stock
from decimal import Decimal


class ArbTrade:
    def __init__(self, api: ib.IB, stock : Stock, trade : str, qty : int):
        self._qty = qty
        self._api = api
        self._isopen = False
        self._isclosed = False
        self._stock = stock
        self._trade = trade
        self._active = False
        self._open = None
    
    @property
    def stock(self):
        return self._stock
    
    @property
    def qty(self):
        return self._qty
    
    @property
    def trade(self):
        return self._trade
    
    @property
    def isopen(self):
        return self._isopen

    @property
    def api(self):
        return self._api
    
    @property
    def isclosed(self):
        return self._isclosed

    def open(self):
        return self._open
    
    def open(self, price : float):
        self._open = price
    
    @property
    def close(self):
        return self._close
    
    @close.setter
    def close(self, price : Decimal):
        self._close = price
    
    @property
    def active(self):
        return self._active

    def _open_order_status(self, trade):
        if trade.orderStatus.status == 'Filled':
            fill = trade.fills[-1]
            print("Order Filled:", fill.time, fill.execution.side, fill.contract.symbol, fill.execution.shares, fill.execution.avgPrice)
            self._open = fill.execution.avgPrice
            self._isopen = True
            self._active = False
        else:
            print("Waiting to open.", fill.execution.side, fill.contract.symbol)

    def _close_order_status(self, trade):
        if trade.orderStatus.status == 'Filled':
            fill = trade.fills[-1]
            print("Order Filled:", fill.time, fill.execution.side, fill.contract.symbol, fill.execution.shares, fill.execution.avgPrice)
            self._close = fill.execution.avgPrice
            self._isclosed = True
            self._active = False
        else:
            print("Waiting to close.", fill.execution.side, fill.contract.symbol)

    def open_trade(self):
        '''Open a trade'''
        if self._trade == 'long':
            action = 'BUY'
        elif self._trade == 'short':
            action = 'SELL'

        order = ib.MarketOrder(action, self._qty)
        trade = self._api.placeOrder(self._stock.contract, order)
        trade.filledEvent += self._open_order_status
        self._active = True
        # self._api.sleep(60)
        # if trade.orderStatus.status != 'Filled':
        #     raise "Order placement error!"

    def close_trade(self):
        '''Close a trade'''
        if self._trade == 'long':
            action = 'SELL'
        elif self._trade == 'short':
            action = 'BUY'
        
        order = ib.MarketOrder(action, self._qty)
        trade = self._api.placeOrder(self._stock.contract, order)
        trade.filledEvent += self._close_order_status
        self._active = True
        # self._api.sleep(60)
        # if trade.orderStatus.status != 'Filled':
        #     raise "Order closing error!"


    def base_margin(self):
        if self.isopen or self.isclosed:    
            return abs((self._open) * self.qty)
        else:
            return None
    
    def market_margin(self):
        if self.isopen or self.isclosed:
            return abs(self.stock.last * self.qty)
        else:
            return None
    
    def profit(self):
        if self.isclosed:
            if self.trade == 'long':
                return (self._close - self._open) * self.qty
            elif self.trade == 'short':
                return (self._open - self._close) * self.qty
            else:
                return None
        elif self.isopen:
            if self.trade == 'long':
                return (self.stock._last - self._open) * self.qty
            if self.trade == 'short':
                return (self._open - self.stock._last) * self.qty
            else:
                return None
        else:
            return None

    def gain(self):
        if self.isopen or self.isclosed:
            return self.profit() / self.base_margin()
        else:
            return None
    
    
