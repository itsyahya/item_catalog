import os

from .Database_setup import Markets, ItemsInMarket,addAndCommit


apple = Markets(name="Apple")

addAndCommit(apple)

item = ItemsInMarket(name="MacBookPro",
                     description=" 15 inch - i9 - 32 ram",
                     price="$8.99", market=apple)
addAndCommit(item)

item = ItemsInMarket(name="Iphone X",
                     description="250 gigs - 4 ram",
                     price="$3,49", market=apple)
addAndCommit(item)

item = ItemsInMarket(name="MacBookPro",
                     description=" 15 inch - i9 - 32 ram",
                     price="$8.99", market=apple)
addAndCommit(item)

# Samsung market
samSung = Markets(name="SamSung")
addAndCommit(samSung)

item = ItemsInMarket(name="Galaxy s9",
                     description=" 250 gigs - 4 ram - slot SD",
                     price="$2.99",
                     market=samSung)
addAndCommit(item)

item = ItemsInMarket(name="Galaxy Note 8",
                     description="250 gigs - 6 ram dual sim - SD slot",
                     price="$4,00",
                     market=samSung)
addAndCommit(item)

item = ItemsInMarket(name="Watch",
                     description="headphone jack ",
                     price="$1.99",
                     market=samSung)
addAndCommit(item)

print('menu Added !')
