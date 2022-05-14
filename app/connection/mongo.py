def get_database(db_name):
    from pymongo import MongoClient
    import pymongo

    CONNECTION_STRING = "mongodb://root:example@mongo:27017/"

    from pymongo import MongoClient
    client = MongoClient(CONNECTION_STRING)

    return client[db_name]
