# Running locally

### Requirements  
- Python 3
- VirtualEnv

### Setup the environment

> 1. **Setup**
Create a *.env* file containing the following:

```
SECRET_KEY=secret
MONGO_URI=mongodb://localhost:27017/weminder-api-db
```

> 2. **Running the API**

1. Create a new Virtual Env: py -m venv venv
2. Activate Virtual Env: .\venv\Scripts\activate
2. Install dependencies: pip install -r requirements.txt
3. Start the API by running: py .\src\app.py

> 3. **Testing**

```
pytest --cov=src

----------- coverage: platform win32, python 3.9.1-final-0 -----------
Name                         Stmts   Miss  Cover
------------------------------------------------
src\app.py                      76      3    96%
src\controller\__init__.py       4      0   100%
src\controller\check.py          3      0   100%
src\controller\group.py         45      3    93%
src\controller\task.py          43      0   100%
src\controller\user.py          56      6    89%
src\errors\__init__.py          20      0   100%
src\services\__init__.py         7      0   100%
src\services\group.py           62      8    87%
src\services\mongodb.py          5      0   100%
src\services\task.py            83      4    95%
src\services\user.py            39      0   100%
------------------------------------------------
TOTAL                          443     24    95%
```