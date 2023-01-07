import sqlite3

# Connecting to sqlite
conn = sqlite3.connect("AuctionAndBid_Sys.db")

# Creating a cursor object using the cursor() method
cursor = conn.cursor()

# Doping EMPLOYEE table if already exists
cursor.execute("DROP TABLE <Table_Name>")
print("Table dropped... ")

# Commit your changes in the database
conn.commit()

# Closing the connection
conn.close()


"""
To create tables from python Classes, through Command Line use below commands:
Run below commands in CMD after reaching the SellerApp directory
1. python3
2. from app import db
3. db.create_all()
"""


"""
Access Sqlite Database AuctionAndBid_Sys.db through Command Line using below commands:
Run below commands in CMD after reaching the SellerApp directory
1. sqlite3 AuctionAndBid_Sys.db
2. .tables
3. select * from AuctionsData;

Similar to the above SELECT query all other SQL queries executed.
"""
