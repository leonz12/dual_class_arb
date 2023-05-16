import ib_insync as ib
from arb_pair import Stock, ArbPair

STK1 = 'GOOG'
STK2 = 'GOOGL'


if __name__ == '__main__':

    api = ib.IB()
    api.connect()

    google = ArbPair(api, STK1, STK2, 100)

    print(google.stock1.bars[-1].close)
    print(google.stock2.bars[-1].close)

    google.update()

    api.run()
