import psycopg2
from config import config
from prettytable import PrettyTable

#Create table helper function
def createTable(crsr):
    table = PrettyTable()
    rows = crsr.fetchall()
    table.field_names = [desc[0] for desc in crsr.description]
    table.add_rows(rows)
    return  table




#This function is used to display products
def display_products(crsr):
    crsr.execute('SELECT * FROM  producttable')
    print(createTable(crsr))

#To get an item from product table
def get_item_from_product_table(crsr, product_id_inp):
    crsr.execute("SELECT * FROM ProductTable WHERE ProductId = %s", (product_id_inp,))
    print(createTable(crsr))

#Updating of the productSoldTable is done using this method
def update_ProductsSoldTable(crsr, product_id_inp):
    crsr.execute("SELECT * FROM productTable WHERE ProductId = %s", (product_id_inp,))
    product_info = crsr.fetchall()[0]
    product_id = product_info[0]
    seller_id = product_info[3]
    price = product_info[4]
    buyer_id = "1"

    print(product_id, seller_id, price, buyer_id)

    #Continue from here
    #Methanin apu output tiken productSold table eka update karanna tiyenne
    crsr.execute("""
        INSERT INTO ProductsSoldTable (SellerId, ProductId, Amount, BuyerId)
        VALUES (%s, %s, %s, %s);
    """, (seller_id, product_id, price, buyer_id))

    crsr.execute("SELECT * FROM ProductsSoldTable")
    print(createTable(crsr))







#The arithmatic operation related to reducing the quantity when a user buys a product
def reduce_quantity(crsr, product_id_inp):
    crsr.execute("SELECT QuantityAvailable FROM ProductTable WHERE ProductId = %s", (product_id_inp,))
    quantity = crsr.fetchone()
    new_quantity = int(quantity[0]) - 1
    crsr.execute("BEGIN; UPDATE ProductTable SET QuantityAvailable = %s WHERE ProductId = %s;",
                   (str(new_quantity), product_id_inp))
    crsr.execute("SELECT * FROM ProductTable")
    wish_to_change = input("Press 1 to save change or else of rollback :")
    if wish_to_change == "1":
        crsr.execute("commit")
        update_ProductsSoldTable(crsr,product_id_inp)
    else:
        crsr.execute("rollback")
    crsr.execute("SELECT * FROM ProductTable")
    print(createTable(crsr))
    Login_page(crsr)

#This method is responsible for handling operations when a product is listed to sell
def sell_product(crsr, username):
    crsr.execute("SELECT SellerId FROM SellerTable WHERE SellerName = %s", (username,))
    seller_id = crsr.fetchone()[0]
    product_name = input("Please Enter product name : ")
    description = input("Please Enter a product description : ")
    price = float(input("Please Enter the price : "))
    Quantity_available = int(input("please Enter the quantity : "))

    crsr.execute("""Begin;
        INSERT INTO ProductTable (ProductName, Description, SellerId, Price, QuantityAvailable)
        VALUES (%s, %s, %s, %s, %s);
    """, (product_name, description, seller_id, price, Quantity_available))

    sure_commit_statement = input("Press 1 to commit or other to rollback : ")
    if sure_commit_statement == "1":
        crsr.execute("commit")
        crsr.execute("SELECT * FROM producttable")
        print(createTable(crsr))
        print("Changes saved!")
        Login_page(crsr)
    else:
        crsr.execute("rollback")
        Login_page(crsr)

def veiw_seller_products(crsr, user_name):
    query = """
        SELECT 
            ProductTable.ProductId,
            ProductName,
            Description,
            SellerName,
            Price,
            QuantityAvailable
        FROM 
            ProductTable
        JOIN 
            SellerTable ON ProductTable.SellerId = SellerTable.SellerId
        WHERE 
            SellerName = %s;
    """

    crsr.execute(query, (user_name,))

    products = crsr.fetchall()

    # Display the products
    for product in products:
        print("---------------------------------")
        print("Product ID:", product[0])
        print("Product Name:", product[1])
        print("Description:", product[2])
        print("Seller Name:", product[3])
        print("Price:", product[4])
        print("Quantity Available:", product[5])
        print("----------------------------------")

    Login_page(crsr)



def Login_page(crsr):
    buyer_or_seller = input("Please Enter 1-Buyer 2-Seller : ")
    if buyer_or_seller == "1":
        display_products(crsr)
        print("Looking for a specific product?")

        product_id_inp = input("Enter a valid product ID to select or % to Home page : ")
        if product_id_inp == "%":
            Login_page(crsr)
        get_item_from_product_table(crsr, product_id_inp)
        buy_item_request = input("Press 1 to buy this item : ")
        if buy_item_request == "1":
            reduce_quantity(crsr, product_id_inp)
    elif buyer_or_seller == "2":
        user_name = input("Enter your name : ")
        crsr.execute("SELECT SellerName FROM SellerTable")
        seller_names = [seller[0] for seller in crsr.fetchall()]

        if user_name in seller_names:
            sell_or_exit_input = input("Please enter 1-Sell 2-Veiw Products 3-Exit : ")
            if sell_or_exit_input == "1":
                sell_product(crsr, user_name)
            elif sell_or_exit_input == "2":
                veiw_seller_products(crsr, user_name)
            elif sell_or_exit_input == "3":
                Login_page()


        else:
            crsr.execute("""
                INSERT INTO SellerTable (SellerName)
                VALUES (%s);
            """, (user_name,))
            Login_page(crsr)








def connect():
    connection = None
    try:
        params = config()
        print('Connecting to the postgreSQL database...')
        connection = psycopg2.connect(**params)
        
        #Create a cursor
        crsr = connection.cursor()

        crsr.execute("SELECT version();")
        # Fetch the result
        version = crsr.fetchone()[0]
        print("ProsgreSQL Version : " + version)


        Login_page(crsr)

        crsr.close()
    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if connection is not None:
            connection.close()
            print('Database connection terminated')



if __name__ == "__main__":
    connect()

