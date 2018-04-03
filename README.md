# sqs-aws-message-parser-in-python

(Design document is here : https://docs.google.com/document/d/1PGQsgCSt96Tda1MXLw-3GXoSmdL98mFHwhmuAJbTuEA/edit?usp=sharing
)

This project is to give a solution to message consumption from sqs in python and handle message processing failure cases and act in a more error-tolerant way.

In this solution we have 

1) requests-queue - which receives data from external environment

2) rejects-queue - which receives data that failed while being received from requests-queue and processed

# How is it processed ?

we have a set of consumer jobs to process items in requests-queue.

If the message processing is successful we delete the message from queue.In case, after it receives, if the processing fails, then it reposts the message to the rejects-queue.

Then we have set of consumer jobs to process items in rejects-queue. 

Here when these items in rejects-queue is processed successfully, then it deletes it from queue.
In case, after it processes if the processing fails, then you can do some custom activity like logging to slack.


# How to start this entire system ?

Just do 


    python main.py


this configures the Simple Queuing Service(SQS) with all the queues and then runs all the consumer jobs. The number of consumer jobs is configurable. It is found in config/configuration.py. Even the POOL_SIZE is configurable.

# What will happen when the message is received from the QUEUE ?

We have a set of tasks defined in the folder. You can define your own custom tasks by just dropping a file inside that folder. The file should have a class that inherits from Task class. Then create a function run inside it. This is what gets called when the message from queue is received. (Note: don't forget to fill the tasks.xml).

When a message is received from queue, all the tasks defined with default as false are are executed. When one of the tasks fail, then that task alone is again executed and if it again fails, then a message is sent to Slack channel.
(Note: you should configure slack channel properties in the task4_constants.py file) This task executed on continuous irrecoverable failures is the task defined in tasks.xml as 'default' true.


# We have sample tasks for the following already done for you

        1) Jira Issue creation

        2) Trello Card creation

        3) Slack Message sending

Note: If you want to use th above tasks, make sure you change the tasks.xml appropriately. Then also export the following environment variables

    export SLACK_API_TOKEN=<token>

    export SLACK_CHANNEL=<channelname>

    export JIRA_SERVER_URL=<serverurl>

    export JIRA_USERNAME=<username>

    export JIRA_PASSWORD=<password>

    export JIRA_PROJECT_KEY=<projectkey>

    export JIRA_ISSUE_TYPE=<issuetype>

    export TRELLO_KEY=<trellokey>

    export TRELLO_AUTH_TOKEN=<trelloauthtoken>

    export TRELLO_BOARD_ID=<trelloboard>

    export TRELLO_LIST_NAME=<trellolistname>

Note: If you are using rabbitmq in place of  Amazons Simple Queuing, use this repository https://github.com/HarishAtGitHub/rabbitmq-message-parser-in-python
