import math
import json
import requests
from tqdm import tqdm

API_URL = 'https://production-api.waremu.com/graphql'
JSON_OUTPUT_FILE = './ror-killboard_scenario_listings.json'


def main():
    """"""
    json_headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:99.0) Gecko/20100101 Firefox/99.0',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip',
        'Referer': 'https://killboard.returnofreckoning.com/',
        'Content-Type': 'application/json',
        'Origin': 'https://killboard.returnofreckoning.com',
        'Content-Length': '702',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'cross-site',
        'TE': 'trailers'
    }

    json_request = {
        'operationName': 'GetScenarioList',
        'variables': {
            'first': 50,
            # 'after': '12345'
        },
        'query': 'query GetScenarioList($characterId: ID, $guildId: ID, $queueType: ScenarioQueueType, $first: Int, $last: Int, $before: String, $after: String) {\n  scenarios(\n    characterId: $characterId\n    guildId: $guildId\n    queueType: $queueType\n    first: $first\n    last: $last\n    before: $before\n    after: $after\n  ) {\n    totalCount\n    nodes {\n      instanceId\n      scenarioId\n      startTime\n      endTime\n      winner\n      points\n      __typename\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n      hasPreviousPage\n      startCursor\n      __typename\n    }\n    __typename\n  }\n}'
    }

    response = requests.post(API_URL, json=json_request, headers=json_headers)
    response_json = response.json()

    scenario_listings = dict()
    for scenario_instance in response_json['data']['scenarios']['nodes']:
        scenario_listings[scenario_instance['instanceId']] = scenario_instance

    total_scenarios_count = response_json['data']['scenarios']['totalCount']
    total_requests_count = math.ceil(total_scenarios_count / 50)

    for request_counter in tqdm(range(1, total_requests_count)):
        scenario_after_idx = total_scenarios_count - request_counter * 50
        json_request['variables']['after'] = str(scenario_after_idx)

        response = requests.post(API_URL, json=json_request, headers=json_headers)
        response_json = response.json()

        for scenario_instance in response_json['data']['scenarios']['nodes']:
            scenario_listings[scenario_instance['instanceId']] = scenario_instance

    with open(JSON_OUTPUT_FILE, 'w') as out_file:
        json.dump(scenario_listings, out_file)

    print(f'Scenario listings scraped: {len(scenario_listings)}')
    print('fin')


if __name__ == '__main__':
    main()
