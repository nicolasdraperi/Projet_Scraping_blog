import pymongo
import json

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
db = myclient["articles"]
collection = db["posts"]

with open('articles.json', encoding="utf8") as file:
    file_data = json.load(file)

documents = list(file_data.values())

if documents:
    collection.insert_many(documents)
    print("finis :0")
