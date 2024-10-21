from datetime import date
from product import Product
class Sale:
    def __init__(self,quantity : int, total : float,product : Product) -> None:

        self.dateOfSale = date.today()
        self.quantity = quantity
        self.total = total
        self.product = product