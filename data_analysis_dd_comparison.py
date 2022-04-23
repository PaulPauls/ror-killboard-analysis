import os
import json
import matplotlib.pyplot as plt
from tqdm import tqdm
from statistics import mean
from collections import defaultdict
from matplotlib.font_manager import FontProperties

SCENARIO_STATISTICS_JSON = './subdivided_scenario_statistics/scenario_statistics_t4_standard.json'
TABLE_TITLE = "mean_{}_career-relative_in_t4_standard_scenarios_-_{}"
TABLE_OUTDIR = './dd_comparison_tables_t4_standard/'
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

    careers = {'order': ['SWORDMASTER', 'IRONBREAKER', 'KNIGHT', 'WHITE_LION', 'SLAYER', 'WITCH_HUNTER', 'ENGINEER',
                         'SHADOW_WARRIOR', 'BRIGHT_WIZARD', 'ARCHMAGE', 'RUNE_PRIEST', 'WARRIOR_PRIEST'],
               'destro': ['BLACK_ORC', 'BLACKGUARD', 'CHOSEN', 'MARAUDER', 'CHOPPA', 'WITCH_ELF', 'MAGUS',
                          'SQUIG_HERDER', 'SORCERER', 'SHAMAN', 'ZEALOT', 'DISCIPLE']}

    mean_damage_share_acc = dict()
    mean_deathblows_share_acc = dict()
    mean_kill_damage_share_acc = dict()
    for realm, realm_careers in careers.items():
        mean_damage_share_acc[realm] = {x: {y: {'own': list(), 'other': list()} for y in realm_careers if x != y}
                                        for x in realm_careers}
        mean_deathblows_share_acc[realm] = {x: {y: {'own': list(), 'other': list()} for y in realm_careers if x != y}
                                            for x in realm_careers}
        mean_kill_damage_share_acc[realm] = {x: {y: {'own': list(), 'other': list()} for y in realm_careers if x != y}
                                             for x in realm_careers}

    total_scenarios = len(scenario_statistics)
    total_damage = {'order': 0, 'destro': 0}
    total_deathblows = {'order': 0, 'destro': 0}
    total_kill_damage = {'order': 0, 'destro': 0}

    for instance_info in tqdm(scenario_statistics.values()):
        scenario_career_damage = {'order': defaultdict(list), 'destro': defaultdict(list)}
        scenario_career_deathblows = {'order': defaultdict(list), 'destro': defaultdict(list)}
        scenario_career_kill_damage = {'order': defaultdict(list), 'destro': defaultdict(list)}

        scenario_damage = {'order': 0, 'destro': 0}
        scenario_deathblows = {'order': 0, 'destro': 0}
        scenario_kill_damage = {'order': 0, 'destro': 0}

        scenario_top_damage = dict()
        for realm, realm_careers in careers.items():
            scenario_top_damage[realm] = max([character['damage'] for character in instance_info['scoreboardEntries']
                                              if character['character']['career'] in realm_careers])

        for character in instance_info['scoreboardEntries']:
            # Disregard character stats if it is focused on healing and protection and is therefore a defensively
            # or support specced tank or healer
            total_healing_protection = character['healing'] + character['protection']
            if total_healing_protection >= character['damage']:
                continue

            career = character['character']['career']
            realm = 'order' if career in careers['order'] else 'destro'

            # Disregard character stats if he achieved less than DISREGARD_THRESHOLD * top_damage of their
            # respective realm, which is presumably because they joined the scenario late
            if character['damage'] < scenario_top_damage[realm] * DISREGARD_LATE_THRESHOLD:
                continue

            if not RR_NORMALIZATION:
                scenario_career_damage[realm][career].append(character['damage'])
                scenario_career_deathblows[realm][career].append(character['deathBlows'])
                scenario_career_kill_damage[realm][career].append(character['killDamage'])

                scenario_damage[realm] += character['damage']
                scenario_deathblows[realm] += character['deathBlows']
                scenario_kill_damage[realm] += character['killDamage']
            else:
                renown_rank = min([80, character['renownRank']])
                rr_norm = 80 / renown_rank

                scenario_career_damage[realm][career].append(character['damage'] * rr_norm)
                scenario_career_deathblows[realm][career].append(character['deathBlows'] * rr_norm)
                scenario_career_kill_damage[realm][career].append(character['killDamage'] * rr_norm)

                scenario_damage[realm] += character['damage'] * rr_norm
                scenario_deathblows[realm] += character['deathBlows'] * rr_norm
                scenario_kill_damage[realm] += character['killDamage'] * rr_norm

        for realm in scenario_damage.keys():
            total_damage[realm] += scenario_damage[realm]
            total_deathblows[realm] += scenario_deathblows[realm]
            total_kill_damage[realm] += scenario_kill_damage[realm]

        # Create average share of the scenario totals for each class in each accumulator
        career_damage_share = {'order': dict(), 'destro': dict()}
        career_deathblows_share = {'order': dict(), 'destro': dict()}
        career_kill_damage_share = {'order': dict(), 'destro': dict()}

        for realm, career_acc in scenario_career_damage.items():
            for career, damage_acc in career_acc.items():
                career_damage_share[realm][career] = div_zero(mean(damage_acc), scenario_damage[realm])
        for realm, career_acc in scenario_career_deathblows.items():
            for career, deathblow_acc in career_acc.items():
                career_deathblows_share[realm][career] = div_zero(mean(deathblow_acc), scenario_deathblows[realm])
        for realm, career_acc in scenario_career_kill_damage.items():
            for career, kill_damage_acc in career_acc.items():
                career_kill_damage_share[realm][career] = div_zero(mean(kill_damage_acc), scenario_kill_damage[realm])

        # Store the relationship of each pairing of their respective share in the respective global accumulators
        for realm, career_acc in career_damage_share.items():
            for career_x, mean_damage_share_x in career_acc.items():
                for career_y, mean_damage_share_y in career_acc.items():
                    if career_x == career_y:
                        continue
                    mean_damage_share_acc[realm][career_x][career_y]['own'].append(mean_damage_share_x)
                    mean_damage_share_acc[realm][career_x][career_y]['other'].append(mean_damage_share_y)
        for realm, career_acc in career_deathblows_share.items():
            for career_x, mean_deathblows_share_x in career_acc.items():
                for career_y, mean_deathblows_share_y in career_acc.items():
                    if career_x == career_y:
                        continue
                    mean_deathblows_share_acc[realm][career_x][career_y]['own'].append(mean_deathblows_share_x)
                    mean_deathblows_share_acc[realm][career_x][career_y]['other'].append(mean_deathblows_share_y)
        for realm, career_acc in career_kill_damage_share.items():
            for career_x, mean_kill_damage_share_x in career_acc.items():
                for career_y, mean_kill_damage_share_y in career_acc.items():
                    if career_x == career_y:
                        continue
                    mean_kill_damage_share_acc[realm][career_x][career_y]['own'].append(mean_kill_damage_share_x)
                    mean_kill_damage_share_acc[realm][career_x][career_y]['other'].append(mean_kill_damage_share_y)

    # Now that the mean damage share for each class relationship is known and also the total damage, deathblows and
    # kill damage in all scenarios for the respective realm can the mean damage share be converted back to absolute
    # numbers taking the average damage, deathblows and kill damage for each realm as reference
    mean_damage = {'order': total_damage['order'] / total_scenarios,
                   'destro': total_damage['destro'] / total_scenarios}
    mean_deathblows = {'order': total_deathblows['order'] / total_scenarios,
                       'destro': total_deathblows['destro'] / total_scenarios}
    mean_kill_damage = {'order': total_kill_damage['order'] / total_scenarios,
                        'destro': total_kill_damage['destro'] / total_scenarios}

    damage_career_relative = dict()
    deathblows_career_relative = dict()
    kill_damage_career_relative = dict()
    for realm, realm_careers in careers.items():
        damage_career_relative[realm] = {x: {y: {'own': list(), 'other': list()} for y in realm_careers if x != y}
                                         for x in realm_careers}
        deathblows_career_relative[realm] = {x: {y: {'own': list(), 'other': list()} for y in realm_careers if x != y}
                                             for x in realm_careers}
        kill_damage_career_relative[realm] = {x: {y: {'own': list(), 'other': list()} for y in realm_careers if x != y}
                                              for x in realm_careers}

    for realm, realm_careers in careers.items():
        for career_x in realm_careers:
            for career_y in realm_careers:
                if career_x == career_y:
                    continue
                mean_own_damage_share = mean_selective(mean_damage_share_acc[realm][career_x][career_y]['own'])
                mean_other_damage_share = mean_selective(mean_damage_share_acc[realm][career_x][career_y]['other'])
                mean_own_damage = round_none(mean_own_damage_share * mean_damage[realm])
                mean_other_damage = round_none(mean_other_damage_share * mean_damage[realm])
                damage_career_relative[realm][career_x][career_y]['own'] = mean_own_damage
                damage_career_relative[realm][career_x][career_y]['other'] = mean_other_damage

                mean_own_deathblows_share = mean_selective(mean_deathblows_share_acc[realm][career_x][career_y]['own'])
                mean_other_deathblows_share = \
                    mean_selective(mean_deathblows_share_acc[realm][career_x][career_y]['other'])
                mean_own_deathblows = round_none(mean_own_deathblows_share * mean_deathblows[realm], 1)
                mean_other_deathblows = round_none(mean_other_deathblows_share * mean_deathblows[realm], 1)
                deathblows_career_relative[realm][career_x][career_y]['own'] = mean_own_deathblows
                deathblows_career_relative[realm][career_x][career_y]['other'] = mean_other_deathblows

                mean_own_kill_damage_share = \
                    mean_selective(mean_kill_damage_share_acc[realm][career_x][career_y]['own'])
                mean_other_kill_damage_share = \
                    mean_selective(mean_kill_damage_share_acc[realm][career_x][career_y]['other'])
                mean_own_kill_damage = round_none(mean_own_kill_damage_share * mean_kill_damage[realm])
                mean_other_kill_damage = round_none(mean_other_kill_damage_share * mean_kill_damage[realm])
                kill_damage_career_relative[realm][career_x][career_y]['own'] = mean_own_kill_damage
                kill_damage_career_relative[realm][career_x][career_y]['other'] = mean_other_kill_damage

    # Create matplotlib table of the analysed data
    print("Creating matplotlib table plots...")
    for description, career_relative_stat in {'damage': damage_career_relative,
                                              'deathblows': deathblows_career_relative,
                                              'kill_damage': kill_damage_career_relative}.items():
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
                            datapoint_count = len(mean_damage_share_acc[realm][row_career][col_career]['own'])
                        else:
                            datapoint_count = int(len(mean_damage_share_acc[realm][row_career][col_career]['own'])
                                                  * (1 - DISREGARD_WORST_PERFORMANCES))
                        row_values.append(f"{own_stat}:{other_stat}\n"
                                          f"{relation}\n"
                                          f"(DPs: {datapoint_count})")
                        row_values_avg_acc[0].append(own_stat)
                        row_values_avg_acc[1].append(other_stat)
                table_values.append(row_values)

            fig, ax = plt.subplots()
            fig.set_figheight(3)
            fig.set_figwidth(6.4)
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
