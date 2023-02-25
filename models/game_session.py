import os

from pynamodb.attributes import UnicodeAttribute, UnicodeSetAttribute
from pynamodb.models import Model


class GameSession(Model):
    """
    A representation of a game session and its properties- players and words.
    """
    class Meta:
        region = os.environ["AWS_DEFAULT_REGION"]
        table_name = "huji-lightricks-pitkiot"
    game_id = UnicodeAttribute(hash_key=True)
    status = UnicodeAttribute(null=True)
    players = UnicodeSetAttribute(null=True)
    words = UnicodeSetAttribute(null=True)
