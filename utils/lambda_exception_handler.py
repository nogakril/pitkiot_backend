import json


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
