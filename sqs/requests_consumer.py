from common.msgqueue.consumer import Consumer
from logger.logger_util import *
from sqs.sqs_util import SQS

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
                WaitTimeSeconds=20
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
        except KeyError as e:

            logger.debug(" Message received from requests queue was not of required format "
                         " so we will not act on the message ")
            logger.debug("This probably implies the empty message sent on long polling")

            return
        logger.info(" Message received from requests queue : %s" % body)
        if(body.startswith('s')):
            success = True
        else:
            success = False
        if success:
            logger.info(" Message processed successfully by 'requests consumer' so deleting it from requests queue")
            SQS.delete_msg_from_main_q(receipt_handle=receipt_handle)
        else:
            logger.info(" Message from requests queue faced failure while processing "
                        " so we will not delete from requests queue ")
            pass