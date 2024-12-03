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
    def __init__(self, config):
        self.pool = mysql.connector.pooling.MySQLConnectionPool(**config)
    
    def connect(self):
        return self.pool.get_connection()
