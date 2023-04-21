import os
import dialogflow
import mysql.connector
import json

if __name__ == '__main__':
    # Access database
    cnx = mysql.connector.connect(user='root', password='67048Rc!', host='Richards-MacBook-Pro-2.local', database='DialogFlow')
    cursor = cnx.cursor(buffered=True)
    cursor2 = cnx.cursor(buffered=True)
    cursor3 = cnx.cursor(buffered=True)
    # Dialogflow
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'private_key.json'
    DIALOGFLOW_PROJECT_ID = 'dialogflow-demo-eflx'

    # Clear DFintent and DFleadsTo tables
    cursor.execute("DELETE FROM DFleadsTo WHERE parentIID > 0")
    cursor.execute("DELETE FROM DFintent WHERE iid > 0")
    cnx.commit()

    # Insert welcome intent
    query = "SELECT * FROM question WHERE qid = 1"
    cursor.execute(query)
    query = "INSERT INTO DFintent(iid, resp_txt, inputCtx, outputCtx, params) values\n"
    for (qid, text) in cursor:
        query += "(1,\"" + text + "\"," + "'[]','[1]','[]')"
    cursor.execute(query)
    cnx.commit()

    # Fill DFintent table
    query = "SELECT * FROM question WHERE qid > 1"
    cursor.execute(query)
    query = "INSERT INTO DFintent(resp_txt, inputCtx, outputCtx, params) values\n"
    for (qid, text) in cursor:
        cursor2.execute("SELECT * FROM leadsTo WHERE childQID = " + str(qid))
        outputCtx = "[" + str(qid) + "]"
        params = "[]"
        parents = []
        for (parentQID, childQID, response) in cursor2:
            if parents.count(parentQID) == 0:
                parents.append(parentQID)
                inputCtx = "[" + str(parentQID) + "]"
            query += "(\"" + text + "\",'" + inputCtx + "','" + outputCtx + "','" + params + "'),\n"
    query = query[:-2]
    query += ";"
    cursor.execute(query)
    cnx.commit()

    # Fill DFleadsTo
    query = "SELECT * FROM leadsTo"
    cursor.execute(query)
    query = "INSERT INTO DFleadsTo(parentIID, childIID) values\n"
    for (parentQID, childQID, response) in cursor:
        cursor2.execute("SELECT * FROM DFintent WHERE JSON_CONTAINS(outputCtx,'" +
                        str(parentQID) + "')")
        for (iid, resp_txt, inputCtx, outputCtx, params) in cursor2:
            parentIID = iid
        cursor2.execute("SELECT * FROM DFintent WHERE JSON_CONTAINS(inputCtx,'" +
                        str(parentQID) + "') AND JSON_CONTAINS(outputCtx,'" + str(childQID) + "')")
        for (iid, resp_txt, inputCtx, outputCtx, params) in cursor2:
            childIID = iid
        query += "(" + str(parentIID) + "," + str(childIID) + "),\n"
    query = query[:-2]
    query += ";"
    cursor.execute(query)
    cnx.commit()

    # Creating intents
    intents_client = dialogflow.IntentsClient()
    parent = intents_client.project_agent_path(DIALOGFLOW_PROJECT_ID)
    cursor.execute("SELECT * FROM DFintent")
    for (iid, resp_txt, inputCtx, outputCtx, params) in cursor:
        # Set up intent message
        messages = []
        text = dialogflow.types.Intent.Message.Text(text=[resp_txt])
        text_message = dialogflow.types.Intent.Message(text=text)
        messages.append(text_message)

        # Set up intent contexts
        input_contexts = json.loads(inputCtx)
        output_contexts = json.loads(outputCtx)
        input_context_names = []
        for context in input_contexts:
            ctx_name = "projects/" + DIALOGFLOW_PROJECT_ID + "/agent/sessions/-/contexts/" + str(context)
            input_context_names.append(ctx_name)
        for context in output_contexts:
            output_context = "projects/" + DIALOGFLOW_PROJECT_ID + "/agent/sessions/-/contexts/" + str(context)
            output_context_names = [dialogflow.types.Context(name=output_context, lifespan_count=1)]

        # Set up intent training phrases
        phrases = []
        for context in input_contexts:
            cursor2.execute("SELECT * FROM question WHERE text = \"" + resp_txt + "\"")
            for (qid, text) in cursor2:
                childID = qid
            cursor2.execute("SELECT * FROM DFintent WHERE JSON_CONTAINS(outputCtx,'" + str(context) + "')")
            for (iid2, resp_txt2, inputCtx2, outputCtx2, params2) in cursor2:
                cursor3.execute("SELECT * FROM question WHERE text = \"" + resp_txt2 + "\"")
                for (qid, text) in cursor3:
                    parentID = qid
            cursor2.execute("SELECT * FROM leadsTo where parentQID = " + str(parentID) + " AND childQID = " +
                            str(childID))
            for (parentQID, childQID, response) in cursor2:
                phrases.append(response)
        training_phrases = []
        if not input_contexts:
            phrases = ["Hello", "Hi", "I feel sick"]
        for phrase in phrases:
            part = dialogflow.types.Intent.TrainingPhrase.Part(text=phrase)
            training_phrase = dialogflow.types.Intent.TrainingPhrase(parts=[part])
            training_phrases.append(training_phrase)

        # Create intent
        name = resp_txt[:50] + str(iid)
        parameter = dialogflow.types.Intent.Parameter(display_name='value', is_list=False, value='#')
        intent = dialogflow.types.Intent(display_name=name, messages=messages,
                                         input_context_names=input_context_names, output_contexts=output_context_names,
                                         training_phrases=training_phrases, parameters=[parameter])
        response = intents_client.create_intent(parent, intent)

    cursor.close()
    cursor2.close()
    cnx.close()
