import json
from typing import Dict, Any
import botocore.exceptions as boto_exceptions
from uuid import uuid4
from hashlib import sha256

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

    # Get nickname from body
    nickname = json.loads(event.get('body', {})).get('nickName', '')
    if not nickname:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'body must contain nickName field.'})
        }

    # create game ID
    game_id = sha256(str(uuid4()).encode('utf-8')).hexdigest()[:4]
    try:
        # create new game in DB
        game = GameSession()
        game.game_id = game_id
        game.status = "adding_players"
        game.players = [nickname]
        game.save()
        print(f"game added: id- {game_id}, admin nickName- {nickname}")

        return {
            'statusCode': 201,
            'body': json.dumps({'gameId': game_id})
        }

    except boto_exceptions.ClientError as e:
        return LambdaExceptionHandler.handle_client_error(e)
    except Exception as e:
        return LambdaExceptionHandler.handle_general_error(e)
