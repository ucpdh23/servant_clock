import boto3
import json
import schedule
import time
import datetime
import os
import platform
import socket
import paho.mqtt.client as mqtt

def load_config(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def get_aws_cost(region, access_key_id, secret_access_key):
    client = boto3.client('ce', region_name=region,
                          aws_access_key_id=access_key_id,
                          aws_secret_access_key=secret_access_key)

    # Get the current date
    end = datetime.datetime.utcnow()
    start = end - datetime.timedelta(days=1)  # For the last 24 hours

    # Get the cost and convert it to JSON
    cost_response = client.get_cost_and_usage(
        TimePeriod={'Start': start.strftime('%Y-%m-%d'), 'End': end.strftime('%Y-%m-%d')},
        Granularity='DAILY',
        Metrics=['BlendedCost']
    )

    return json.dumps(cost_response, indent=2)


def publish_to_mqtt(message, broker_host, broker_port, username, password, topic):
    client = mqtt.Client()
    client.username_pw_set(username, password)
    client.connect(broker_host, broker_port)
    client.publish(topic, message)
    client.disconnect()


def job():
    config = load_config('config.json')
    aws_config = config['aws']
    mqtt_config = config['mqtt']

    aws_cost = get_aws_cost(**aws_config)
    publish_to_mqtt(aws_cost, **mqtt_config)


if __name__ == "__main__":
    # Schedule the job to run daily
    schedule.every().day.at("00:00").do(job)

    # Run the scheduler
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


