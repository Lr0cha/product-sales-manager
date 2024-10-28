import sqlite3
from src.modules.product import Product
from src.modules.category import Category
from src.modules.sale import Sale
from datetime import date
import pandas as pd
from tabulate import tabulate

# Função para converter date em string
def adapt_date(d):
    return d.isoformat()

# Função para converter string em date
def convert_date(date_string):
    return date.fromisoformat(date_string)

# Registrar os adaptadores: informa ao SQLite como tratar o tipo date do Py.
sqlite3.register_adapter(date, adapt_date)
sqlite3.register_converter("date", convert_date)


def intInputIsValid(textInput):
    while True:
        if textInput.isdigit():  # Verifica se a entrada é um número positivo
            return int(textInput)  # Sai da função
        else:
            textInput = input("Entrada inválida.Tente novamente: ")

def strInputIsValid(textInput):
    if all(letter.isalpha() for letter in textInput.strip()):
        return True
    else:
        return False

def registerCategory(conn):
    cursor = conn.cursor()
    try:
        sql = '''
        create table if not exists categories(
        _id integer primary key,
        name varchar(20));'''
        cursor.execute(sql) #criação caso não tenha a table
        while True:
            nameCategory = input("Digite o nome da categoria: ")
            isValid = strInputIsValid(nameCategory)
            if isValid and nameCategory != "":
                category = Category(nameCategory.upper()) #obj
                break
            else:
                print("Entrada inválida!")
                continue
        sql = '''
        insert into categories (name) 
        values (?)'''
        cursor.execute(sql,(category.name,)) #com parametro na query sql
        conn.commit() #gravar no db
        lastId = cursor.lastrowid #pegar id da inserção
        cursor.close()
        return lastId #retorna id do ult. inserido
    except sqlite3.Error as exc:
        print(f"Problema com o banco de dados: {exc}")
    except OSError as exc:
        print(f"Erro no que foi digitado: {exc}")

def registerProduct(conn):
    try:
        cursor = conn.cursor()
        sql = '''
        create table if not exists products(
        _id integer primary key,
        id_category integer,
        name varchar(80),
        price numeric,
        foreign key (id_category) references categories(_id))''' # fk da categoria
        cursor.execute(sql)
        
        Category.showCategories("select _id,name from categories",conn) #metodo da classe Category
        print("Digite ID da categoria do produto a ser cadastrado:")
        categoryId = intInputIsValid(input())
        objCategory = Category.selectedCategory(conn,categoryId) # recuperar categoria
        if not objCategory:
            print("Não há nenhuma categoria com este ID")
            return
        category = Category(_id = objCategory[0], name=objCategory[1])# obj

        inputText = input("Entre com os dados do produto:(nome,preço)").strip()
        productValues = inputText.split(",") 
        if len(productValues) != 2:
            print("Erro,digite 2 valores (o nome e o preço) do produto à ser inserido.")
            return
        product = Product(name = productValues[0].upper(),price = productValues[1],category = category)
        sql = '''
        insert into products(id_category, name, price) values
        (?,?,?)'''
        cursor.execute(sql,(product.category.id,product.name,product.price))
        conn.commit()
        lastId = cursor.lastrowid
        return lastId
    except sqlite3.Error as exc:
        print(f"Problema com o banco de dados: {exc}")
    except OSError as exc:
        print(f"Erro no que foi digitado: {exc}")
    finally:
        cursor.close()

def registerSale(conn):
    try:
        cursor = conn.cursor()
        sql = '''
        create table if not exists sales(
        _id integer primary key,
        id_product integer,
        dateOfSale date,
        quantity integer,
        total numeric,
        foreign key (id_product) references products(_id))'''
        cursor.execute(sql)

        productId = intInputIsValid(input("Digite o ID do produto a ser vendido: "))
        tupleProduct = Product.filterProduct(productId,conn)
        if not tupleProduct:
            print("Não há nenhum produto com este ID")
            return
        product = Product(_id = tupleProduct[0], category=tupleProduct[1],name=tupleProduct[2],price=tupleProduct[3])
        quantity = intInputIsValid(input("Digite a quantidade vendida: "))
        total = quantity * product.price

        sale = Sale(quantity,total,product)
        sql = '''
            insert into sales (id_product,dateOfSale,quantity,total)
            values (?,?,?,?)'''
        cursor.execute(sql,(sale.product._id,sale.dateOfSale,sale.quantity,sale.total))
        conn.commit()
        print(f"Venda de {sale.quantity} {sale.product.name} realizada com sucesso")
    except sqlite3.Error as exc:
        print(f"Problema com o banco de dados: {exc}")
    except OSError as exc:
        print(f"Erro no que foi digitado: {exc}")
    finally:
        cursor.close()

def showReports(conn):
    print("\t\t Relatórios de vendas:")

    sql = """
            SELECT p.name, strftime('%Y-%m-%d', s.dateOfSale) AS dateOfSale, s.quantity, s.total 
            FROM sales AS s 
            INNER JOIN products AS p ON p._id = s.id_product;
            """
    try:
        df = pd.read_sql_query(sql, conn) # pegar dados correspondentes da query
        # Exibir o DataFrame formatado com tabulate
        print(tabulate(df, headers='keys', tablefmt='pretty'))
        inputText = input("Deseja salvar a tabela como excel(s/n):")
        if strInputIsValid(inputText): # se for um dado válido
            if(inputText.lower()[0] == 's'):
                nameArq = input("Digite o nome do arquivo excel (ex: dados)")
                df.to_excel(f"{nameArq}.xlsx") # salvar o excel
            else:
                return
    except Exception as e:
         print(f"Erro ao executar a consulta SQL: {e}")

def main():
    try:
        # conexão com detecção de tipos
        with sqlite3.connect('src/database/store.db',
                            detect_types=sqlite3.PARSE_DECLTYPES) as conn:
            while(True):
                print("-" * 100)
                print("\t\t Controle de produtos e venda:")
                print('''
                [1] Cadastrar categoria de produto
                [2] Cadastrar produto
                [3] Registrar venda produto
                [4] Registros de venda
                [5] Sair do programa
                ->>''', end="")
                resp = intInputIsValid(input())
                match resp: #switch case
                    case 1:
                        catId = registerCategory(conn)
                        print(f"Categoria {catId} cadastrada com sucesso")
                    case 2:
                        prodId = registerProduct(conn)
                        if prodId:
                            print(f"Produto {prodId} cadastrado com sucesso")
                    case 3:
                        registerSale(conn)
                    case 4:
                        showReports(conn)
                    case 5:
                        print("Saindo")
                        break
                    case _:
                        print("Opção inválida, tente novamente!")
    except sqlite3.Error as exc:
        print(f"Erro no banco de dados: {exc}")

if __name__ == '__main__':
    main()


