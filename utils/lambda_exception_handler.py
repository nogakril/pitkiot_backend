import json


class LambdaExceptionHandler:
    """
    A handler for exceptions raised by AWS SDK and caught in lambdas.
    """
    @staticmethod
    def handle_client_error(e):
        error_code = e.response.get('Error').get('Code')
        error_message = e.response.get('Error').get('Message')
        return {
            'statusCode': error_code,
            'body': json.dumps({'error message': error_message})
        }

    @staticmethod
    def handle_general_error(e):
        return {
            'statusCode': 500,
            'body': json.dumps({'error': "Internal server error occurred communicating with DynamoDB"})
        }
