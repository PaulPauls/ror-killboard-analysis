import os
import json
import matplotlib.pyplot as plt
from tqdm import tqdm
from statistics import mean
from collections import defaultdict
from matplotlib.font_manager import FontProperties

SCENARIO_STATISTICS_JSON = './subdivided_scenario_statistics/scenario_statistics_t4_standard.json'
TABLE_TITLE = "mean_{}_career-relative_in_t4_standard_scenarios_-_{}"
TABLE_OUTDIR = './tank_comparison_tables_t4_standard/'
DISREGARD_LATE_THRESHOLD = 0.1
DISREGARD_WORST_PERFORMANCES = False
RR_NORMALIZATION = False


def div_zero(a, b):
    """"""
    return a / b if b else 0


def mean_selective(a):
    """"""
    if not DISREGARD_WORST_PERFORMANCES:
        return mean(a) if a else None
    sorted_a = sorted(a)
    selected_a = sorted_a[int(len(sorted_a) * DISREGARD_WORST_PERFORMANCES):]
    return mean(selected_a) if selected_a else None


def round_none(a, b=None):
    """"""
    if b is None:
        return None if a is None else round(a)
    else:
        return None if a is None else round(a, b)


def main():
    """"""
    table_output_dir = os.path.abspath(TABLE_OUTDIR)
    os.makedirs(table_output_dir, exist_ok=True)

    with open(SCENARIO_STATISTICS_JSON, 'r') as json_file:
        scenario_statistics = json.load(json_file)

    careers = {'order': ['SWORDMASTER', 'IRONBREAKER', 'KNIGHT'],
               'destro': ['BLACK_ORC', 'BLACKGUARD', 'CHOSEN']}

    mean_protection_share_acc = dict()
    mean_healing_share_acc = dict()
    mean_protheal_share_acc = dict()
    mean_dmgprotheal_share_acc = dict()
    for realm, realm_careers in careers.items():
        mean_protection_share_acc[realm] = {x: {y: {'own': list(), 'other': list()} for y in realm_careers if x != y}
                                            for x in realm_careers}
        mean_healing_share_acc[realm] = {x: {y: {'own': list(), 'other': list()} for y in realm_careers if x != y}
                                         for x in realm_careers}
        mean_protheal_share_acc[realm] = {x: {y: {'own': list(), 'other': list()} for y in realm_careers if x != y}
                                          for x in realm_careers}
        mean_dmgprotheal_share_acc[realm] = {x: {y: {'own': list(), 'other': list()} for y in realm_careers if x != y}
                                          for x in realm_careers}

    total_scenarios = len(scenario_statistics)
    total_protection = {'order': 0, 'destro': 0}
    total_healing = {'order': 0, 'destro': 0}
    total_protheal = {'order': 0, 'destro': 0}
    total_dmgprotheal = {'order': 0, 'destro': 0}

    for instance_info in tqdm(scenario_statistics.values()):
        scenario_career_protection = {'order': defaultdict(list), 'destro': defaultdict(list)}
        scenario_career_healing = {'order': defaultdict(list), 'destro': defaultdict(list)}
        scenario_career_protheal = {'order': defaultdict(list), 'destro': defaultdict(list)}
        scenario_career_dmgprotheal = {'order': defaultdict(list), 'destro': defaultdict(list)}

        scenario_protection = {'order': 0, 'destro': 0}
        scenario_healing = {'order': 0, 'destro': 0}
        scenario_protheal = {'order': 0, 'destro': 0}
        scenario_dmgprotheal = {'order': 0, 'destro': 0}

        scenario_top_protheal = dict()
        for realm, realm_careers in careers.items():
            temp = [character['healing'] + character['protection'] for character in instance_info['scoreboardEntries']
                    if character['character']['career'] in realm_careers]
            scenario_top_protheal[realm] = max(temp) if temp else 0

        for character in instance_info['scoreboardEntries']:
            # Disregard character stats if it is focused on damage and is therefore an offensively specced tank
            character_protheal = character['healing'] + character['protection']
            if character['damage'] >= character_protheal:
                continue

            career = character['character']['career']

            # Disregard if not a tank
            if career not in careers['order'] and career not in careers['destro']:
                continue

            realm = 'order' if career in careers['order'] else 'destro'

            # Disregard character stats if he achieved less than DISREGARD_THRESHOLD * top_protheal of their
            # respective realm, which is presumably because they joined the scenario late
            if character_protheal < scenario_top_protheal[realm] * DISREGARD_LATE_THRESHOLD:
                continue

            if not RR_NORMALIZATION:
                scenario_career_protection[realm][career].append(character['protection'])
                scenario_career_healing[realm][career].append(character['healing'])
                scenario_career_protheal[realm][career].append(character_protheal)
                scenario_career_dmgprotheal[realm][career].append(character_protheal + character['damage'])

                scenario_protection[realm] += character['protection']
                scenario_healing[realm] += character['healing']
                scenario_protheal[realm] += character_protheal
                scenario_dmgprotheal[realm] += character_protheal + character['damage']
            else:
                renown_rank = min([80, character['renownRank']])
                rr_norm = 80 / renown_rank

                scenario_career_protection[realm][career].append(character['protection'] * rr_norm)
                scenario_career_healing[realm][career].append(character['healing'] * rr_norm)
                scenario_career_protheal[realm][career].append(character_protheal * rr_norm)
                scenario_career_dmgprotheal[realm][career].append((character_protheal + character['damage']) * rr_norm)

                scenario_protection[realm] += character['protection'] * rr_norm
                scenario_healing[realm] += character['healing'] * rr_norm
                scenario_protheal[realm] += character_protheal * rr_norm
                scenario_dmgprotheal[realm] += (character_protheal + character['damage']) * rr_norm

        for realm in scenario_protection.keys():
            total_protection[realm] += scenario_protection[realm]
            total_healing[realm] += scenario_healing[realm]
            total_protheal[realm] += scenario_protheal[realm]
            total_dmgprotheal[realm] += scenario_dmgprotheal[realm]

        # Create average share of the scenario totals for each class in each accumulator
        career_protection_share = {'order': dict(), 'destro': dict()}
        career_healing_share = {'order': dict(), 'destro': dict()}
        career_protheal_share = {'order': dict(), 'destro': dict()}
        career_dmgprotheal_share = {'order': dict(), 'destro': dict()}

        for realm, career_acc in scenario_career_protection.items():
            for career, protection_acc in career_acc.items():
                career_protection_share[realm][career] = div_zero(mean(protection_acc), scenario_protection[realm])
        for realm, career_acc in scenario_career_healing.items():
            for career, healing_acc in career_acc.items():
                career_healing_share[realm][career] = div_zero(mean(healing_acc), scenario_healing[realm])
        for realm, career_acc in scenario_career_protheal.items():
            for career, protheal_acc in career_acc.items():
                career_protheal_share[realm][career] = div_zero(mean(protheal_acc), scenario_protheal[realm])
        for realm, career_acc in scenario_career_dmgprotheal.items():
            for career, dmgprotheal_acc in career_acc.items():
                career_dmgprotheal_share[realm][career] = div_zero(mean(dmgprotheal_acc), scenario_dmgprotheal[realm])

        # Store the relationship of each pairing of their respective share in the respective global accumulators
        for realm, career_acc in career_protection_share.items():
            for career_x, mean_protection_share_x in career_acc.items():
                for career_y, mean_protection_share_y in career_acc.items():
                    if career_x == career_y:
                        continue
                    mean_protection_share_acc[realm][career_x][career_y]['own'].append(mean_protection_share_x)
                    mean_protection_share_acc[realm][career_x][career_y]['other'].append(mean_protection_share_y)
        for realm, career_acc in career_healing_share.items():
            for career_x, mean_healing_share_x in career_acc.items():
                for career_y, mean_healing_share_y in career_acc.items():
                    if career_x == career_y:
                        continue
                    mean_healing_share_acc[realm][career_x][career_y]['own'].append(mean_healing_share_x)
                    mean_healing_share_acc[realm][career_x][career_y]['other'].append(mean_healing_share_y)
        for realm, career_acc in career_protheal_share.items():
            for career_x, mean_protheal_share_x in career_acc.items():
                for career_y, mean_protheal_share_y in career_acc.items():
                    if career_x == career_y:
                        continue
                    mean_protheal_share_acc[realm][career_x][career_y]['own'].append(mean_protheal_share_x)
                    mean_protheal_share_acc[realm][career_x][career_y]['other'].append(mean_protheal_share_y)
        for realm, career_acc in career_dmgprotheal_share.items():
            for career_x, mean_dmgprotheal_share_x in career_acc.items():
                for career_y, mean_dmgprotheal_share_y in career_acc.items():
                    if career_x == career_y:
                        continue
                    mean_dmgprotheal_share_acc[realm][career_x][career_y]['own'].append(mean_dmgprotheal_share_x)
                    mean_dmgprotheal_share_acc[realm][career_x][career_y]['other'].append(mean_dmgprotheal_share_y)

    # Now that the mean protection share for each class relationship is known and also the total protection, healing and
    # protheal in all scenarios for the respective realm can the mean protection share be converted back to absolute
    # numbers taking the average protection, healing and protheal for each realm as reference
    mean_protection = {'order': total_protection['order'] / total_scenarios,
                       'destro': total_protection['destro'] / total_scenarios}
    mean_healing = {'order': total_healing['order'] / total_scenarios,
                    'destro': total_healing['destro'] / total_scenarios}
    mean_protheal = {'order': total_protheal['order'] / total_scenarios,
                     'destro': total_protheal['destro'] / total_scenarios}
    mean_dmgprotheal = {'order': total_dmgprotheal['order'] / total_scenarios,
                     'destro': total_dmgprotheal['destro'] / total_scenarios}

    protection_career_relative = dict()
    healing_career_relative = dict()
    protheal_career_relative = dict()
    dmgprotheal_career_relative = dict()
    for realm, realm_careers in careers.items():
        protection_career_relative[realm] = {x: {y: {'own': list(), 'other': list()} for y in realm_careers if x != y}
                                             for x in realm_careers}
        healing_career_relative[realm] = {x: {y: {'own': list(), 'other': list()} for y in realm_careers if x != y}
                                          for x in realm_careers}
        protheal_career_relative[realm] = {x: {y: {'own': list(), 'other': list()} for y in realm_careers if x != y}
                                           for x in realm_careers}
        dmgprotheal_career_relative[realm] = {x: {y: {'own': list(), 'other': list()} for y in realm_careers if x != y}
                                           for x in realm_careers}

    for realm, realm_careers in careers.items():
        for career_x in realm_careers:
            for career_y in realm_careers:
                if career_x == career_y:
                    continue
                mean_own_protection_share = mean_selective(mean_protection_share_acc[realm][career_x][career_y]['own'])
                mean_other_protection_share = \
                    mean_selective(mean_protection_share_acc[realm][career_x][career_y]['other'])
                mean_own_protection = round_none(mean_own_protection_share * mean_protection[realm])
                mean_other_protection = round_none(mean_other_protection_share * mean_protection[realm])
                protection_career_relative[realm][career_x][career_y]['own'] = mean_own_protection
                protection_career_relative[realm][career_x][career_y]['other'] = mean_other_protection

                mean_own_healing_share = mean_selective(mean_healing_share_acc[realm][career_x][career_y]['own'])
                mean_other_healing_share = mean_selective(mean_healing_share_acc[realm][career_x][career_y]['other'])
                mean_own_healing = round_none(mean_own_healing_share * mean_healing[realm])
                mean_other_healing = round_none(mean_other_healing_share * mean_healing[realm])
                healing_career_relative[realm][career_x][career_y]['own'] = mean_own_healing
                healing_career_relative[realm][career_x][career_y]['other'] = mean_other_healing

                mean_own_protheal_share = mean_selective(mean_protheal_share_acc[realm][career_x][career_y]['own'])
                mean_other_protheal_share = mean_selective(mean_protheal_share_acc[realm][career_x][career_y]['other'])
                mean_own_protheal = round_none(mean_own_protheal_share * mean_protheal[realm])
                mean_other_protheal = round_none(mean_other_protheal_share * mean_protheal[realm])
                protheal_career_relative[realm][career_x][career_y]['own'] = mean_own_protheal
                protheal_career_relative[realm][career_x][career_y]['other'] = mean_other_protheal

                mean_own_dmgprotheal_share = \
                    mean_selective(mean_dmgprotheal_share_acc[realm][career_x][career_y]['own'])
                mean_other_dmgprotheal_share = \
                    mean_selective(mean_dmgprotheal_share_acc[realm][career_x][career_y]['other'])
                mean_own_dmgprotheal = round_none(mean_own_dmgprotheal_share * mean_dmgprotheal[realm])
                mean_other_dmgprotheal = round_none(mean_other_dmgprotheal_share * mean_dmgprotheal[realm])
                dmgprotheal_career_relative[realm][career_x][career_y]['own'] = mean_own_dmgprotheal
                dmgprotheal_career_relative[realm][career_x][career_y]['other'] = mean_other_dmgprotheal

    # Create matplotlib table of the analysed data
    print("Creating matplotlib table plots...")
    for description, career_relative_stat in {'healing': healing_career_relative,
                                              'protection': protection_career_relative,
                                              'protection_and_heal': protheal_career_relative,
                                              'damage_and_protection_and_heal': dmgprotheal_career_relative}.items():
        for realm, realm_career_relative_stat in career_relative_stat.items():
            row_labels = careers[realm]
            col_labels = careers[realm] + ['ROW-AVERAGE']

            table_values = list()
            for row_career in row_labels:
                row_values = list()
                row_values_avg_acc = (list(), list())
                for col_career in col_labels:
                    if row_career == col_career:
                        row_values.append("")
                    elif col_career == 'ROW-AVERAGE':
                        if not row_values_avg_acc[0]:
                            row_values.append("(DPs: 0)")
                            continue
                        row_value_own = mean(row_values_avg_acc[0])
                        row_value_other = mean(row_values_avg_acc[1])
                        if row_value_own < 100:
                            row_value_own = round(row_value_own, 1)
                            row_value_other = round(row_value_other, 1)
                        else:
                            row_value_own = round(row_value_own)
                            row_value_other = round(row_value_other)
                        relation = round(div_zero(row_value_own, row_value_other), 2)
                        row_values.append(f"{row_value_own}:{row_value_other}\n"
                                          f"{relation}")
                    else:
                        own_stat = realm_career_relative_stat[row_career][col_career]['own']
                        other_stat = realm_career_relative_stat[row_career][col_career]['other']
                        if own_stat is None or other_stat is None:
                            row_values.append('(DPs: 0)')
                            continue
                        relation = round(div_zero(own_stat, other_stat), 2)
                        # Any acc list is possible here since all contain equal amount of data for respective relation
                        if not DISREGARD_WORST_PERFORMANCES:
                            datapoint_count = len(mean_healing_share_acc[realm][row_career][col_career]['own'])
                        else:
                            datapoint_count = int(len(mean_healing_share_acc[realm][row_career][col_career]['own'])
                                                  * (1 - DISREGARD_WORST_PERFORMANCES))
                        row_values.append(f"{own_stat}:{other_stat}\n"
                                          f"{relation}\n"
                                          f"(DPs: {datapoint_count})")
                        row_values_avg_acc[0].append(own_stat)
                        row_values_avg_acc[1].append(other_stat)
                table_values.append(row_values)

            fig, ax = plt.subplots()
            fig.set_figheight(1)
            fig.set_figwidth(2)
            ax.set_axis_off()
            table = ax.table(cellText=table_values,
                             rowLabels=row_labels,
                             colLabels=col_labels,
                             rowColours=['lightblue'] * len(row_labels),
                             colColours=['lightblue'] * (len(col_labels) - 1) + ['coral'],
                             cellLoc='center',
                             loc='upper left')
            table.auto_set_font_size(False)
            for _, cell in table.get_celld().items():
                cell.set_text_props(fontproperties=FontProperties(size=3, weight='bold'))

            table_title = TABLE_TITLE.format(description, realm) + f'\n\nsource: {SCENARIO_STATISTICS_JSON}'
            ax.set_title(table_title, fontsize=6, fontweight="bold")
            table_filepath = table_output_dir + '/' + TABLE_TITLE.format(description, realm) + '.png'
            plt.savefig(table_filepath, dpi=600, bbox_inches='tight')

    print('fin')


if __name__ == '__main__':
    main()
