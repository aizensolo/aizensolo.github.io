from sqlite3 import connect
import hashlib

def check_is_username_exists(name:str, db_name:str):
    db = connect(db_name)
    cursor = db.cursor()

    cursor.execute(f"SELECT 1 FROM USERS WHERE NAME=?", (name,))
    result = cursor.fetchall()

    cursor.close()
    db.close()

    if result:
        return True
    return False

def check_is_valid_password(name:str, password:str, db_name:str):
    passhash = hashlib.sha256(password.encode()).hexdigest()

    db = connect(db_name)
    cursor = db.cursor()

    cursor.execute(f"SELECT 1 FROM USERS WHERE NAME=? AND password=?", (name, passhash,))
    result = cursor.fetchall()

    cursor.close()
    db.close()

    if result:
        return True
    return False

def update_password(name:str, oldpassword:str, newpassword:str, db_name:str):
    old_passhash = hashlib.sha256(oldpassword.encode()).hexdigest()
    new_passhash = hashlib.sha256(newpassword.encode()).hexdigest()

    db = connect(db_name)
    cursor = db.cursor()

    cursor.execute(f"UPDATE USERS SET PASSWORD=? WHERE NAME=? AND PASSWORD=?", (new_passhash, name, old_passhash,))
    rows_affected = cursor.rowcount

    cursor.close()
    db.commit()
    db.close()

    if rows_affected:
        return True
    return False