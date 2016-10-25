from common.task.task import Task
from tasks import task4_constants

class Task4(Task):

    @classmethod
    def run(cls, data):

        from slacker import Slacker
        # FIXME: DO better error handling - reason: time contraint
        slack = Slacker(task4_constants.SLACK_API_TOKEN)

        try:
            slack.chat.post_message(task4_constants.SLACK_CHANNEL, data)
        except Exception as e:
            return False
        print("Task 4 done : The default")
        return True