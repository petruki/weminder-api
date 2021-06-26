import bson
from datetime import datetime

from .mongodb import db
from bson.objectid import ObjectId
from errors import BadRequestError, NotFoundError

def validate(
    group_id = None, 
    title = None, 
    content = None, 
    priority = None,
    task_id = None
):
    """ Validates task values """

    if title is not None and len(title) == 0:
        raise BadRequestError('Title cannot be empty')

    if content is not None and len(content) == 0:
        raise BadRequestError('Content cannot be empty')

    if priority is not None and (priority < 0 or priority > 5):
        raise BadRequestError('Priority must be between 0 and 5')

    if task_id is not None:
        if len(task_id) == 0:
            raise BadRequestError('Task ID cannot be empty')

        if not bson.objectid.ObjectId.is_valid(task_id):
            raise BadRequestError('Invalid Task ID')

    if group_id is not None:
        if len(group_id) == 0:
            raise BadRequestError('Group ID cannot be empty')

        if not bson.objectid.ObjectId.is_valid(group_id):
            raise BadRequestError('Invalid Group ID')

def create_task(user_id: str, group_id: str, title: str, content: str, priority: int):
    validate(group_id, title, content, priority)

    task = {
        'user_id': ObjectId(user_id),
        'group_id': ObjectId(group_id),
        'title': title,
        'content': content,
        'priority': priority,
        'log': []
    }

    db.tasks.insert_one(task)
    return task

def list_tasks_by_group(group_id: str):
    validate(group_id=group_id)

    tasks = []
    for data in db.tasks.aggregate([
        { '$match': { 'group_id': ObjectId(group_id) } },
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

def update_task(
    task_id: str, 
    title = None, 
    content = None, 
    priority = None
):
    validate(task_id=task_id, title=title, content=content)

    time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

    changes = []
    update = { '$set': {} }
    if title is not None:
        update['$set']['title'] = title
        changes.append(f"{time}: Title has changed to {title}")
    if content is not None:
        update['$set']['content'] = content
        changes.append(f"{time}: Content updated")
    if priority is not None:
        update['$set']['priority'] = priority
        changes.append(f"{time}: Priority has changed to {priority}")

    if len(changes) > 0:
        update['$push'] = { 'log': { '$each':  changes } }
    
    result = db.tasks.update_one({ '_id': ObjectId(task_id) }, update)
    if result.modified_count == 1:
        return db.tasks.find_one({ '_id': ObjectId(task_id) })