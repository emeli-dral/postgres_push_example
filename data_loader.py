import datetime
import random
import time
import logging
import uuid
import pandas as pd
import requests
import zipfile
import io

from evidently import ColumnMapping
from evidently.report import Report
from evidently.metrics import DatasetMissingValuesMetric, DatasetDriftMetric, DatasetSummaryMetric

import psycopg

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

SEND_TIMEOUT = 10

rand = random.Random()

# data loading
content = requests.get("https://archive.ics.uci.edu/ml/machine-learning-databases/00275/Bike-Sharing-Dataset.zip").content
with zipfile.ZipFile(io.BytesIO(content)) as arc:
    raw_data = pd.read_csv(arc.open("day.csv"), header=0, sep=',', parse_dates=['dteday'], index_col='dteday')

# create report
reference_data = raw_data.loc['2011-01-01 00:00:00':'2011-01-28 23:00:00']
begin = datetime.datetime(2011,1,20,0,0)
end = datetime.datetime(2011,1,20,23,59)

report = Report(metrics=[
    DatasetMissingValuesMetric(), 
    DatasetDriftMetric(), 
    DatasetSummaryMetric()
])

create_table_statement = """
drop table if exists metric_name;
create table metric_name(
    timestamp timestamp,
    number_of_drifted_columns integer,
    number_of_almost_duplicated_columns integer,
    number_of_missing_values integer
)
"""

def prep_db():
    with psycopg.connect("host=localhost port=5432 user=postgres password=example", autocommit=True) as conn:
        res = conn.execute("SELECT 1 FROM pg_database WHERE datname='test'")
        if len(res.fetchall()) == 0:
            conn.execute("create database test;")
    with psycopg.connect("host=localhost port=5432 dbname=test user=postgres password=example") as conn:
        conn.execute(create_table_statement)


def calculate_metrics_postgresql(i, curr):
    current_data = raw_data[begin + datetime.timedelta(i) : end + datetime.timedelta(i)]
    report.run(reference_data=reference_data, current_data=current_data)
    result = report.as_dict()

    drift = result['metrics'][1]['result']['number_of_drifted_columns']
    duplicated_cols = result['metrics'][2]['result']['current']['number_of_almost_duplicated_columns']
    missing_values = result['metrics'][0]['result']['number_of_missing_values']
    
    curr.execute(
        "insert into metric_name(timestamp, number_of_drifted_columns, number_of_almost_duplicated_columns, number_of_missing_values) values (%s, %s, %s, %s)",
        (datetime.datetime.now(), drift, duplicated_cols, missing_values)
    )


def main():
    prep_db()
    last_send = datetime.datetime.now() - datetime.timedelta(seconds=10)
    with psycopg.connect("host=localhost port=5432 dbname=test user=postgres password=example", autocommit=True) as conn:
        for i in range(0, 100):
            with conn.cursor() as curr:
                calculate_metrics_postgresql(i, curr)
            # this sends all metrics with TIMEOUT
            new_send = datetime.datetime.now()
            seconds_elapsed = (new_send - last_send).total_seconds()
            if seconds_elapsed < SEND_TIMEOUT:
                time.sleep(SEND_TIMEOUT - seconds_elapsed)
            while last_send < new_send:
                last_send = last_send + datetime.timedelta(seconds=10)
            logging.info("data sent")


if __name__ == '__main__':
    main()
