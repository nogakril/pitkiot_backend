import json
from typing import Dict, Any

import pynamodb
from pynamodb.exceptions import PynamoDBException

from models.game_session import GameSession
from utils.lambda_exception_handler import LambdaExceptionHandler


def handler(event: Dict[str, Any], _: Any) -> Dict[str, Any]:
    """
    Lambda handler for the word_adder lambda.
    Expected input: An event containing a REST API request, with a PUT method, a gameId query parameter
     and a JSON-formatted body containing a word field.
    Expected output: An empty REST response.
     In case of an error, a status code and an informative message will be returned.
    """
    # check REST method
    method = event.get('requestContext', {}).get('http', {}).get('method', '')

    if method != "PUT":
        return LambdaExceptionHandler.handle_error(405, "Only PUT request allowed")

    # Get game ID from url, nickname from body
    game_id = event.get("queryStringParameters", {}).get("gameId")
    word = json.loads(event.get('body', {})).get('word', '')
    if not game_id:
        return LambdaExceptionHandler.handle_error(400, "Failed to process game PIN")

    if not word:
        return LambdaExceptionHandler.handle_error(400, "Body must contain word field")

    # add word to DB words list
    try:
        game = GameSession.get(hash_key=game_id)

    except GameSession.DoesNotExist:
        return LambdaExceptionHandler.handle_error(404, 'Given PIN does not belong to an existing game')

    except pynamodb.exceptions.PynamoDBConnectionError:
        return LambdaExceptionHandler.handle_error(503, 'Failed to connect. Please try again')

    except PynamoDBException as e:
        return LambdaExceptionHandler.handle_error(500, 'Internal Server Error')

    status = game.status

    if status == "game_ended":
        return LambdaExceptionHandler.handle_error(409, "Game session with this PIN has ended")

    words = game.words

    if status != "adding_words":
        return LambdaExceptionHandler.handle_error(409, "Can't currently add words to the game")

    if not words:
        words = {word}
    else:
        words.add(word)
    game.words = words

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
