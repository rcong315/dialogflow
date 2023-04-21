import os
import dialogflow

if __name__ == '__main__':
    # Dialogflow
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'private_key.json'
    DIALOGFLOW_PROJECT_ID = 'dialogflow-demo-eflx'
    intents_client = dialogflow.IntentsClient()
    parent = intents_client.project_agent_path(DIALOGFLOW_PROJECT_ID)
    intents = intents_client.list_intents(parent)
    intents_client.batch_delete_intents(parent, intents)