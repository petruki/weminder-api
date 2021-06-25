# Running locally

### Requirements  
- Python 3
- VirtualEnv

### Setup the environment

> 1. **Setup**
Create a *.env* file containing the following:

```
SECRET_KEY=secret
MONGO_URI=mongodb://localhost:27017/reminder-api
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
src\app.py                      51      1    98%
src\controller\__init__.py       4      0   100%
src\controller\auth.py          35      2    94%
src\controller\check.py          3      0   100%
src\controller\group.py         34     10    71%
src\controller\task.py          10      2    80%
src\errors\__init__.py          20      6    70%
src\model\__init__.py            4      0   100%
src\services\__init__.py         7      0   100%
src\services\auth.py            21      0   100%
src\services\group.py           30      4    87%
src\services\mongodb.py          5      0   100%
src\services\task.py             8      0   100%
------------------------------------------------
TOTAL                          232     25    89%
```