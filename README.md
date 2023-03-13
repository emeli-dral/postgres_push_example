# postgres_push_example
An example of data monitoring setup using Evidently tool, Postgres DG and Grafana service.
<img width="1440" alt="Evidently_Postgres_Grafana_dashboard" src="https://user-images.githubusercontent.com/22995068/224705517-4e6f4a59-37a1-45f2-ae20-d9cf2d33eaef.png">

## Prerequisites
You need following tools installed:
- [docker](https://docs.docker.com/get-docker) 
- docker-compose (included to Docker Desktop for Mac and Docker Desktop for Windows )

## Preparation
Note: all actions expected to be executed in repo folder.

Create virtual environment and activate it (eg. python -m venv venv && ./venv/bin/activate)

Install required packages pip install -r requirements.txt

## Starting services
Go to the project directory and run the following command from the terminal: ```docker-compose up --build``` 
Note:
- to stop the docker later, run: docker-compose down;
- to rebuild docker image (for example, to get the latest version of the libraries) run: docker compose build --no-cache

## Sending Data
To start sending data to service, execute:
```python data_loader.py```

This script will expose a single batch of calculated metrics through prometheus pushgateway every 10 seconds

## Setting up Dashboards
- Run the example using the above instructions
- Open the Grafana web interface (localhost:3000)
- Create new Dashboard, add a Panel, and make sure you selected PostgreSQL as a source
<img width="1138" alt="Screenshot 2023-03-13 at 12 51 38" src="https://user-images.githubusercontent.com/22995068/224707080-bdbd8188-bd6d-499a-9923-2307bb0d5886.png">

- Customize visuals in the Grafana interface
<img width="1378" alt="Screenshot 2023-03-13 at 12 47 25" src="https://user-images.githubusercontent.com/22995068/224706196-7ef951ff-a539-4829-a2bf-b52fcdc8ef50.png">

- Apply your changes to the Dashboard and check that you like what you see :)
- Click the button "save" from the Grafana Top Menu. This will open a dialog window. Select the option "Download JSON" to save the configurations in the JSON file if like to reuse it later.
