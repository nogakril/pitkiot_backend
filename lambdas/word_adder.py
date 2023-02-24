import json
from typing import Dict, Any
import botocore.exceptions as boto_exceptions

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
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'only PUT request allowed'})
        }

    # Get game ID from url, nickname from body
    game_id = event.get("queryStringParameters", {}).get("gameId")
    word = json.loads(event.get('body', {})).get('word', '')
    if not game_id or not word:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'url must contain gameId parameter.'
                                         'body must contain word field.'})
        }

    # add word to DB words list
    try:
        game = GameSession.get(hash_key=game_id)
        game.words = game.words.append(word)
        game.save()

        return {
            'statusCode': 200
        }

    except GameSession.DoesNotExist:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Given ID does not belong to an existing game'})
        }
    except boto_exceptions.ClientError as e:
        return LambdaExceptionHandler.handle_client_error(e)
    except boto_exceptions.EndpointConnectionError as e:
        return LambdaExceptionHandler.handle_general_error(e)
      