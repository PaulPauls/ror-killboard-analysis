import json
from statistics import mean
from collections import defaultdict
from tqdm import tqdm

SCENARIO_STATISTICS_JSON = './subdivided_scenario_statistics/scenario_statistics_t4_standard.json'


def main():
    """"""
    with open(SCENARIO_STATISTICS_JSON, 'r') as json_file:
        scenario_statistics = json.load(json_file)

    order_careers = ['SWORDMASTER', 'IRONBREAKER', 'KNIGHT', 'WHITE_LION', 'SLAYER', 'WITCH_HUNTER', 'ENGINEER',
                     'SHADOW_WARRIOR', 'BRIGHT_WIZARD', 'ARCHMAGE', 'RUNE_PRIEST', 'WARRIOR_PRIEST']
    destro_careers = ['BLACK_ORC', 'BLACKGUARD', 'CHOSEN', 'MARAUDER', 'CHOPPA', 'WITCH_ELF', 'MAGUS', 'SQUIG_HERDER',
                      'SORCERER', 'SHAMAN', 'ZEALOT', 'DISCIPLE']

    career_win_loss_acc = defaultdict(list)
    order_wins = 0
    destro_wins = 0

    for instance_info in tqdm(scenario_statistics.values()):
        # The winner is manually determined by comparing scenario points as a draw in points results in the
        # 'winner' field being set to 0, same as when order wins.
        # A draw is set to not influence the win/loss rate of a career
        order_points, destro_points = instance_info['points']
        if order_points > destro_points:
            order_wins += 1
            # Order won. Append 1 to order chars win rate
            for character in instance_info['scoreboardEntries']:
                career = character['character']['career']
                if career in order_careers:
                    career_win_loss_acc[career].append(1)
                else:
                    career_win_loss_acc[career].append(0)
        elif destro_points > order_points:
            destro_wins += 1
            # Destro won. Append 1 to destro chars win rate
            for character in instance_info['scoreboardEntries']:
                career = character['character']['career']
                if career in order_careers:
                    career_win_loss_acc[career].append(0)
                else:
                    career_win_loss_acc[career].append(1)
        else:
            continue

    total_scenarios = len(scenario_statistics)
    order_win_ratio = round(100 * order_wins / total_scenarios, 1)
    destro_win_ratio = round(100 * destro_wins / total_scenarios, 1)

    print(f"Source: {SCENARIO_STATISTICS_JSON}\n\n"
          f"Order Win-Rate: {order_win_ratio}%\n"
          f"Order Careers Win-Rate:")
    for career in order_careers:
        win_rate = round(100 * mean(career_win_loss_acc[career]), 1)
        win_rate_diff = round(win_rate - order_win_ratio, 1)
        win_rate_diff_str = f'+{win_rate_diff}' if win_rate_diff > 0 else str(win_rate_diff)
        print(f"{str(career) + ':':<15}{win_rate:>5}% ({win_rate_diff_str}%)")

    print(f"\nDestro Win-Rate: {destro_win_ratio}%\n"
          f"Destro Careers Win-Rate:")
    for career in destro_careers:
        win_rate = round(100 * mean(career_win_loss_acc[career]), 1)
        win_rate_diff = round(win_rate - destro_win_ratio, 1)
        win_rate_diff_str = f'+{win_rate_diff}' if win_rate_diff > 0 else str(win_rate_diff)
        print(f"{str(career) + ':':<15}{win_rate:>5}% ({win_rate_diff_str}%)")

    print('\nfin')


if __name__ == '__main__':
    main()
