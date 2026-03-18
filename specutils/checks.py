def check_trade_id_is_correct(trade_id:str):
    if not trade_id.isascii():
        return False
    if not trade_id.isalpha():
        return False
    
    return True