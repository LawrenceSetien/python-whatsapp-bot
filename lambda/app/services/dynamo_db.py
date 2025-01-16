import os
import time
import boto3
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION_NAME = os.getenv("AWS_REGION_NAME")


def dynamodb_table_connector() -> object:
    """
    Connects to an Amazon DynamoDB table and returns the table resource.

    Returns:
        A DynamoDB Table resource connected to the specified table.
    """
    # Initialize a session using Amazon DynamoDB
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION_NAME
    )

    # Get the service resource
    dynamodb = session.resource('dynamodb')

    # Specify the DynamoDB table
    table = dynamodb.Table('whatsapp-chatbot')

    return table


def store_thread(wsp_id: str, thread_id: str) -> None:
    """
    Stores a thread in a DynamoDB table with metadata, including timestamps and time-to-live.

    Args:
        wsp_id: The unique identifier for the WhatsApp session.
        thread_id: The unique identifier for the thread to be stored.

    """

    table = dynamodb_table_connector()
    current_time = int(time.time())

    # Convert Unix timestamp to datetime object
    dt = datetime.fromtimestamp(current_time)

    # Format datetime object to a human-readable string
    date_time = dt.strftime('%Y-%m-%d %H:%M:%S')

    # Define the data to be inserted
    item = {
        'chatbot_partition_key': wsp_id,
        'chatbot_sort_key': 'chatbot-key',
        'thread_id': thread_id,
        'created_at': date_time,
        'time_to_live': current_time + 86400
    }

    # Insert the data into the table
    table.put_item(Item=item)
    print(f"item saved: {item}")


def check_if_thread_exists(wsp_id: str):
    """
    Checks if a thread exists in the DynamoDB table for a given WhatsApp session ID.

    Args:
        wsp_id: The unique identifier for the WhatsApp session.

    Returns:
        The 'thread_id' if a thread exists for the specified `wsp_id`, otherwise None.
    """

    table = dynamodb_table_connector()

    # Query the table for the specific item
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('chatbot_partition_key').eq(wsp_id)
    )

    # Extract the items from the response
    items = response.get('Items', [])

    # Check if items were found and return the 'thread_id' if it exists
    if items:
        # Assuming 'thread_id' is one of the attributes in the item
        print(f"items retrieved: {items}")

        return items[0].get('thread_id', None)

    return None

