import os
import sys
sys.path.append(os.getcwd())  # NOQA

from pymongo.server_api import ServerApi
from pymongo.mongo_client import MongoClient


class MongoDB():
    uri = 'mongodb+srv://introtods:14EQseYaNc1ceOhR@laptop-price.wngpnbl.mongodb.net/'

    def __init__(self, cluster: str) -> None:
        self.client = MongoClient(self.uri, server_api=ServerApi('1'))

        # Get the cluster
        self.db = self.client[cluster]

    def get_db(self):
        return self.db

    def update_collection(self, collection_name: str, data):
        collection = self.db[collection_name]
        if isinstance(data, list):
            return collection.insert_many(data)
        elif isinstance(data, dict):
            return collection.insert_one(data)
        else:
            raise ValueError('Data must be a list or a dict')


if __name__ == '__main__':
    cluster = MongoDB(
        cluster='newegg'
    )

    collection = cluster.get_db()['laptops']

    print('Done')
