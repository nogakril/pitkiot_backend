import json
from functools import wraps

import pynamodb.exceptions
from pynamodb.exceptions import PynamoDBException

from models.game_session import GameSession


class LambdaExceptionHandler:
    """
    A handler for exceptions raised in the lambdas.
    """
    @staticmethod
    def handle_error(error_code, error_message):
        """
        A static handler for exceptions raised in the lambdas.
        :param error_code: The REST error code
        :param error_message: An informative error message
        :return: A JSON-formatted response
        """
        return {
            'statusCode': error_code,
            'body': json.dumps({'error': error_message})
        }

    """
    A handler for exceptions raised in the lambdas.
    """
    # @staticmethod
    # def handle_dynamoDB_error(e):
    #     """
    #     A handler for exceptions raised by pynamoDB.
    #     :param error_code: The REST error code
    #     :param error_message: An informative error message
    #     :return: A JSON-formatted response
    #     """
    #     if type(e) == GameSession.DoesNotExist:
    #         return {
    #             'statusCode': 404,
    #             'body': json.dumps({'error': 'Given PIN does not belong to an existing game'})
    #         }
    #
    #     except pynamodb.exceptions.PynamoDBConnectionError:
    #         return {
    #             'statusCode': 503,
    #             'body': json.dumps({'error': 'Failed to connect. Please try again'})
    #         }
    #
    #     except PynamoDBException as e:
    #         return {
    #             'statusCode': 500,
    #             'body': json.dumps({'error': 'Internal Server Error'})
    #         }

    # @staticmethod
    # def pynamodb_exception_handler(func):
    #     """
    #     A handler for pynamoDB exceptions, to be used as a decorator.
    #     :param func: The DB operation to be performed.
    #     :return: A JSON-formatted response
    #     """
    #     @wraps(func)
    #     def wrapper(*args, **kwargs):
    #         try:
    #             return func(*args, **kwargs)
    #
    #         except GameSession.DoesNotExist:
    #             return {
    #                 'statusCode': 404,
    #                 'body': json.dumps({'error': 'Given PIN does not belong to an existing game'})
    #             }
    #
    #         except pynamodb.exceptions.PynamoDBConnectionError:
    #             return {
    #                 'statusCode': 503,
    #                 'body': json.dumps({'error': 'Failed to connect. Please try again'})
    #             }
    #
    #         except PynamoDBException as e:
    #             return {
    #                 'statusCode': 500,
    #                 'body': json.dumps({'error': 'Internal Server Error'})
    #             }
    #
    #     return wrapper
