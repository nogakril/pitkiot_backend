import json

import boto3
import pytest
import requests
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
        'game_id': 'test',
        'status': 'adding_players',
        'players': set(['TestAdmin'])
    }

    table.put_item(Item=game)


@pytest.fixture(scope='function')
def create_a_game_with_2_players():
    game = {
        'game_id': 'test',
        'status': 'adding_players',
        'players': {'TestAdmin', 'TestUser'}
    }

    table.put_item(Item=game)


@pytest.fixture(scope='function')
def create_a_game_with_2_players_in_adding_words_status():
    game = {
        'game_id': 'test',
        'status': 'adding_words',
        'players': {'TestAdmin', 'TestUser'}
    }

    table.put_item(Item=game)


@pytest.fixture(scope='function')
def create_a_game_with_2_players_and_5_words():
    game = {
        'game_id': 'test',
        'status': 'in_game',
        'players': {'TestAdmin', 'TestUser'},
        'words': {"one", "two", "three", "four", "five"}
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
                batch.delete_item(Key={'game_id': item['game_id']})

    request.addfinalizer(delete_inserted_items)


def change_game_status_to_game_ended():
    table.update_item(
        Key={'game_id': 'test'},
        UpdateExpression='SET #s = :val',
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={':val': 'game_ended'}
    )


# ----------------------------------------------------- Tests ------------------------------------------------------


# --------------------------------------------------- game creator -------------------------------------------------
@pytest.mark.usefixtures("clear_dynamodb_table")
def test_valid_game_creation():
    response = requests.post(GAME_CREATOR_LAMBDA,
                             headers={'Content-Type': 'application/json'},
                             data=json.dumps({'nickName': 'TestUser'}))
    assert response.status_code == 201
    response_data = response.json()
    assert len(response_data["gameId"]) == 4


@pytest.mark.usefixtures("clear_dynamodb_table")
def test_game_creation_with_wrong_method():
    response = requests.put(GAME_CREATOR_LAMBDA,
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'nickName': 'TestUser'}))
    assert response.status_code == 405


@pytest.mark.usefixtures("clear_dynamodb_table")
def test_create_game_without_admin_nickname():
    response = requests.post(GAME_CREATOR_LAMBDA,
                             headers={'Content-Type': 'application/json'},
                             data=json.dumps({}))
    assert response.status_code == 400


# --------------------------------------------------- player-adder -------------------------------------------------
@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_single_game")
def test_player_addition():
    response = requests.put(PLAYER_ADDER_LAMBDA,
                            params={'gameId': 'test'},
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'nickName': 'TestUser'}))
    assert response.status_code == 200
    item = table.get_item(Key={'game_id': 'test'})['Item']
    assert 'TestUser' in item['players']


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_single_game")
def test_player_addition_with_wrong_method():
    response = requests.post(PLAYER_ADDER_LAMBDA,
                             params={'gameId': 'test'},
                             headers={'Content-Type': 'application/json'},
                             data=json.dumps({'nickName': 'TestUser'}))
    assert response.status_code == 405


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_single_game")
def test_player_addition_without_game_id():
    response = requests.put(PLAYER_ADDER_LAMBDA,
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'nickName': 'TestUser'}))
    assert response.status_code == 400


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_single_game")
def test_player_addition_without_nickname():
    response = requests.put(PLAYER_ADDER_LAMBDA,
                            params={'gameId': 'test'},
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({}))
    assert response.status_code == 400


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_single_game")
def test_player_addition_with_invalid_game_id():
    response = requests.put(PLAYER_ADDER_LAMBDA,
                            params={'gameId': 'tst1'},
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'nickName': 'TestUser'}))
    assert response.status_code == 404


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_single_game")
def test_player_addition_with_existing_nickname():
    response = requests.put(PLAYER_ADDER_LAMBDA,
                            params={'gameId': 'test'},
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'nickName': 'TestAdmin'}))
    assert response.status_code == 409


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_single_game")
def test_player_addition_while_in_invalid_game_status():
    table.update_item(
        Key={'game_id': 'test'},
        UpdateExpression='SET #s = :val',
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={':val': 'in_game'}
    )

    response = requests.put(PLAYER_ADDER_LAMBDA,
                            params={'gameId': 'test'},
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'nickName': 'TestUser'}))
    assert response.status_code == 409


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_single_game")
def test_player_addition_while_in_game_ended_status():
    change_game_status_to_game_ended()

    response = requests.put(PLAYER_ADDER_LAMBDA,
                            params={'gameId': 'test'},
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'nickName': 'TestUser'}))
    assert response.status_code == 409


