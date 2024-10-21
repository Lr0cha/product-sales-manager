class Category:
    def __init__(self, name = "", _id = None) -> None:
        self.name = name
        self.id = _id

    @classmethod
    def showCategories(self,sql,conn):
        cursor = conn.cursor()
        cursor.execute(sql)
        output = cursor.fetchall()
        for row in output:
            print(F"{row[0]} - {row[1]}")
        cursor.close()

    @classmethod
    def selectedCategory(self,conn,_id):
        cursor = conn.cursor()
        sql = '''
        select * from categories
        where _id = ?'''
        cursor.execute(sql,(_id,))
        category = cursor.fetchone()
        if category:
            return category
        cursor.close()