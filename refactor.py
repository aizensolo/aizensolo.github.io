from sqlite3 import connect
from hashlib import sha256

db = connect("db")
cursor = db.cursor()
cursor.execute("CREATE TABLE TRADE_IDS(ID TEXT UNIQUE, COST FLOAT, OWNER_NAME TEXT)")
cursor.execute("CREATE TABLE SUBSCRIPTIONS(NAME TEXT UNIQUE, TRADEPACK INTEGER, NOADS INTEGER)")

cursor.execute("SELECT NAME FROM USERS")
result = cursor.fetchall()

for row in result:
    cursor.execute("INSERT INTO SUBSCRIPTIONS VALUES(?,?,?)", (row[0], 0, 0))

cursor.execute("SELECT NAME, PASSWORD FROM USERS")
result = cursor.fetchall()

for row in result:
    cursor.execute("UPDATE USERS SET PASSWORD=? WHERE NAME=?", (sha256(row[1]).hexdigest(), row[0]))

cursor.close()
db.commit()
db.close()