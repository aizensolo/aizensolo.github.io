from sqlite3 import connect
import hashlib

from . import transactions

def get_top_by_money(db_name:str):
    db = connect(db_name)
    cursor = db.cursor()

    cursor.execute("SELECT NAME, BALANCE FROM USERS ORDER BY BALANCE DESC")
    result = cursor.fetchall()

    return result

def delete_trade_id(name:str, password:str, id:str, db_name:str):
    passhash = hashlib.sha256(password.encode()).hexdigest()
    db = connect(db_name)
    cursor = db.cursor()
    cursor.execute("SELECT 1 FROM USERS WHERE NAME=? AND PASSWORD=?", (name, passhash,))
    if cursor.fetchall()[0][0]:
        cursor.execute("DELETE FROM TRADE_IDS WHERE ID=? AND OWNER_NAME=?", (id, name))
        isok = cursor.rowcount
        cursor.close()
        db.commit()
        db.close()

        if isok == 1:
            return True
        return False
    cursor.close()
    db.close()
    return False

def search_trade_id(id:str, db_name:str):
    db = connect(db_name)
    cursor = db.cursor()
    cursor.execute("SELECT OWNER_NAME, COST FROM TRADE_IDS WHERE ID=?", (id,))
    result = cursor.fetchall()[0]
    cursor.close()
    db.close()

    return result

def is_tradepack_bought(name:str, db_name:str):
    db = connect(db_name)
    cursor = db.cursor()
    cursor.execute("SELECT TRADEPACK FROM SUBSCRIPTIONS WHERE NAME=?", (name,))
    result = cursor.fetchall()[0][0]
    cursor.close()
    db.close()

    if result==1:
        return True
    return False

def how_much_people_using_trade_system(db_name:str):
    db = connect(db_name)
    cursor = db.cursor()
    cursor.execute("SELECT DISTINCT OWNER_NAME FROM TRADE_IDS")
    result = cursor.fetchall()
    cursor.close()
    db.close()

    return result

def get_users(db_name:str):
    db = connect(db_name)
    cursor = db.cursor()
    cursor.execute("SELECT NAME FROM USERS")
    result = cursor.fetchall()
    cursor.close()
    db.close()

    return result

def get_economy_sum(db_name:str):
    db = connect(db_name)
    cursor = db.cursor()
    cursor.execute("SELECT SUM(BALANCE) FROM USERS")
    result = cursor.fetchall()[0][0]
    cursor.close()
    db.close()

    return result

def transfer_to_all(name:str, password:str, value:float, db_name:str):
    passhash = hashlib.sha256(password.encode()).hexdigest()

    db = connect(db_name)
    cursor = db.cursor()

    cursor.execute("SELECT 1 FROM USERS WHERE NAME=? AND PASSWORD=?", (name, passhash,))
    result = cursor.fetchall()[0][0]
    cursor.close()

    if result:
        peoplist = get_users(db_name)
        len_peoplist = len(peoplist)-1
        value_per_person = value/len_peoplist
        if len_peoplist:
            for str_fetched in peoplist:
                if str_fetched[0] == name:
                    continue
                value-=value_per_person
                isok = transactions.transfer(name, password, value_per_person, str_fetched[0], db_name)
                if not isok: break

        if value == 0:
            db.commit()
            db.close()
            return True
    db.close()
    return False


def buy_tradepack(name:str, password:str, value:float, db_name:str):
    passhash = hashlib.sha256(password.encode()).hexdigest()

    db = connect(db_name)
    cursor = db.cursor()
    cursor.execute("SELECT 1 FROM USERS WHERE NAME=? AND PASSWORD=?", (name, passhash,))
    result = cursor.fetchall()[0][0]

    if not result:
        cursor.close()
        db.close()
        return False
    
    peoplist = how_much_people_using_trade_system(db_name)
    len_peoplist = len(peoplist)-1
    if len_peoplist:
        value_per_person = value/len_peoplist
        for str_fetched in peoplist:
            if str_fetched[0] == name:
                continue
            value-=value_per_person
            if not transactions.transfer(name, password, value_per_person, str_fetched[0], db_name): break
        if value == 0:
            cursor.execute("UPDATE SUBSCRIPTIONS SET TRADEPACK=1 WHERE NAME=?", (name,))
            isok = cursor.rowcount
            cursor.close()
            db.commit()
            db.close()
            if isok:
                return True
            return False
   
    if transfer_to_all(name, password, value, db_name):
        cursor.execute("UPDATE SUBSCRIPTIONS SET TRADEPACK=1 WHERE NAME=?", (name,))
        isok = cursor.rowcount
        cursor.close()
        db.commit()
        db.close()
        if isok:
            return True
        return False
    return False

def get_trade_ids_by_user(name:str, db_name:str):
    db = connect(db_name)
    cursor = db.cursor()

    cursor.execute("SELECT ID FROM TRADE_IDS WHERE OWNER_NAME=?", (name,))
    results = cursor.fetchall()

    cursor.close()
    db.close()

    return results

def how_much_trade_ids_on_user(name:str, db_name:str):
    db = connect(db_name)
    cursor = db.cursor()

    cursor.execute("SELECT COUNT(ID) FROM TRADE_IDS WHERE OWNER_NAME=?", (name,))
    result = cursor.fetchall()[0][0]

    cursor.close()
    db.close()

    return result

def is_trade_id_avaliable(trade_id:str, db_name:str):
    db = connect(db_name)
    cursor = db.cursor()

    cursor.execute("SELECT 1 FROM TRADE_IDS WHERE ID=?", (trade_id,))
    result = cursor.fetchall()

    if result:
        return False
    return True

def create_trade_id(trade_id:str, creator_name:str, password:str, value:float, db_name:str):
    passhash = hashlib.sha256(password.encode()).hexdigest()

    db = connect(db_name)
    cursor = db.cursor()

    cursor.execute("SELECT 1 FROM USERS WHERE NAME=? AND PASSWORD=?", (creator_name, passhash,))
    result = cursor.fetchall()
    if result:
        cursor.execute("INSERT INTO TRADE_IDS VALUES(?, ?, ?)", (trade_id, value, creator_name,))
        isok = cursor.rowcount

        cursor.close()
        db.commit()
        db.close()

        if isok:
            return True
        return False
    return False
