import json
from typing import Dict, Any
import botocore.exceptions as boto_exceptions

from models.game_session import GameSession
from utils.lambda_exception_handler import LambdaExceptionHandler


def handler(event: Dict[str, Any], _: Any) -> Dict[str, Any]:
    """
        Lambda handler for the status_getter lambda.
        Expected input: An event containing a REST API request, with a GET method and a gameId query parameter.
        Expected output: A JSON-formatted response containing a status.
         In case of an error, a status code and an informative message will be returned.
        """
    # check REST method
    method = event.get('requestContext', {}).get('http', {}).get('method', '')
    if method != "GET":
        return {
            'statusCode': 405,
            'body': json.dumps({'error': 'only GET request allowed'})
        }

    # Get game ID from url
    game_id = event.get("queryStringParameters", {}).get("gameId")
    if not game_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'url must contain gameId parameter.'})
        }

    # get current status from DB
    try:
        game = GameSession.get(hash_key=game_id)
        status = game.status

        return {
            'statusCode': 200,
            'body': json.dumps({'status': status})
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