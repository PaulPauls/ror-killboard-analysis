import json
import requests
from tqdm import tqdm

API_URL = 'https://production-api.waremu.com/graphql'
SCENARIO_LISTINGS_JSON_FILE = './ror-killboard_scenario_listings.json'
JSON_OUTPUT_FILE = './ror-killboard_scenario_statistics.json'


def main():
    """"""
    with open(SCENARIO_LISTINGS_JSON_FILE, 'r') as json_file:
        scenario_listings = json.load(json_file)

    json_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip',
        'Referer': 'https://killboard.returnofreckoning.com/',
        'Content-Type': 'application/json',
        'Origin': 'https://killboard.returnofreckoning.com',
        'Content-Length': '1024',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'TE': 'trailers'
    }

    json_request = {
        'operationName': 'GetScenarioInfo',
        'variables': {
            'id': None
        },
        'query': 'query GetScenarioInfo($id: ID) {\n  scenario(id: $id) {\n    instanceId\n    scenarioId\n    startTime\n    endTime\n    winner\n    points\n    queueType\n    scoreboardEntries {\n      character {\n        id\n        name\n        career\n        __typename\n      }\n      guild {\n        id\n        name\n        heraldry {\n          emblem\n          pattern\n          color1\n          color2\n          shape\n          __typename\n        }\n        __typename\n      }\n      team\n      level\n      renownRank\n      quitter\n      protection\n      kills\n      deathBlows\n      deaths\n      damage\n      healing\n      objectiveScore\n      killsSolo\n      killDamage\n      healingSelf\n      healingOthers\n      protectionSelf\n      protectionOthers\n      damageReceived\n      resurrectionsDone\n      healingReceived\n      protectionReceived\n      __typename\n    }\n    __typename\n  }\n}'
    }

    scenario_statistics = dict()

    for scenario_id in tqdm(scenario_listings.keys()):
        json_request['variables']['id'] = scenario_id

        try:
            response = requests.post(API_URL, json=json_request, headers=json_headers)
            response_json = response.json()
        except Exception as e:
            print(f"Error occured with scenario id {scenario_id}: {e}.")
            continue

        scenario_statistics[scenario_id] = response_json['data']['scenario']

    with open(JSON_OUTPUT_FILE, 'w') as out_file:
        json.dump(scenario_statistics, out_file)

    print(f'Scenario statistics scraped: {len(scenario_statistics)}')
    print('fin')


if __name__ == '__main__':
    main()
