import xml.etree.ElementTree as ET
from config.configuration import *
import importlib
from logger.logger_util import *

class TaskExecutor:

    @classmethod
    def execute(cls, data, tast_list = None, default=False):

        logger = getLogger()
        tasks = cls.get_tasks(default=default)
        results = []
        for task in tasks:
            try:
                # FIXME : The loop can be made correct
                if(tast_list != None):
                    if(task.__name__ in tast_list):
                        result = task.run(data)
                    else:
                        continue
                else:
                    result = task.run(data)
                if(result):
                    logger.debug(task.__name__ + ' : Successful Execution')
                else:
                    logger.debug(task.__name__ + ' : Failed Execution')
                results.append({task.__name__: result})
            except NotImplementedError as nie:
                logger.debug('Seems like you have not implemeneted run function in ' + task.__name__ +
                            '. Please implement it.')
                results.append({task.__name__: False})
        return results

    @classmethod
    def parse_tasks_xml(cls):
        tree = ET.parse(TASKS_XML_FILE)
        return tree.getroot()

    @classmethod
    def get_tasks(cls, default=False):
        tasks_element = cls.parse_tasks_xml()
        task_classes = []
        for task_element in tasks_element:

            file_name = task_element.find('filename').text
            class_name = task_element.find('classname').text
            if(default):
                # load only default tasks
                if(task_element.find('default').text == 'true'):
                    module = importlib.import_module('tasks.' + file_name)
                    task_class = getattr(module, class_name)
                    task_classes.append(task_class)
                continue
            if (task_element.find('default').text == 'false'):
                module = importlib.import_module('tasks.' + file_name)
                task_class = getattr(module, class_name)
                task_classes.append(task_class)
        return task_classes
