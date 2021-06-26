from src.services.mongodb import db

def tear_down_task():
    db.tasks.delete_many({})