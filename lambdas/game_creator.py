import json

from typing import Dict, Any
from uuid import uuid4
from hashlib import sha256

from models.game_session import GameSession
from utils.lambda_exception_handler import LambdaExceptionHandler
import pynamodb.exceptions
from pynamodb.exceptions import PynamoDBException


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
        return LambdaExceptionHandler.handle_error(405, "Only POST request allowed")

    # Get nickname from body
    nickname = json.loads(event.get('body', {})).get('nickName', '')
    if not nickname:
        return LambdaExceptionHandler.handle_error(400, "Nickname must be provided to create a game")

    # create game ID
    game_id = sha256(str(uuid4()).encode('utf-8')).hexdigest()[:4]

    # create game object
    game = GameSession()
    game.game_id = game_id
    game.status = "adding_players"
    game.players = [nickname]

    try:
        game.save()

    except GameSession.DoesNotExist:
        return LambdaExceptionHandler.handle_error(404, 'Given PIN does not belong to an existing game')

    except pynamodb.exceptions.PynamoDBConnectionError:
        return LambdaExceptionHandler.handle_error(503, 'Failed to connect. Please try again')

    except PynamoDBException as e:
        return LambdaExceptionHandler.handle_error(500, 'Internal Server Error')

    print(f"game added: id- {game_id}, admin nickName- {nickname}")

    return {
        'statusCode': 201,
        'body': json.dumps({'gameId': game_id})
    }
