from common.task.task import Task

class Task1(Task):

    @classmethod
    def run(cls):
        print("Task 1 done")
        return True