from bson.objectid import ObjectId

from .mongodb import db

def validate(group_id: str, title: str, content: str, priority: int):
    """ Validates task values """
    pass

def create_task(user_id: str, group_id: str, title: str, content: str, priority: int):
    validate(group_id, title, content, priority)

    task = {
        'user_id': ObjectId(user_id),
        'group_id': group_id,
        'title': title,
        'content': content,
        'priority': priority,
        'log': []
    }

    db.tasks.insert_one(task)
    return task

def list_tasks_by_group(group_id: str):
    tasks = []
    
    for data in db.tasks.aggregate([
        { '$match': { 'group_id': group_id } },
        { 
            '$lookup': {
                'from': 'users',
                'let': { 'id': '$user_id' },
                'as': 'created_by',
                'pipeline': [
                    { '$match': { '$expr': { '$eq': [ '$_id', '$$id' ] } } },
                    { '$project': { '_id': 0, 'username': 1 }}
                ],
            }
        },
        { '$unwind': '$created_by' }
    ]):
        tasks.append(data)

    return tasks