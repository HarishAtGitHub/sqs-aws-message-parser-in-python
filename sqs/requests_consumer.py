from common.msgqueue.consumer import Consumer
from logger.logger_util import *
from sqs.sqs_util import SQS
from common.task.task_executor import TaskExecutor

class RequestsConsumer(Consumer):

    def __init__(self, id):
        logger = getLogger()
        self.connection = SQS.get_connection()
        self.id = id
        print('Successfully initialized Requests Consumer : ' + str(self.id))
        logger.info('Successfully initialized Requests Consumer : ' + str(self.id))

    def start(self):
        logger = getLogger()
        while True:
            logger.debug('Requests Consumer : ' + str(self.id) +
                        ' is subscribing to queue : ' + MAIN_QUEUE)
            message  = self.connection.receive_message(
                QueueUrl=SQS.get_main_q_url(),
                MaxNumberOfMessages=1,
                VisibilityTimeout=30,
                WaitTimeSeconds=20,
                MessageAttributeNames=[
                    'past_results',
                ]
            )
            self.callback(message)
            #print(message)

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
        logger.info(" Message received from requests queue : %s" % body)
        if not tast_list:
            results = TaskExecutor.execute()
        else:
            results = TaskExecutor.execute(tast_list)
        success = True
        for i in results:
            for key, value in i.items():
               if (not value):
                   # means some task failed
                   success = False
                   break
        if success:
            logger.info(" Message processed successfully by 'requests consumer' so deleting it from requests queue")
            SQS.delete_msg_from_main_q(receipt_handle=receipt_handle)
        else:
            logger.info(" Message from requests queue faced failure while processing "
                        " so we will delete from requests queue and repost it to rejects queue")
            '''
            logger.info(" Message from requests queue faced failure while processing "
                        " so we will not delete from requests queue ")
            # delete and repost as SQS does not have the feature to update attributes
            '''
            SQS.delete_msg_and_repost_to_deadletter_q(receipt_handle=receipt_handle,
                                                      message_body=body,
                                                      past_results=results)

