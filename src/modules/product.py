from src.modules.category import Category
class Product:
    def __init__(self, name : str, price : float, category : Category, _id = None) -> None:
        self._id = _id
        self.name = name
        self.price = price
        self.category = category

    @classmethod
    def filterProduct(self,productId,conn):
        cursor = conn.cursor()
        sql = '''
            select * from products 
            where _id = (?) '''
        cursor.execute(sql,(productId,))
        product = cursor.fetchone()
        if product:
            return product
        cursor.close()
        
    
    def showProducts(self,sql,conn):
        cursor = conn.cursor()
        cursor.execute(sql)
        output = cursor.fetchall()
        for row in output:
            print(F"{row[0]} - {row[1]}")

    def selectedProduct(self,conn,_id):
        cursor = conn.cursor()
        sql = '''
        select * from categories
        where _id = ?'''
        cursor.execute(sql,_id)
        category = cursor.fetchone()
        self.id = category[0]
        self.name = category[1]
        cursor.close()
    