import json
from tqdm import tqdm

SCENARIO_STATISTICS_JSON = './subdivided_scenario_statistics/scenario_statistics_t4_standard.json'


def main():
    """"""
    with open(SCENARIO_STATISTICS_JSON, 'r') as json_file:
        scenario_statistics = json.load(json_file)

    order_wins = 0
    total_order_points = 0
    destro_wins = 0
    total_destro_points = 0
    draws = 0

    for instance_info in tqdm(scenario_statistics.values()):
        # The winner is manually determined by comparing scenario points as a draw in points results in the
        # 'winner' field being set to 0, same as when order wins
        order_points, destro_points = instance_info['points']
        if order_points > destro_points:
            order_wins += 1
        elif destro_points > order_points:
            destro_wins += 1
        else:
            draws += 1
        total_order_points += order_points
        total_destro_points += destro_points

    total_scenarios = len(scenario_statistics)
    order_win_ratio = round(100 * order_wins / total_scenarios, 1)
    destro_win_ratio = round(100 * destro_wins / total_scenarios, 1)
    draw_ratio = round(100 * draws / total_scenarios, 1)

    print(
        f"Source: {SCENARIO_STATISTICS_JSON}\n\n"
        f"{'Total Scenarios:':<16}{total_scenarios:>8}\n"
        f"{'Order Wins:':<16}{order_wins:>8} ({order_win_ratio}%) [total points: {total_order_points}]\n"
        f"{'Destro Wins:':<16}{destro_wins:>8} ({destro_win_ratio}%) [total points: {total_destro_points}]\n"
        f"{'Draws:':<16}{draws:>8} ({draw_ratio}%)\n"
    )

    print('fin')


if __name__ == '__main__':
    main()
