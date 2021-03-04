# Flask RestX Google Calendar API
Documentation at http://localhost:5000/turno/doc

![APIs and Services](images/SwaggerFront.png)

## installation of dependencies

Create environment:

```python3 -m venv ./venv```

Activate environment:

```source ./venv/bin/activate```

Install dependencies:

```pip install -r requirements.txt```

Run the API:

```python3 run.py```

## Docker implementation

docker run --publish 5000:5000 --detach --name cal_api bubjanes/calendar_api:2.0

## Endpoints:

