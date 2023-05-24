import ib_insync as ib
from stock import Stock
from arb_trade import ArbTrade
import sys



import ib_insync as ib
from arb_pair import ArbTrade

LOWER = -0.2
UPPER = 0.2

class ArbPair:

    _stock1 : Stock
    _stock2 : Stock
    _api : ib.IB
    _lot : int
    _ratio : int
    _direction : str
    _long : ArbTrade
    _short : ArbTrade
    _isopen : bool

    def __init__(self, api : ib.IB, stock1 : str, stock2 : str, lot : int, ratio : int = 1):
        self._stock1 = Stock(stock1)
        self._stock2 = Stock(stock2)
        self._api = api
        self._ratio = ratio
        self._lot = lot
        self._direction = None
        self._long = None
        self._short = None
        self._isopen = False
        self._isactive = False

        contract = ib.Stock(self.stock1.symbol, 'SMART', 'USD')
        self.api.qualifyContracts(contract)
        self.stock1.contract = contract

        contract = ib.Stock(self.stock2.symbol, 'SMART', 'USD')
        self.api.qualifyContracts(contract)
        self.stock2.contract = contract

        self.check_existing()

        self.stock1.bars = self.api.reqHistoricalData(self.stock1.contract, '', '5 D', '1 day', 'TRADES', useRTH=True, keepUpToDate=True)

        self.stock1.bars.updateEvent += self.stock1.bar_update
        self.stock1.bars.updateEvent += self.update

        self.stock2.bars = self.api.reqHistoricalData(self.stock2.contract, '', '5 D', '1 day', 'TRADES', useRTH=True, keepUpToDate=True)

        self.stock2.bars.updateEvent += self.stock2.bar_update
        self.stock2.bars.updateEvent += self.update


    @property
    def stock1(self):
        return self._stock1
    
    @property
    def stock2(self):
        return self._stock2
    
    @property
    def api(self):
        return self._api
    
    @property
    def long(self):
        return self._long
    
    @property
    def short(self):
        return self._short
    
    @property
    def lot(self):
        return self._lot
    
    @property
    def ratio(self):
        return self._ratio
    
    
    def check_existing(self):
        positions = self._api.positions()
        for i in positions:
            if self.stock1.contract == i.contract:
                if i.position > 0:
                    self._long = ArbTrade(self.api, self.stock1, 'long', abs(i.position))
                    self._long.open = i.avgCost
                else:
                    self._short = ArbTrade(self.api, self.stock1, 'short', abs(i.position))
                    self._short.open = i.avgCost
            elif self.stock2.contract == i.contract:
                if i.position > 0:
                    self._long = ArbTrade(self.api, self.stock2, 'long', abs(i.position))
                    self._long.open = i.avgCost
                else:
                    self._short = ArbTrade(self.api, self.stock2, 'short', abs(i.position))
                    self._short.open = i.avgCost

        if self._long == None and self._short == None:
            return
        
        print("Long:", self._long.stock.symbol, self._long.qty, self._long.open)
        print('Short:', self._short.stock.symbol, self._short.qty, self._short.open)
        
        # Validation
        try:
            if (self._long == None) != (self._short == None):
                raise ValueError('Not long/short pair')
            if self._long.stock == self.stock1 and self._short.stock == self.stock2:
                self._direction = 'forward'
                if int(self._lot) != self._long.qty or abs(int(self._short.qty/self._long.qty)) != self._ratio:
                    raise ValueError(f'Quantity not correct. {self._long.qty}, {self._short.qty/self._long.qty}')
            elif self._long.stock == self.stock2 and self._short.stock == self.stock1:
                self._direction = 'reverse'
                if self._lot != self._short.qty or self._long.qty/self._short.qty != self._ratio:
                    raise ValueError('Quantity not correct')
            else:
                raise ValueError("Not long/short pair")
        except Exception as e:
            print('Error Occured in existing positon!')
            print(e)
            if self._long != None:
                print("Long:", self._long.stock.symbol, self._long.qty, self._long.open)
            if self._long != None:
                print('Short:', self._short.stock.symbol, self._short.qty, self._short.open)
            sys.exit()
        
        self._isopen = True

        print("Direction:", self._direction)


    def index(self):
        if self.stock1.has_value() and self.stock2.has_value():
            i = (self.stock2.gain() - self.stock1.gain()) / self.stock1.gain()
            if self.stock1.gain() >= self.stock2.gain():
                return -1 * abs(i)
            else:
                return abs(i)
        else:
            return None
        
    def check_open(self):
        if self.check_active():
            return self._isopen
        
        self._isopen = False
        if self._long != None and self._short != None:
            if self._long.isopen and not self._long.isclosed:
                if self._short.isopen and not self._short.isclosed:
                    self._isopen = True
            
        return self._isopen

    def check_active(self):
        self._isactive = False
        if self._long != None and self._short != None:
            if self._long.active or self._short.active:
                self._isactive = True
        return self._isactive
    
    def algo(self):
        if self.index() is None or self.check_active():
            return
        
        print('Index:', self.index(), 'Direction:', self._direction, 'Open:', self.check_open())
        
        if self.index() < LOWER and not self.check_open():
            self._direction = 'reverse'
            self._short = ArbTrade(self._api, self._stock1, 'short', self._lot)
            self._short.open_trade()
            self._long = ArbTrade(self._api, self._stock2, 'long', self._lot)
            self._long.open_trade()
            # self._isopen = True

        elif self.index() > UPPER and not self.check_open():
            self._direction = 'forwrad'
            self._long = ArbTrade(self._api, self._stock1, 'long', self._lot)
            self._long.open_trade()
            self._short = ArbTrade(self._api, self._stock2, 'short', self._lot)
            self._short.open_trade()
            # self._isopen = True

        elif self.index() < 0.02 and self._direction == 'forward' and self.check_open():
            self._long.close_trade()
            self._short.close_trade()
            # self._isopen = False
        
        elif self.index() > -0.02 and self._direction == 'reverse' and self.check_open():
            self._long.close_trade()
            self._short.close_trade()
            # self._isopen = False

    
        
    def update(self, *args):
        print('=' *20 )
        print(self.stock1.symbol, self.stock1.open, self.stock1.last, self.stock1.gain())
        print(self.stock2.symbol, self.stock2.open, self.stock2.last, self.stock2.gain())
        print('Index: ', self.index())
        self.algo()
        
        if self._isopen:
            print('Long:', self._long.stock.symbol, self._long.open, self._long.stock.last, self._long.profit())
            print('Short:', self._short.stock.symbol, self._short.open, self._short.stock.last, self._short.profit())
        
        
        