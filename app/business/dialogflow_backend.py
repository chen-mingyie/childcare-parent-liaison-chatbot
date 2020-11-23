import dialogflow_v2 as dialogflow
import os

PROJECT_ID = os.environ['PROJECT_ID']

def get_intent(session_id, text):
    """Returns the result of detect intent with texts as inputs.
    Using the same `session_id` between requests allows continuation
    of the conversation."""
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(PROJECT_ID, session_id)
    # print('Session path: {}\n'.format(session))
    text_input = dialogflow.types.TextInput(text=text, language_code='en-US')
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = session_client.detect_intent(session=session, query_input=query_input)
    return response