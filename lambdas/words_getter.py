import json
from typing import Dict, Any
import boto3
import pynamodb
from botocore.exceptions import EndpointConnectionError, ConnectTimeoutError, ClientError

from models.game_session import GameSession


def handler(event: Dict[str, Any], _: Any) -> Dict[str, Any]:
    """
    """
    pass
