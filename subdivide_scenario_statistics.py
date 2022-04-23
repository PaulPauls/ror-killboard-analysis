import os
import json
from tqdm import tqdm
from statistics import mean

SCENARIO_STATISTICS_JSON_FILE = './ror-killboard_scenario_statistics.json'
SUBDIVIDED_JSON_OUTPUT_DIR = './subdivided_scenario_statistics/'


def main():
    """"""
    subdivided_json_outdir = os.path.abspath(SUBDIVIDED_JSON_OUTPUT_DIR)
    os.makedirs(subdivided_json_outdir, exist_ok=True)

    t1_standard_json_path = subdivided_json_outdir + '/scenario_statistics_t1_standard.json'
    t1_pug_json_path = subdivided_json_outdir + '/scenario_statistics_t1_pug.json'
    mid_tier_standard_json_path = subdivided_json_outdir + '/scenario_statistics_mid-tier_standard.json'
    mid_tier_pug_json_path = subdivided_json_outdir + '/scenario_statistics_mid-tier_pug.json'
    t4_standard_json_path = subdivided_json_outdir + '/scenario_statistics_t4_standard.json'
    t4_pug_json_path = subdivided_json_outdir + '/scenario_statistics_t4_pug.json'
    t4_city_json_path = subdivided_json_outdir + '/scenario_statistics_t4_city.json'
    t4_group_ranked_json_path = subdivided_json_outdir + '/scenario_statistics_t4_group-ranked.json'

    with open(SCENARIO_STATISTICS_JSON_FILE, 'r') as json_file:
        scenario_statistics = json.load(json_file)

    scenario_statistics_t1 = {'standard': dict(), 'pug': dict()}
    scenario_statistics_mid_tier = {'standard': dict(), 'pug': dict()}
    scenario_statistics_t4 = {'standard': dict(), 'pug': dict(), 'city': dict(), 'group_ranked': dict()}

    for scenario_id, scenario_info in tqdm(scenario_statistics.items()):
        scenario_type = scenario_info['queueType'].lower()
        if scenario_type == 'duo':
            scenario_type = 'pug'

        if scenario_type in ['city', 'group_ranked']:
            scenario_statistics_t4[scenario_type][scenario_id] = scenario_info
            continue

        character_levels = [character_info['level'] for character_info in scenario_info['scoreboardEntries']]
        mean_character_level = round(mean(character_levels))

        if mean_character_level < 16:
            scenario_statistics_t1[scenario_type][scenario_id] = scenario_info
        elif mean_character_level < 40:
            scenario_statistics_mid_tier[scenario_type][scenario_id] = scenario_info
        else:
            scenario_statistics_t4[scenario_type][scenario_id] = scenario_info

    with open(t1_standard_json_path, 'w') as out_file:
        json.dump(scenario_statistics_t1['standard'], out_file)
    with open(t1_pug_json_path, 'w') as out_file:
        json.dump(scenario_statistics_t1['pug'], out_file)
    with open(mid_tier_standard_json_path, 'w') as out_file:
        json.dump(scenario_statistics_mid_tier['standard'], out_file)
    with open(mid_tier_pug_json_path, 'w') as out_file:
        json.dump(scenario_statistics_mid_tier['pug'], out_file)
    with open(t4_standard_json_path, 'w') as out_file:
        json.dump(scenario_statistics_t4['standard'], out_file)
    with open(t4_pug_json_path, 'w') as out_file:
        json.dump(scenario_statistics_t4['pug'], out_file)
    with open(t4_city_json_path, 'w') as out_file:
        json.dump(scenario_statistics_t4['city'], out_file)
    with open(t4_group_ranked_json_path, 'w') as out_file:
        json.dump(scenario_statistics_t4['group_ranked'], out_file)

    print('fin')


if __name__ == '__main__':
    main()
