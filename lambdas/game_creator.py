import json
from typing import Dict, Any
import botocore.exceptions as boto_exceptions
import boto3
from uuid import uuid4
import pynamodb
from botocore.exceptions import EndpointConnectionError, ConnectTimeoutError, ClientError

from models.game_session import GameSession


def handler(event: Dict[str, Any], _: Any) -> Dict[str, Any]:
    """
    Lambda handler for the game_creator lambda.
    Expected input: An event containing a REST API request, with a POST method and no body.
    Expected output: A JSON-formatted response containing a game ID.
     In case of an error, a status code, a status string and an informative message will be returned.
    """

    # check REST method
    method = event.get('requestContext', {}).get('http', {}).get('method', '')
    if method != "POST":
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'only POST request allowed'})
        }

    # create game ID
    game_id = str(uuid4())

    try:
        # create new game in DB
        game = GameSession()
        game.game_id = game_id
        game.status = "adding_players"
        game.save()

        return {
            'statusCode': 201,
            'body': json.dumps({'game_id': game_id})
        }

    except boto_exceptions.ClientError as e:
        error_code = e.response.get('Error').get('Code')
        error_message = e.response.get('Error').get('Message')
        return {
            'statusCode': error_code,
            'body': json.dumps({'error message': error_message})
        }
    except boto_exceptions.EndpointConnectionError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': "Internal error occurred communicating with DynamoDB"})
        }
