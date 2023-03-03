import json
from typing import Dict, Any
import botocore.exceptions as boto_exceptions

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
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'only PUT request allowed'})
        }

    # Get game ID from url, status from body
    game_id = event.get("queryStringParameters", {}).get("gameId")
    status = json.loads(event.get('body', {})).get('status', '')
    if not game_id or not status:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'url must contain gameId parameter.'
                                         'body must contain status field.'})
        }

    if status not in ['adding_players', 'adding_words', 'in_game', 'game_ended']:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'game status must be one of:'
                                         'adding_players, adding_words, in_game, game_ended'})
        }

    # get game session from DB and set the status
    try:
        game = GameSession.get(hash_key=game_id)
        if game.status == "game_ended":
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'game session with this PIN has ended'})
            }

        # prevent game with less than 2 players (which is not enough for 2 teams)
        if len(game.players) < 2:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'game must have a least 2 players'})
            }

        # prevent starting game with less than 5 words
        if status == "in_game":  # only relevant when starting game
            if (not game.words) or (len(game.words) < 5):
                return {
                    'statusCode': 400,
                    'body': json.dumps({'error': 'game must have a least 5 words'})
                }

        game.status = status
        game.save()

        return {
                'statusCode': 200
            }

    except GameSession.DoesNotExist:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'given PIN does not belong to an existing game'})
        }
    except boto_exceptions.ClientError as e:
        return LambdaExceptionHandler.handle_client_error(e)
    except boto_exceptions.EndpointConnectionError as e:
        return LambdaExceptionHandler.handle_general_error(e)
