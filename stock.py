import ib_insync as ib

class Stock:
    def __init__(self, stk : str):
        self._symbol = stk
        self._update = False
        self._open = None
        self._last = None

    @property
    def symbol(self):
        return self._symbol

    @property
    def last(self):
        return self._last
    
    @last.setter
    def last(self, value : float):
        self._last = value
    
    @property
    def open(self):
        return self._open
    
    @open.setter
    def open(self, value : float):
        self._open = value

    @property
    def contract(self):
        return self._contract
    
    @contract.setter
    def contract(self, ctr : ib.Stock):
        self._contract = ctr

    @property
    def bars(self):
        return self._bars
    
    @bars.setter
    def bars(self, bar : ib.BarDataList):
        self._bars = bar

    @property
    def update(self):
        return self._update
    
    @update.setter
    def update(self, value : bool):
        return self.update
    
    
    def has_value(self) -> bool:
        if self._last is None or self._open is None:
            return False
        else:
            return True
    
    def gain(self) -> float:
        if self.has_value():
            return (self.last - self.open) / self.open
        else:
            return None
        
    def bar_update(self, bars : ib.BarDataList, hasNewBar : bool):
        if self.open is None:
            self.open = bars[-1].open
        else:
            self.last = bars[-1].close
    

