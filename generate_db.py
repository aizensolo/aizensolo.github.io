from sqlite3 import connect
from hashlib import sha256

db = connect("db")
cursor = db.cursor()

cursor.execute("CREATE TABLE USERS(NAME TEXT UNIQUE, PASSWORD TEXT, BALANCE FLOAT)")
cursor.execute("CREATE TABLE TRADE_IDS(ID TEXT UNIQUE, COST FLOAT, OWNER_NAME TEXT)")
cursor.execute("CREATE TABLE SUBSCRIPTIONS(NAME TEXT UNIQUE, TRADEPACK BOOLEAN, NOADS BOOLEAN)")

users_sql = [
    ("Plushka_Legend", sha256("uela".encode()).hexdigest(), 1000),
    ("_DarTone_", sha256("DARTONE".encode()).hexdigest(), 1000)
]

cursor.executemany("INSERT INTO USERS VALUES(?,?,?)", users_sql)

cursor.execute("SELECT NAME FROM USERS")
names = cursor.fetchall()

for row in names:
    cursor.execute("INSERT INTO SUBSCRIPTIONS VALUES(?,?,?)", (row[0], False, False))
    print(cursor.rowcount)

cursor.close()
db.commit()
db.close()