# --------------------------------------------------- status-setter -------------------------------------------------
@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_game_with_2_players")
def test_valid_status_set():
    response = requests.put(STATUS_SETTER_LAMBDA,
                            params={'gameId': 'test'},
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'status': 'adding_words'}))
    assert response.status_code == 200
    item = table.get_item(Key={'game_id': 'test'})['Item']
    assert item['status'] == "adding_words"


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_game_with_2_players")
def test_status_set_with_wrong_method():
    response = requests.post(STATUS_SETTER_LAMBDA,
                             params={'gameId': 'test'},
                             headers={'Content-Type': 'application/json'},
                             data=json.dumps({'status': 'adding_words'}))
    assert response.status_code == 405


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_game_with_2_players")
def test_status_set_without_game_id():
    response = requests.put(STATUS_SETTER_LAMBDA,
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'status': 'adding_words'}))
    assert response.status_code == 400


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_game_with_2_players")
def test_status_set_with_invalid_game_id():
    response = requests.put(STATUS_SETTER_LAMBDA,
                            params={'gameId': 'tst1'},
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'status': 'adding_words'}))
    assert response.status_code == 404


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_game_with_2_players")
def test_status_set_without_status():
    response = requests.put(STATUS_SETTER_LAMBDA,
                            params={'gameId': 'test'},
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({}))
    assert response.status_code == 400


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_single_game")
def test_status_set_with_less_than_2_players():
    response = requests.put(STATUS_SETTER_LAMBDA,
                            params={'gameId': 'test'},
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'status': 'adding_words'}))
    assert response.status_code == 400


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_game_with_2_players")
def test_status_set_to_in_game_with_less_than_5_words():
    response = requests.put(STATUS_SETTER_LAMBDA,
                            params={'gameId': 'test'},
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'status': 'in_game'}))
    assert response.status_code == 400


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_game_with_2_players")
def test_status_set_with_game_ended_status():
    change_game_status_to_game_ended()

    response = requests.put(STATUS_SETTER_LAMBDA,
                            params={'gameId': 'test'},
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'status': 'adding_words'}))
    assert response.status_code == 409


# --------------------------------------------------- status-getter -------------------------------------------------
@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_single_game")
def test_valid_get_status():
    response = requests.get(STATUS_GETTER_LAMBDA,
                            params={'gameId': 'test'})
    assert response.status_code == 200


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_single_game")
def test_get_status_with_wrong_method():
    response = requests.post(STATUS_GETTER_LAMBDA,
                             params={'gameId': 'test'})
    assert response.status_code == 405


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_single_game")
def test_get_status_without_game_id():
    response = requests.get(STATUS_GETTER_LAMBDA)
    assert response.status_code == 400


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_single_game")
def test_get_status_with_invalid_game_id():
    response = requests.get(STATUS_GETTER_LAMBDA,
                            params={'gameId': 'tst1'})
    assert response.status_code == 404


