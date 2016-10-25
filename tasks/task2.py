from common.task.task import Task

class Task2(Task):

    @classmethod
    def run(cls, data):
        print("Task 2 done")
        return True