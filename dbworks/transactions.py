from sqlite3 import connect
import hashlib

def check_balance(name:str, password:str, db_name:str):
    passhash = hashlib.sha256(password.encode()).hexdigest()

    db = connect(db_name)
    cursor = db.cursor()

    cursor.execute(f"SELECT BALANCE FROM USERS WHERE NAME=? AND PASSWORD=?", (name, passhash,))
    result = cursor.fetchall()

    cursor.close()
    db.close()

    if not result:
        return -1
    return result[0][0]

def transfer(name:str, password:str, value:float, endpoint:str, db_name:str):
    passhash = hashlib.sha256(password.encode()).hexdigest()

    db = connect(db_name)
    cursor = db.cursor()

    cursor.execute("SELECT BALANCE FROM USERS WHERE NAME=? AND PASSWORD=?", (name, passhash,))
    from_balance = cursor.fetchall()[0][0]

    cursor.execute("SELECT BALANCE FROM USERS WHERE NAME=?", (endpoint,))
    to_balance = cursor.fetchall()[0][0]

    cursor.execute("UPDATE USERS SET BALANCE=? WHERE NAME=? AND PASSWORD=?", (from_balance-value, name, passhash,))
    isok = cursor.rowcount

    cursor.execute("UPDATE USERS SET BALANCE=? WHERE NAME=?", (to_balance+value, endpoint,))
    isok += cursor.rowcount

    cursor.close()
    db.commit()
    db.close()

    if isok == 2:
        return True
    return False