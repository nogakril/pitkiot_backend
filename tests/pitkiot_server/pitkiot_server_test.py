import json
import os
import pytest
import requests
import boto3
from botocore.config import Config

# ------------------------------------------------- Test arguments -------------------------------------------------
REGION = "us-west-2"
TABLE_NAME = "huji-lightricks-pitkiot"
GAME_CREATOR_LAMBDA = "https://2fd7cttxuprcyyav2ybdhzk4hi0ywbtr.lambda-url.us-west-2.on.aws/"
PLAYER_ADDER_LAMBDA = "https://sjaxvgnhxa5vmiiew7cnr5anmi0aftdh.lambda-url.us-west-2.on.aws/players/"
STATUS_SETTER_LAMBDA = "https://ebs2llc3ixerfgkboyd6gfmxsa0qxwom.lambda-url.us-west-2.on.aws/status/"
STATUS_GETTER_LAMBDA = "https://q4i3ok63vpncmuvgd3xmaw4of40ijbds.lambda-url.us-west-2.on.aws/status/"
PLAYERS_GETTER_LAMBDA = " https://y2ptad7vg7pl2raly7ebo7asti0hjojt.lambda-url.us-west-2.on.aws/players/"
WORD_ADDER_LAMBDA = "https://o2e6gr76txdn4f5w3dtodgvmb40ckyqb.lambda-url.us-west-2.on.aws/words/"
WORDS_GETTER_LAMBDA = " https://bn7hrwlgyyveylitohyguntmnu0rcfya.lambda-url.us-west-2.on.aws/words/"

# GAME_CREATOR_LAMBDA = "huji-lightricks-pitkiot-game-creator-lambda"
# PLAYER_ADDER_LAMBDA = "huji-lightricks-pitkiot-player-adder-lambda"
# STATUS_SETTER_LAMBDA = "huji-lightricks-pitkiot-status-setter-lambda"
# STATUS_GETTER_LAMBDA = "huji-lightricks-pitkiot-status-getter-lambda"
# PLAYERS_GETTER_LAMBDA = "huji-lightricks-pitkiot-players-getter-lambda"
# WORD_ADDER_LAMBDA = "huji-lightricks-pitkiot-word-adder-lambda"
# WORDS_GETTER_LAMBDA = "huji-lightricks-pitkiot-words-getter-lambda"

# ---------------------------------------------------- Fixture -----------------------------------------------------
# Set up the boto3 client for handling the DB
dynamodb = boto3.resource('dynamodb', region_name=REGION)
table = dynamodb.Table(TABLE_NAME)

# Set up the boto3 client for invoking the lambda function
config = Config(retries={'max_attempts': 0})
lambda_client = boto3.client('lambda', region_name=REGION, config=config)


@pytest.fixture(scope='function')
def create_a_single_game():
    game = {
        'gameId': 'test',
        'status': 'adding_players',
        'players': ['TestAdmin']
    }

    table.put_item(Item=game)


@pytest.fixture(scope='function')
def clear_dynamodb_table(request):
    # Before the test, save all the existing items in the table
    existing_items = table.scan()['Items']

    def delete_inserted_items():
        # After the test, delete all the items that were inserted during the test
        inserted_items = table.scan()['Items']
        items_to_delete = [item for item in inserted_items if item not in existing_items]
        with table.batch_writer() as batch:
            for item in items_to_delete:
                batch.delete_item(Key={'gameId': item['gameId']})

    request.addfinalizer(delete_inserted_items)

# ----------------------------------------------------- Tests ------------------------------------------------------


# game creator
@pytest.mark.usefixtures("clear_dynamodb_table")
def test_valid_game_creation():
    response = requests.post(GAME_CREATOR_LAMBDA,
                             headers={'Content-Type': 'application/json'},
                             data=json.dumps({'nickName': 'TestUser'}))
    assert response.status_code == 201
    response_data = response.json()
    assert len(response_data["gameId"]) == 4


@pytest.mark.usefixtures("clear_dynamodb_table")
def test_create_game_without_admin_nickname():
    response = requests.post(GAME_CREATOR_LAMBDA,
                             headers={'Content-Type': 'application/json'},
                             data=json.dumps({}))
    assert response.status_code == 400


# player-adder
@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_single_game")
def test_player_addition():
    assert 1 == 1


@pytest.mark.usefixtures("clear_table")
def test_player_addition_without_game_id():
    pass


@pytest.mark.usefixtures("clear_table")
def test_player_addition_without_nickname():
    pass


@pytest.mark.usefixtures("clear_table")
def test_player_addition_with_invalid_game_id():
    pass


@pytest.mark.usefixtures("clear_table")
def test_player_addition_with_existing_nickname():
    pass


@pytest.mark.usefixtures("clear_table")
def test_player_addition_while_in_invalid_game_status():
    pass


# status-setter
@pytest.mark.usefixtures("clear_table")
def test_valid_status_set():
    pass


@pytest.mark.usefixtures("clear_table")
def test_status_set_without_game_id():
    pass


@pytest.mark.usefixtures("clear_table")
def test_status_set_with_invalid_game_id():
    pass


@pytest.mark.usefixtures("clear_table")
def test_status_set_without_status():
    pass


@pytest.mark.usefixtures("clear_table")
def test_status_set_with_invalid_status():
    # not adding_players/in_game etc
    pass


# status-getter
@pytest.mark.usefixtures("clear_table")
def test_valid_get_status():
    pass


@pytest.mark.usefixtures("clear_table")
def test_get_status_without_game_id():
    pass


@pytest.mark.usefixtures("clear_table")
def test_get_status_with_invalid_game_id():
    pass


# players-getter
@pytest.mark.usefixtures("clear_table")
def test_valid_get_players():
    pass


@pytest.mark.usefixtures("clear_table")
def test_get_players_without_game_id():
    pass


@pytest.mark.usefixtures("clear_table")
def test_get_players_with_invalid_game_id():
    pass


# word-adder
@pytest.mark.usefixtures("clear_table")
def test_valid_word_addition():
    pass


@pytest.mark.usefixtures("clear_table")
def test_word_addition_without_game_id():
    pass


@pytest.mark.usefixtures("clear_table")
def test_word_addition_with_invalid_game_id():
    pass


@pytest.mark.usefixtures("clear_table")
def test_word_addition_without_word():
    pass


@pytest.mark.usefixtures("clear_table")
def test_word_addition_while_in_invalid_status():
    pass


# words-getter
@pytest.mark.usefixtures("clear_table")
def test_valid_get_words():
    pass


@pytest.mark.usefixtures("clear_table")
def test_get_words_without_game_id():
    pass


@pytest.mark.usefixtures("clear_table")
def test_get_words_with_invalid_game_id():
    pass


# game scenarios
@pytest.mark.usefixtures("clear_table")
def test_valid_simple_game_session():
    pass


@pytest.mark.usefixtures("clear_table")
def test_valid_two_concurrent_game_sessions():
    pass


@pytest.mark.usefixtures("clear_table")
def test_multiple_invalid_requests_during_game_session():
    pass
