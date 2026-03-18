# from dbworks.login import check_is_username_exists
# from sqlite3 import connect

# db = connect('db')
# cursor = db.cursor()

from dbworks import varied

# cursor.execute("CREATE TABLE USERS(NAME TEXT, VALUE TEXT)")
# cursor.executemany("INSERT INTO USERS VALUES(?, ?)", 
# [
#     ("A", "A",),
#     ("B", "B",)
# ]
# )

# cursor.close()
# db.commit()
# db.close()

# print(check_is_username_exists("' OR 1=1--", "db"))

# chars = "charsisasci  __ &&ihhhh   "

# print(chars.isascii())
# print(chars.isalpha())

# cursor.execute("SELECT COUNT(ID) FROM TRADE_IDS WHERE OWNER_NAME=?", ("GG",))
# result = cursor.fetchall()

# print(result)

# cursor.close()
# db.close()

# res = varied.buy_tradepack("Plushka_Legend", "uela", 210, "db")

# print(res)


import sqlite3

db = sqlite3.connect("db")
cursor = db.cursor()

# cursor.execute("SELECT * FROM SUBSCRIPTIONS")
# print(cursor.fetchall())

cursor.execute("DELETE FROM TRADE_IDS WHERE ID='Ha'")

cursor.close()
db.commit()
db.close()
