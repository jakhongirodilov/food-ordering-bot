import sqlite3


class Database:
    def __init__(self, path_to_db="main.db"):
        self.path_to_db = path_to_db

    @property
    def connection(self):
        return sqlite3.connect(self.path_to_db)

    def execute(self, sql: str, parameters: tuple = None, fetchone=False, fetchall=False, commit=False):
        if not parameters:
            parameters = ()
        connection = self.connection
        connection.set_trace_callback(logger)
        cursor = connection.cursor()
        data = None
        cursor.execute(sql, parameters)

        if commit:
            connection.commit()
        if fetchall:
            data = cursor.fetchall()
        if fetchone:
            data = cursor.fetchone()
        connection.close()
        return data
    

# users   -------------------------------------------------------------------------------------------------------
    def create_table_users(self):
        sql = """
            CREATE TABLE Users (
                id int NOT NULL,
                Name varchar(255) NOT NULL,
                email varchar(255),
                language varchar(3),
                PRIMARY KEY (id)
                );
        """
        self.execute(sql, commit=True)

    @staticmethod
    def format_args(sql, parameters: dict):
        sql += " AND ".join([
            f"{item} = ?" for item in parameters
        ])
        return sql, tuple(parameters.values())

    def add_user(self, id: int, name: str, email: str = None, language: str = 'uz'):
        # SQL_EXAMPLE = "INSERT INTO Users(id, Name, email) VALUES(1, 'John', 'John@gmail.com')"

        sql = """
        INSERT INTO Users(id, Name, email, language) VALUES(?, ?, ?, ?)
        """
        self.execute(sql, parameters=(id, name, email, language), commit=True)

    def select_all_users(self):
        sql = """
        SELECT * FROM Users
        """
        return self.execute(sql, fetchall=True)

    def select_user(self, **kwargs):
        # SQL_EXAMPLE = "SELECT * FROM Users where id=1 AND Name='John'"
        sql = "SELECT * FROM Users WHERE "
        sql, parameters = self.format_args(sql, kwargs)

        return self.execute(sql, parameters=parameters, fetchone=True)

    def count_users(self):
        return self.execute("SELECT COUNT(*) FROM Users;", fetchone=True)

    def update_user_email(self, email, id):
        # SQL_EXAMPLE = "UPDATE Users SET email=mail@gmail.com WHERE id=12345"

        sql = f"""
        UPDATE Users SET email=? WHERE id=?
        """
        return self.execute(sql, parameters=(email, id), commit=True)

    def delete_users(self):
        self.execute("DELETE FROM Users WHERE TRUE", commit=True)


# products  -------------------------------------------------------------------------------------------------------
    def create_table_products(self):
        sql = """
        CREATE TABLE Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(50) NOT NULL,
            price REAL NOT NULL,
            UNIQUE(name, category)
        );
        """
        self.execute(sql, commit=True)

    def add_product(self, name: str, category: str, price: float):
        sql = """
        INSERT INTO Products (name, category, price) VALUES (?, ?, ?)
        """
        self.execute(sql, parameters=(name, category, price), commit=True)

    def select_all_products(self):
        sql = """
        SELECT * FROM Products
        """
        return self.execute(sql, fetchall=True)
    
    def select_product(self, id: int):
        # SQL_EXAMPLE = "SELECT * FROM Users where id=1 AND Name='John'"
        sql = """
            SELECT * FROM Products WHERE id = ?
        """

        return self.execute(sql, parameters=(id,), fetchone=True)

    def select_products_by_category(self, category: str):
        sql = """
        SELECT * FROM Products WHERE category = ?
        """
        return self.execute(sql, parameters=(category,), fetchall=True)

    def delete_products(self):
        self.execute("DELETE FROM Products WHERE TRUE", commit=True)

    
# carts ------------------------------------------------------------------------------------------------------
    def create_table_carts(self):
        sql = """
        CREATE TABLE Carts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES Users(id),
            FOREIGN KEY (product_id) REFERENCES Products(id),
            UNIQUE (user_id, product_id)
        );
        """
        self.execute(sql, commit=True)

    def add_to_cart(self, user_id: int, product_id: int, quantity: int):
        sql = """
        INSERT INTO Carts (user_id, product_id, quantity) VALUES (?, ?, ?)
        """
        self.execute(sql, parameters=(user_id, product_id, quantity), commit=True)

    def increment_quantity(self, quantity, user_id, product_id):
        # Increment the quantity for the specified user and product
        sql = """
            UPDATE Carts
            SET quantity = quantity + ?
            WHERE user_id = ? AND product_id = ?
        """
        self.execute(sql, parameters=(quantity, user_id, product_id), commit=True)

    def get_cart_item(self, user_id, product_id):
        # Retrieve one cart item based on user_id and product_id
        sql = """
            SELECT * FROM Carts
            WHERE user_id = ? AND product_id = ?
        """
        return self.execute(sql, parameters=(user_id, product_id), fetchone=True)

    def get_cart_products(self, user_id: int):
        sql = """
            SELECT * FROM carts WHERE user_id = ?
        """

        return self.execute(sql, parameters=(user_id,), fetchall=True)

    def clear_cart(self, user_id: int):
        sql = """
        DELETE FROM Carts WHERE user_id = ?
        """
        self.execute(sql, parameters=(user_id,), commit=True)


# orders ------------------------------------------------------------------------------------------------------
    def create_table_orders(self):
        sql = """
        CREATE TABLE Orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,

            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL DEFAULT 1,
            
            full_name varchar(255) NOT NULL,
            phone_number varchar(255) NOT NULL,
            address varchar(255) NOT NULL,
            
            FOREIGN KEY (user_id) REFERENCES Users(id),
            FOREIGN KEY (product_id) REFERENCES Products(id)
        );
        """
        self.execute(sql, commit=True)

    def create_order(self, user_id: int, product_id: int, quantity: int, full_name: str, phone_number: str, address: str):
        sql = """
        INSERT INTO Orders (user_id, product_id, quantity, full_name, phone_number, address) VALUES (?, ?, ?, ?, ?, ?)
        """
        self.execute(sql, parameters=(user_id, product_id, quantity, full_name, phone_number, address), commit=True)

    def get_orders(self, user_id: int):
        sql = """
            SELECT * FROM Orders WHERE user_id = ?
        """

        return self.execute(sql, parameters=(user_id,), fetchall=True)


def logger(statement):
    print(f"""
_____________________________________________________        
Executing: 
{statement}
_____________________________________________________
""")