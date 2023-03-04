import json
from typing import Dict, Any

import pynamodb
from pynamodb.exceptions import PynamoDBException

from models.game_session import GameSession
from utils.lambda_exception_handler import LambdaExceptionHandler


def handler(event: Dict[str, Any], _: Any) -> Dict[str, Any]:
    """
        Lambda handler for the players_getter lambda.
        Expected input: An event containing a REST API request, with a GET method and a gameId query parameter.
        Expected output: A JSON-formatted response containing a players list.
         In case of an error, a status code and an informative message will be returned.
    """
    # check REST method
    method = event.get('requestContext', {}).get('http', {}).get('method', '')

    if method != "GET":
        return LambdaExceptionHandler.handle_error(405, "Only GET request allowed")

    # Get game ID from url
    game_id = event.get("queryStringParameters", {}).get("gameId")
    if not game_id:
        return LambdaExceptionHandler.handle_error(400, "Failed to process game PIN")

    # get current players list from DB
    try:
        game = GameSession.get(hash_key=game_id)

    except GameSession.DoesNotExist:
        return LambdaExceptionHandler.handle_error(404, 'Given PIN does not belong to an existing game')

    except pynamodb.exceptions.PynamoDBConnectionError:
        return LambdaExceptionHandler.handle_error(503, 'Failed to connect. Please try again')

    except PynamoDBException as e:
        return LambdaExceptionHandler.handle_error(500, 'Internal Server Error')

    players = list(game.players)

    return {
        'statusCode': 200,
        'body': json.dumps({'players': players})
    }


