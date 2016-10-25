from common.task.task import Task
from tasks import task4_constants

class SlackMessageSenderTask(Task):

    @classmethod
    def run(cls, data):

        from slacker import Slacker
        import os
        # FIXME: DO better error handling - reason: time contraint
        slack = Slacker(os.environ['SLACK_API_TOKEN'])

        try:
            slack.chat.post_message(os.environ['SLACK_CHANNEL'], data)
        except Exception as e:
            return False
        print("Slack message sending, Successful")
        return True
