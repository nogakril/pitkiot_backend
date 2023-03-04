import json
from typing import Dict, Any
import botocore.exceptions as boto_exceptions
import pynamodb
from pynamodb.exceptions import PynamoDBException

from models.game_session import GameSession
from utils.lambda_exception_handler import LambdaExceptionHandler


def handler(event: Dict[str, Any], _: Any) -> Dict[str, Any]:
    """
    Lambda handler for the status_setter lambda.
    Expected input: An event containing a REST API request, with a PUT method, a gameId query parameter
     and a JSON-formatted body containing a status field.
     status field must be one of: adding_players, adding_words, in_game, game_ended.
    Expected output: An empty REST response.
     In case of an error, a status code and an informative message will be returned.
    """
    # check REST method
    method = event.get('requestContext', {}).get('http', {}).get('method', '')
    if method != "PUT":
        return LambdaExceptionHandler.handle_error(405, "Only PUT request allowed")

    # Get game ID from url, status from body
    game_id = event.get("queryStringParameters", {}).get("gameId")
    status = json.loads(event.get('body', {})).get('status', '')

    if not game_id:
        return LambdaExceptionHandler.handle_error(400, "Failed to process game PIN")

    if not status:
        return LambdaExceptionHandler.handle_error(400, "Body must contain status field")

    # get game session from DB and set the status
    try:
        game = GameSession.get(hash_key=game_id)

    except GameSession.DoesNotExist:
        return LambdaExceptionHandler.handle_error(404, 'Given PIN does not belong to an existing game')

    except pynamodb.exceptions.PynamoDBConnectionError:
        return LambdaExceptionHandler.handle_error(503, 'Failed to connect. Please try again')

    except PynamoDBException as e:
        return LambdaExceptionHandler.handle_error(500, 'Internal Server Error')

    if game.status == "game_ended":
        return LambdaExceptionHandler.handle_error(409, 'The game with this PIN has ended')

    # prevent game with less than 2 players (which is not enough for 2 teams)
    if len(game.players) < 2:
        return LambdaExceptionHandler.handle_error(400, 'Game must have a least 2 players')

    # prevent starting game with less than 5 words
    if status == "in_game":  # only relevant when starting game
        if (not game.words) or (len(game.words) < 5):
            return LambdaExceptionHandler.handle_error(400, 'Game must have a least 5 words')

    game.status = status

    try:
        game.save()

    except GameSession.DoesNotExist:
        return LambdaExceptionHandler.handle_error(404, 'Given PIN does not belong to an existing game')

    except pynamodb.exceptions.PynamoDBConnectionError:
        return LambdaExceptionHandler.handle_error(503, 'Failed to connect. Please try again')

    except PynamoDBException as e:
        return LambdaExceptionHandler.handle_error(500, 'Internal Server Error')

    return {
            'statusCode': 200
        }


