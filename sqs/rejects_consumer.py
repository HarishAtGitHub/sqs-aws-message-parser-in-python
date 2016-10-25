from common.msgqueue.consumer import Consumer
from logger.logger_util import *
from sqs.sqs_util import SQS
from common.task.task_executor import TaskExecutor

class RejectsConsumer(Consumer):

    def __init__(self,id):
        logger = getLogger()
        self.connection = SQS.get_connection()
        self.id = id
        print('Successfully initialized Rejects Consumer :' + str(self.id))
        logger.info('Successfully initialized Rejects Consumer ' + str(self.id))

    def start(self):
        logger = getLogger()
        while True:
            logger.debug('Rejects Consumer : ' + str(self.id) +
                        ' is subscribing to queue : ' + DEAD_LETTER_QUEUE)
            message = self.connection.receive_message(
                QueueUrl=SQS.get_deadletter_q_url(),
                MaxNumberOfMessages=1,
                VisibilityTimeout=30,
                WaitTimeSeconds=20,
                MessageAttributeNames=[
                    'past_results',
                ]
            )
            self.callback(message)

    def stop(self):
        pass

    @staticmethod
    def callback(message):
        logger = getLogger()
        try:
            message_payload = message['Messages'][0] # because we get only one message
            body = message_payload['Body']
            receipt_handle = message_payload['ReceiptHandle']
            tast_list = []
            try:
                message_attributes = message_payload['MessageAttributes']['past_results']
                import ast
                past_results = ast.literal_eval(message_attributes['StringValue'])
                for i in past_results:
                    for key, value in i.items():
                        if (not value):
                            tast_list.append(key)
            except KeyError as e:
                logger.debug('The message does not have MessageAttributes - past_results')

        except KeyError as e:

            logger.debug(" Message received from requests queue was not of required format "
                         " so we will not act on the message ")
            logger.debug("This probably implies the empty message sent on long polling")

            return
        logger.info(" Message received from rejects queue : %s" % body)
        if not tast_list:
            results = TaskExecutor.execute(data=body)
        else:
            results = TaskExecutor.execute(data=body, tast_list=tast_list)
        success = True
        for i in results:
            for key, value in i.items():
               if (not value):
                   # means some task failed
                   success = False
                   break
        if success:
            logger.info(" Message processed successfully by 'rejects consumer' so deleting it from rejects queue")
            SQS.delete_msg_from_deadletter_q(receipt_handle=receipt_handle)
        else:
            logger.info(" Message from rejects queue faced failure while processing "
                         " so will post it to slack and delete it from rejects queue ")
            SQS.delete_msg_from_deadletter_q(receipt_handle=receipt_handle)
            # FIXME: what if default channel is bad
            TaskExecutor.execute(data=body, default=True)
