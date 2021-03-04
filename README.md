# Flask RestX Google Calendar API
Documentation at http://localhost:5000

![APIs and Services](images/SwaggerFront.png)

## installation of dependencies

Create environment:

```python3 -m venv ./venv```

Activate environment:

```source ./venv/bin/activate```

Install dependencies:

```pip install -r requirements.txt```

## Run the API:

```python3 run.py```

## Initial setup

### Step 1
Following instructions in **calendar_setup.md** to generate a token.pkl file. Place thsi pickle file in the directory **turnero/turno/tokens** .
### Step 2
Run the api. 
### Step 3
Using the swagger UI by going to **http://localhost:5000/auth/doc** and generating a new user name and password. The API will return your new hashed password. Paste that hashed password in the 
