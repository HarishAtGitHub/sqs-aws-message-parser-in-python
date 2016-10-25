#!/usr/bin/env python
import boto3
from logger.logger_util import *

class SQS:

    logger = getLogger()
    connection = None

    @classmethod
    def get_connection(cls):
        if cls.connection is None:
            cls.connection = boto3.client('sqs')
            cls.logger.debug('Successfully created AWS SQS connection')
        cls.logger.debug('Successfully provided AWS SQS connection')
        return cls.connection

    @classmethod
    def bootstrap(cls):
        # TODO: Do exhaustive exception handling
        cls.configure_deadletter_q()
        cls.configure_main_q()
        cls.logger.info('Successfully completed initial setup of AWS- SQS')

    @classmethod
    def configure_main_q(cls):
        connection = cls.get_connection()
        queue_url = (connection.create_queue(QueueName=MAIN_QUEUE))['QueueUrl']
        redrive_policy = {
            'deadLetterTargetArn': cls.get_deadletter_q_arn(),
            'maxReceiveCount': 1
        }
        import json
        connection.set_queue_attributes(
              QueueUrl=queue_url,
              Attributes={
                  'RedrivePolicy': json.dumps(redrive_policy),

              }
        )

        cls.logger.debug('Successfully created AWS SQS MAIN QUEUE : ' + MAIN_QUEUE)
        cls.logger.debug('Successfully configured AWS SQS MAIN QUEUE : %s with '
        'DEAD LETTER QUEUE : %s' % (MAIN_QUEUE, DEAD_LETTER_QUEUE,))

    @classmethod
    def configure_deadletter_q(cls):
        connection = cls.get_connection()
        connection.create_queue(QueueName=DEAD_LETTER_QUEUE)['QueueUrl']
        cls.logger.debug('Successfully created AWS SQS DEAD LETTER QUEUE : ' + DEAD_LETTER_QUEUE)

    @classmethod
    def get_deadletter_q_arn(cls):
        connection = cls.get_connection()
        queue_url = (connection.create_queue(QueueName=DEAD_LETTER_QUEUE))['QueueUrl'] # using create
        # we don't have any easy way to get queue url from name from client object
        # cls.logger.info(queue_url)
        queuearn = connection.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=['QueueArn'
                            ])
        return queuearn['Attributes']['QueueArn']

    @classmethod
    def get_deadletter_q_url(cls):
        connection = cls.get_connection()
        queue_url = (connection.create_queue(QueueName=DEAD_LETTER_QUEUE))['QueueUrl']  # using create
        return queue_url

    @classmethod
    def get_main_q_url(cls):
        connection = cls.get_connection()
        queue_url = (connection.create_queue(QueueName=MAIN_QUEUE))['QueueUrl']  # using create
        return queue_url

    @classmethod
    def delete_msg_from_main_q(cls, receipt_handle):
        connection = cls.get_connection()
        connection.delete_message(
            QueueUrl=cls.get_main_q_url(),
            ReceiptHandle=receipt_handle
        )

    @classmethod
    def delete_msg_from_deadletter_q(cls, receipt_handle):
        connection = cls.get_connection()
        connection.delete_message(
            QueueUrl=cls.get_deadletter_q_url(),
            ReceiptHandle=receipt_handle
        )

    @classmethod
    def send_msg_to_deadletter_q(cls, message_body, past_results):
        connection = cls.get_connection()
        connection.send_message(
            QueueUrl=cls.get_deadletter_q_url(),
            MessageBody=message_body,
            DelaySeconds=0,
            MessageAttributes={
                'past_results' : {
                    'DataType': 'String',
                    'StringValue' : str(past_results),

                }

            }
        )

    @classmethod
    def delete_msg_and_repost_to_deadletter_q(cls, receipt_handle, message_body, past_results):
        # this defeats the purpose of deadletter queue
        # but we defeated it for the purpose of selectively running failed tasks
        cls.delete_msg_from_main_q(receipt_handle)
        cls.send_msg_to_deadletter_q(message_body, past_results)