# --------------------------------------------------- players-getter -------------------------------------------------
@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_game_with_2_players")
def test_valid_get_players():
    response = requests.get(PLAYERS_GETTER_LAMBDA,
                            params={'gameId': 'test'})
    assert response.status_code == 200
    expected_players = ['TestAdmin', 'TestUser']
    assert set(expected_players) == set(response.json()['players'])


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_single_game")
def test_get_players_with_wrong_method():
    response = requests.put(PLAYERS_GETTER_LAMBDA,
                            params={'gameId': 'test'})
    assert response.status_code == 405


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_single_game")
def test_get_players_without_game_id():
    response = requests.get(PLAYERS_GETTER_LAMBDA)
    assert response.status_code == 400


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_single_game")
def test_get_players_with_invalid_game_id():
    response = requests.get(PLAYERS_GETTER_LAMBDA,
                            params={'gameId': 'tst1'})
    assert response.status_code == 404


# --------------------------------------------------- word-adder -------------------------------------------------
@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_game_with_2_players_in_adding_words_status")
def test_valid_word_addition():
    response = requests.put(WORD_ADDER_LAMBDA,
                            params={'gameId': 'test'},
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'word': 'addedWord'}))
    assert response.status_code == 200
    item = table.get_item(Key={'game_id': 'test'})['Item']
    assert "addedWord" in item['words']


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_game_with_2_players_in_adding_words_status")
def test_word_addition_with_wrong_method():
    response = requests.post(WORD_ADDER_LAMBDA,
                             params={'gameId': 'test'},
                             headers={'Content-Type': 'application/json'},
                             data=json.dumps({'word': 'addedWord'}))
    assert response.status_code == 405


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_game_with_2_players_in_adding_words_status")
def test_word_addition_without_game_id():
    response = requests.put(WORD_ADDER_LAMBDA,
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'word': 'addedWord'}))
    assert response.status_code == 400


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_game_with_2_players_in_adding_words_status")
def test_word_addition_with_invalid_game_id():
    response = requests.put(WORD_ADDER_LAMBDA,
                            params={'gameId': 'tst1'},
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'word': 'addedWord'}))
    assert response.status_code == 404


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_game_with_2_players_in_adding_words_status")
def test_word_addition_without_word():
    response = requests.put(WORD_ADDER_LAMBDA,
                            params={'gameId': 'test'},
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({}))
    assert response.status_code == 400


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_game_with_2_players_in_adding_words_status")
def test_word_addition_while_in_invalid_status():
    table.update_item(
        Key={'game_id': 'test'},
        UpdateExpression='SET #s = :val',
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={':val': 'adding_players'}
    )

    response = requests.put(WORD_ADDER_LAMBDA,
                            params={'gameId': 'test'},
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'word': 'addedWord'}))
    assert response.status_code == 409


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_game_with_2_players_in_adding_words_status")
def test_word_addition_with_game_ended_status():
    change_game_status_to_game_ended()
    response = requests.put(WORD_ADDER_LAMBDA,
                            params={'gameId': 'test'},
                            headers={'Content-Type': 'application/json'},
                            data=json.dumps({'word': 'addedWord'}))
    assert response.status_code == 409


# --------------------------------------------------- words-getter -------------------------------------------------
@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_game_with_2_players_and_5_words")
def test_valid_get_words():
    response = requests.get(WORDS_GETTER_LAMBDA,
                            params={'gameId': 'test'})
    assert response.status_code == 200
    expected_words = {"one", "two", "three", "four", "five"}
    assert expected_words == set(response.json()['words'])


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_game_with_2_players_and_5_words")
def test_get_words_with_wrong_method():
    response = requests.put(WORDS_GETTER_LAMBDA,
                            params={'gameId': 'test'})
    assert response.status_code == 405


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_game_with_2_players_and_5_words")
def test_get_words_without_game_id():
    response = requests.get(WORDS_GETTER_LAMBDA)
    assert response.status_code == 400


@pytest.mark.usefixtures("clear_dynamodb_table", "create_a_game_with_2_players_and_5_words")
def test_get_words_with_invalid_game_id():
    response = requests.get(WORDS_GETTER_LAMBDA,
                            params={'gameId': 'tst1'})
    assert response.status_code == 404
