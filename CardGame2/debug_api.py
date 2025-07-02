from CardGame2.data_manager import DataManager

def get_collection():
    return DataManager().get_collection()

def get_decks():
    return DataManager().get_decks()

def get_money():
    return DataManager().get_money()

def get_hero_collection():
    return DataManager().get_hero_collection() 