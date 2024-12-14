import mysql.connector

def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    
    return get_instance

@singleton
class db:
    def __init__(self):
        db_config = {
                "host":"db",
                "user":"user",
                "password":"password",
                "database":"MUSICFM",
                "port":3306
        }
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_size= 10,
                **db_config
            )
        except:
            print("Failed to connect")
    def connect(self):
        return self.pool.get_connection()
