from common.task.task import Task

class Task3(Task):

    @classmethod
    def run(cls, data):
        print("Task 3 done")
        return False