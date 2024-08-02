"""A small example of sending emails using AWS."""

import os
from dotenv import load_dotenv
from boto3 import client
import argparse

load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")

START_MESSAGE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
    </head>
    <body>
        <marquee><h1 style="color:chartreuse;border:3px dashed hotpink;background-color:chocolate;max-width:100px;text-align:center;">A new data set is being processed</h1></marquee>
    </body>
    </html>
"""
COMPLETE_MESSAGE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
    </head>
    <body>
        <marquee><h1 style="color:chartreuse;border:3px dashed hotpink;background-color:chocolate;max-width:100px;text-align:center;">A new dataset has been processed</h1></marquee>
    </body>
    </html>
"""

def get_args():
    parser = argparse.ArgumentParser(description="Send an email using AWS SES.")
    parser.add_argument('--process_start', action='store_true', help="Flag to indicate the start of the process.")
    return parser.parse_args()

def setup_client():
    ses = client("ses", aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
    return ses

def notify(ses, process_start: bool):
    msg = START_MESSAGE if process_start else COMPLETE_MESSAGE
    
    ses.send_email(
        Source='trainee.joshua.marden@sigmalabs.co.uk',
        Destination={
            'ToAddresses': [
                'trainee.joshua.marden@sigmalabs.co.uk',
            ]
        },
        Message={
            'Subject': {
                'Data': 'Hi!',
            },
            'Body': {
                'Html': {
                    'Data': msg,
                }
            }
        },
    )

def main():
    args = get_args()
    ses = setup_client()
    notify(ses, args.process_start)

if __name__ == "__main__":
    main()
 