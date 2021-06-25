from .mongodb import db

def task_input(group_id: str, title: str, content: str, priority: int):
    """ Validates task values """
    pass

def create_task(user_id:str, group_id: str, title: str, content: str, priority: int):
    task_input(group_id, title, content, priority)

    task = {
        'user_id': user_id,
        'group_id': group_id,
        'title': title,
        'content': content,
        'priority': priority
    }

    db.tasks.insert_one(task)
    return task