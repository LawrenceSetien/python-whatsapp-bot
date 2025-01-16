import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from .dynamo_db import store_thread, check_if_thread_exists

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")
client = OpenAI(api_key=OPENAI_API_KEY)
thread_status = {}

def run_assistant(thread, name):
    """
    Runs an OpenAI Assistant thread and retrieves its response.

    Args:
        thread: The thread object for the assistant interaction.
        name: The name of the user interacting with the assistant.

    Returns:
        The text response from the assistant after the thread run is completed.
    """

    # Retrieve the Assistant
    assistant = client.beta.assistants.retrieve(OPENAI_ASSISTANT_ID)

    # Run the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        # instructions=f"You are having a conversation with {name}",
    )

    # Wait for completion
    while run.status != "completed":
        # Be nice to the API
        time.sleep(0.5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)

    # Retrieve the Messages
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    new_message = messages.data[0].content[0].text.value
    return new_message


def set_thread_active(thread_id, is_active):
    """Set the active status of a thread."""
    thread_status[thread_id] = is_active

def is_thread_active(thread_id):
    """Check if the thread is currently active."""
    return thread_status.get(thread_id, False)

def generate_response(message_body, wsp_id, name):
    """
    Generates a response from the OpenAI Assistant for a given message.

    Args:
        message_body: The content of the user's message.
        wsp_id: The unique identifier for the WhatsApp session.
        name: The name of the user interacting with the assistant.

    Returns:
        The assistant's response as a string.
    """

    # Check if there is already a thread_id for the wsp_id
    thread_id = check_if_thread_exists(wsp_id)

    # If a thread doesn't exist, create one and store it
    if thread_id is None:
        thread = client.beta.threads.create()
        store_thread(wsp_id, thread.id)
        thread_id = thread.id

    # Otherwise, retrieve the existing thread
    else:
        thread = client.beta.threads.retrieve(thread_id)

    # Check if the thread is currently active
    if is_thread_active(thread_id):
        # Wait until the thread is no longer active
        while is_thread_active(thread_id):
            time.sleep(1)

    # Mark the thread as active
    set_thread_active(thread_id, True)

    try:
        # Add message to thread
        client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message_body,
        )

        # Run the assistant and get the new message
        new_message = run_assistant(thread, name)

    finally:
        # Mark the thread as inactive
        set_thread_active(thread_id, False)

    return new_message


