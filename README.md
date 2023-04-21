IMPLEMENTATION
    SQL queries to create the tables are in create_tables.sql and queries to insert into the tables are in insert.sql.

    My program first accesses the MySQL database. It assumes the DFleadsTo and DFintent tables already exists. It clears those tables and then proceeds to fill the DFintent table first by using the records from the question table. The program assumes that the first question has a qid of 1 so that it knows which question corresponds to the welcome intent. The welcome intent will be created with the training phrases “Hi”, “Hello”, and “I feel sick.” Duplicate intents may be created for questions that may need different training phrases and different input contexts. After filling the DFintent table, the program uses that table and the leadsTo table to fill the DFleadsTo table.

    After filling the tables, the program connects with a Dialogflow agent and creates the intents in the DFintents table. It then trains the intents with their respective training phrases which are retrieved from the response field in the leadsTo table.

    My implementation correctly follows the decision tree provided when given responses matching those of the training phrases.

TO RUN
    1. Code is in “api.py”
    2. Fill in user, password, host, and database parameters for MySQL database in line 8
    3. Fill in path of private key in line 13
    4. Fill in DialogFlow project ID in line 14
    5. Run “api.py”
    *delete.py can be run to delete all intents