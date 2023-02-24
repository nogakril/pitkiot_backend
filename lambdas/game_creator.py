import json
from typing import Dict, Any
import botocore.exceptions as boto_exceptions
from uuid import uuid4

from models.game_session import GameSession
from utils.lambda_exception_handler import LambdaExceptionHandler


def handler(event: Dict[str, Any], _: Any) -> Dict[str, Any]:
    """
    Lambda handler for the game_creator lambda.
    Expected input: An event containing a REST API request, with a POST method and no body.
    Expected output: A JSON-formatted response containing a game ID.
     In case of an error, a status code and an informative message will be returned.
    """

    # check REST method
    method = event.get('requestContext', {}).get('http', {}).get('method', '')
    if method != "POST":
        return {
            'statusCode': 405,
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
        return LambdaExceptionHandler.handle_client_error(e)
    except Exception as e:
        return LambdaExceptionHandler.handle_general_error(e)
