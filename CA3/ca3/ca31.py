import random
import time
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple, Dict, Set
import pandas as pd
import sys


def FL_ca3(A: List[int], G: int, favorite: str) -> Dict:
    """
    Main function for Grandma Rosa's card distribution problem
    Favorite: 'melanie' (favorite), 'selena' (second favorite), 'camila'
    """
    grandchildren = ['melanie', 'selena', 'camila']

    print(f">> Grandma Rosa has a deck of {len(A)} cards and wants to distribute it to {G} grandchildren.")
    print(f">> When she passed, her favorite grandchild was {favorite}.")
    print()

    if G == 1:
        return handle_one_grandchild(A, favorite, grandchildren)
    elif G == 2:
        return handle_two_grandchildren(A, favorite, grandchildren)
    elif G == 3:
        return handle_three_grandchildren(A, favorite, grandchildren)


def handle_one_grandchild(A: List[int], favorite: str, grandchildren: List[str]) -> Dict:
    """G=1: Assign all cards to the favorite"""
    assignments = {child: {'cards': [], 'value': 0} for child in grandchildren}
    assignments[favorite]['cards'] = list(range(1, len(A) + 1))
    assignments[favorite]['value'] = sum(A)

    for child in grandchildren:
        card_info = assignments[child]
        print(
            f">> {child.capitalize()} would get cards {card_info['cards']} with a total value of ${card_info['value']}")

    return {'assignments': assignments, 'excluded_cards': [], 'scenario': '1_grandchild'}


def handle_two_grandchildren(A: List[int], favorite: str, grandchildren: List[str]) -> Dict:
    """G=2: Handle both scenarios"""
    other_child = [child for child in grandchildren if child != favorite][0]

    print(">> Scenario 1 -- Favorite with another grandchild")
    result1 = handle_two_with_favorite(A, favorite, other_child, grandchildren)

    print("\n>> Scenario 2 -- Two grandchildren without favorite")
    second_favorite = 'selena'
    other = 'camila'
    result2 = handle_two_without_favorite(A, second_favorite, other, grandchildren)

    return result1


def handle_two_with_favorite(A: List[int], favorite: str, other: str, grandchildren: List[str]) -> Dict:
    """Favorite gets higher value than other"""
    total_value = sum(A)

    # Find partition where favorite gets more
    n = len(A)
    target = total_value // 2
    dp = [[False] * (target + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        dp[i][0] = True

    for i in range(1, n + 1):
        for j in range(1, target + 1):
            if A[i - 1] <= j:
                dp[i][j] = dp[i - 1][j] or dp[i - 1][j - A[i - 1]]
            else:
                dp[i][j] = dp[i - 1][j]

    # Find partition where favorite gets strictly more
    best_other_sum = 0
    for j in range(target, -1, -1):
        if dp[n][j] and (total_value - j) > j:
            best_other_sum = j
            break

    # If no partition with favorite getting more, use closest and discard cards
    if best_other_sum == 0:
        # Find the partition that gives favorite the maximum possible advantage
        max_favorite_advantage = -float('inf')
        for j in range(target, -1, -1):
            if dp[n][j]:
                favorite_advantage = (total_value - j) - j
                if favorite_advantage > max_favorite_advantage:
                    max_favorite_advantage = favorite_advantage
                    best_other_sum = j

    # Reconstruct partitions
    other_indices = set()
    i, j = n, best_other_sum
    while i > 0 and j >= 0:
        if not dp[i - 1][j]:
            other_indices.add(i - 1)
            j -= A[i - 1]
        i -= 1

    favorite_cards = [idx + 1 for idx in range(n) if idx not in other_indices]
    other_cards = [idx + 1 for idx in other_indices]

    favorite_value = sum(A[idx] for idx in range(n) if idx not in other_indices)
    other_value = best_other_sum

    # Use card discard to ensure favorite has higher value
    excluded_cards = []
    if favorite_value <= other_value:
        # Discard cards from other to make favorite have higher value
        target_other = favorite_value - 1
        if target_other >= 0:
            other_cards, excluded = discard_cards_to_value(A, other_cards, target_other)
            excluded_cards.extend(excluded)
            other_value = target_other
        else:
            # If favorite_value is 0 or 1, discard from favorite to create difference
            target_favorite = other_value + 1
            favorite_cards, excluded = discard_cards_to_value(A, favorite_cards, target_favorite)
            excluded_cards.extend(excluded)
            favorite_value = target_favorite

    assignments = {
        favorite: {'cards': favorite_cards, 'value': favorite_value},
        other: {'cards': other_cards, 'value': other_value},
        [child for child in grandchildren if child not in [favorite, other]][0]: {'cards': [], 'value': 0}
    }

    print(f">> If the deck were being distributed to {favorite} and {other}, then")
    for child in grandchildren:
        card_info = assignments[child]
        print(
            f">> {child.capitalize()} would get cards {card_info['cards']} with a total value of ${card_info['value']}")

    if excluded_cards:
        print(f">> Cards excluded: {excluded_cards}")

    return {'assignments': assignments, 'excluded_cards': excluded_cards, 'scenario': '2_with_favorite'}


def handle_two_without_favorite(A: List[int], child1: str, child2: str, grandchildren: List[str]) -> Dict:
    """Equal distribution between two children using card discard"""
    total_value = sum(A)
    target = total_value // 2

    n = len(A)
    dp = [[False] * (target + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        dp[i][0] = True

    for i in range(1, n + 1):
        for j in range(1, target + 1):
            if A[i - 1] <= j:
                dp[i][j] = dp[i - 1][j] or dp[i - 1][j - A[i - 1]]
            else:
                dp[i][j] = dp[i - 1][j]

    # Find closest partition to target
    best_sum = 0
    for j in range(target, -1, -1):
        if dp[n][j]:
            best_sum = j
            break

    # Reconstruct partitions
    child1_indices = set()
    i, j = n, best_sum
    while i > 0 and j >= 0:
        if not dp[i - 1][j]:
            child1_indices.add(i - 1)
            j -= A[i - 1]
        i -= 1

    child1_cards = [idx + 1 for idx in child1_indices]
    child2_cards = [idx + 1 for idx in range(n) if idx not in child1_indices]

    child1_value = best_sum
    child2_value = total_value - best_sum

    # Equalize using card discard
    excluded_cards = []
    target_value = min(child1_value, child2_value)

    if child1_value > target_value:
        child1_cards, excluded = discard_cards_to_value(A, child1_cards, target_value)
        excluded_cards.extend(excluded)

    if child2_value > target_value:
        child2_cards, excluded = discard_cards_to_value(A, child2_cards, target_value)
        excluded_cards.extend(excluded)

    assignments = {
        child1: {'cards': child1_cards, 'value': target_value},
        child2: {'cards': child2_cards, 'value': target_value},
        [child for child in grandchildren if child not in [child1, child2]][0]: {'cards': [], 'value': 0}
    }

    print(f">> If the deck were being distributed to {child1} and {child2}, then")
    for child in grandchildren:
        card_info = assignments[child]
        print(
            f">> {child.capitalize()} would get cards {card_info['cards']} with a total value of ${card_info['value']}")

    if excluded_cards:
        print(f">> Cards excluded: {excluded_cards}")
    else:
        print(">> No cards were excluded")

    return {'assignments': assignments, 'excluded_cards': excluded_cards, 'scenario': '2_without_favorite'}


def handle_three_grandchildren(A: List[int], favorite: str, grandchildren: List[str]) -> Dict:
    """G=3: Favorite gets highest, second favorite gets second highest, third gets lowest"""
    second_favorite = 'selena'
    third_child = 'camila'

    total_value = sum(A)

    # Get initial partitions using greedy approach
    partitions = multiway_partition_greedy(A, 3)
    values = [sum(A[i - 1] for i in partition) for partition in partitions]

    # Sort by value descending
    partitions_with_values = list(zip(partitions, values))
    partitions_with_values.sort(key=lambda x: x[1], reverse=True)

    # Assign to grandchildren in preference order
    favorite_cards, favorite_value = partitions_with_values[0]
    second_cards, second_value = partitions_with_values[1]
    third_cards, third_value = partitions_with_values[2]

    # Use card discard to establish hierarchy: favorite > second > third
    excluded_cards = []

    # Ensure second favorite has less than favorite
    if second_value >= favorite_value:
        target_second = favorite_value - 1 if favorite_value > 1 else 0
        second_cards, excluded = discard_cards_to_value(A, second_cards, target_second)
        excluded_cards.extend(excluded)
        second_value = target_second

    # Ensure third has less than or equal to second (but we want less for hierarchy)
    if third_value >= second_value:
        target_third = second_value - 1 if second_value > 1 else 0
        third_cards, excluded = discard_cards_to_value(A, third_cards, target_third)
        excluded_cards.extend(excluded)
        third_value = target_third

    # Further optimize to minimize differences while maintaining hierarchy
    if favorite_value - second_value > 1 and len(favorite_cards) > 1:
        # Can reduce favorite's value to be closer to second
        target_favorite = second_value + 1
        favorite_cards, excluded = discard_cards_to_value(A, favorite_cards, target_favorite)
        excluded_cards.extend(excluded)
        favorite_value = target_favorite

    assignments = {
        favorite: {'cards': favorite_cards, 'value': favorite_value},
        second_favorite: {'cards': second_cards, 'value': second_value},
        third_child: {'cards': third_cards, 'value': third_value}
    }

    print(">> Scenario 1 -- Possibility 1")
    print(">> If the deck were being distributed to all three grandchildren, then")
    for child in grandchildren:
        card_info = assignments[child]
        print(
            f">> {child.capitalize()} would get cards {card_info['cards']} with a total value of ${card_info['value']}")

    # Verify hierarchy
    if (assignments[favorite]['value'] > assignments[second_favorite]['value'] and
            assignments[second_favorite]['value'] > assignments[third_child]['value']):
        print(">> Hierarchy maintained: Favorite > Second Favorite > Third")

    if excluded_cards:
        print(f">> Cards excluded to maintain hierarchy: {excluded_cards}")
    else:
        print(">> No cards were excluded")

    return {'assignments': assignments, 'excluded_cards': excluded_cards, 'scenario': '3_grandchildren'}


def discard_cards_to_value(A: List[int], cards: List[int], target_value: int) -> Tuple[List[int], List[int]]:
    """Discard cards to achieve exactly target_value"""
    current_value = sum(A[card - 1] for card in cards)

    if current_value <= target_value:
        return cards, []  # Cannot increase value

    # Sort cards by value descending (discard larger ones first)
    card_values = [(card, A[card - 1]) for card in cards]
    card_values.sort(key=lambda x: x[1], reverse=True)

    remaining_cards = cards.copy()
    discarded_cards = []
    current_val = current_value

    for card, value in card_values:
        if current_val - value >= target_value:
            remaining_cards.remove(card)
            discarded_cards.append(card)
            current_val -= value
        if current_val == target_value:
            break

    return remaining_cards, discarded_cards


def multiway_partition_greedy(A: List[int], G: int) -> List[List[int]]:
    """Greedy multi-way partitioning"""
    indices = sorted(range(len(A)), key=lambda i: A[i], reverse=True)
    sums = [0] * G
    partitions = [[] for _ in range(G)]

    for idx in indices:
        min_idx = np.argmin(sums)
        partitions[min_idx].append(idx + 1)
        sums[min_idx] += A[idx]

    return partitions


def FL_ec_ca3(A: List[int], G: int) -> Dict:
    """Extra credit: All grandchildren get EXACTLY equal value using card discard"""
    if G == 1:
        assignments = {'Grandchild 1': {'cards': list(range(1, len(A) + 1)), 'value': sum(A)}}
        excluded = []
    else:
        total_value = sum(A)
        target_value = total_value // G

        # Get initial partitions
        partitions = multiway_partition_greedy(A, G)
        values = [sum(A[i - 1] for i in partition) for partition in partitions]

        # Find the minimum achievable value for all (may need to discard cards)
        min_achievable = min(values)

        # Discard cards to make all partitions equal to min_achievable
        equalized_partitions = []
        discarded_cards = []

        for i, partition in enumerate(partitions):
            current_value = values[i]
            if current_value > min_achievable:
                remaining, discarded = discard_cards_to_value(A, partition, min_achievable)
                equalized_partitions.append(remaining)
                discarded_cards.extend(discarded)
            else:
                equalized_partitions.append(partition)

        assignments = {}
        final_values = []
        for i in range(G):
            value = sum(A[card - 1] for card in equalized_partitions[i])
            assignments[f'Grandchild {i + 1}'] = {
                'cards': equalized_partitions[i],
                'value': value
            }
            final_values.append(value)

        excluded = discarded_cards

    print(f">> Extra Credit: Distributing {len(A)} cards among {G} grandchildren")
    print(">> Distribution results:")
    for grandchild, info in assignments.items():
        print(f">> {grandchild} would get cards {info['cards']} with a total value of ${info['value']}")

    values = [info['value'] for info in assignments.values()]
    if len(set(values)) == 1:
        print(">> Perfect equal distribution achieved!")
    else:
        # If not perfectly equal, try harder by reducing to the next lower achievable value
        min_val = min(values)
        if min_val > 0:
            print(f">> Re-adjusting to achieve perfect equality...")
            re_equalized_partitions = []
            re_discarded_cards = []

            for i, partition in enumerate(equalized_partitions):
                current_value = values[i]
                if current_value > min_val:
                    remaining, discarded = discard_cards_to_value(A, partition, min_val)
                    re_equalized_partitions.append(remaining)
                    re_discarded_cards.extend(discarded)
                else:
                    re_equalized_partitions.append(partition)

            # Update assignments
            for i in range(G):
                value = sum(A[card - 1] for card in re_equalized_partitions[i])
                assignments[f'Grandchild {i + 1}'] = {
                    'cards': re_equalized_partitions[i],
                    'value': value
                }

            excluded.extend(re_discarded_cards)

            final_values = [info['value'] for info in assignments.values()]
            if len(set(final_values)) == 1:
                print(">> Perfect equal distribution now achieved!")
            else:
                print(
                    f">> Best achievable equal distribution (max difference: {max(final_values) - min(final_values)})")

    if excluded:
        print(f">> Cards discarded to achieve equality: {excluded}")
    else:
        print(">> No cards were discarded")

    return {
        'assignments': assignments,
        'excluded_cards': excluded,
        'scenario': f'{G}_grandchildren'
    }


# ... (Keep the experiment functions exactly the same as before)

def run_main_experiments():
    """Run experiments for main assignment"""
    print("=== RUNNING MAIN ASSIGNMENT EXPERIMENTS ===")

    sizes = [1, 2, 4, 8, 16, 32, 64, 128, 256]
    G_values = [1, 2, 3]
    favorite = 'melanie'

    results = {}

    for size in sizes:
        print(f"Testing array size: {size}")
        results[size] = {}
        A = [random.randint(1, 50) for _ in range(size)]

        for G in G_values:
            try:
                start_time = time.time()

                if hasattr(sys, 'getallocatedblocks'):
                    memory_before = sys.getallocatedblocks()

                result = FL_ca3(A, G, favorite)

                if hasattr(sys, 'getallocatedblocks'):
                    memory_after = sys.getallocatedblocks()
                    memory_used = (memory_after - memory_before) * 1024
                else:
                    if G == 2:
                        total = sum(A)
                        target = total // 2
                        memory_used = (len(A) + 1) * (target + 1) * 8
                    else:
                        memory_used = len(A) * G * 16

                end_time = time.time()
                execution_time = end_time - start_time

                results[size][G] = {
                    'time': execution_time,
                    'memory': memory_used,
                    'result': result
                }
            except Exception as e:
                print(f"Error with size={size}, G={G}: {e}")
                results[size][G] = {'time': 0, 'memory': 0, 'result': None}
    df = pd.DataFrame(results)
    df.to_csv("main_assignment.csv")
    return results


def run_extra_credit_experiments():
    """Run experiments for extra credit"""
    print("=== RUNNING EXTRA CREDIT EXPERIMENTS ===")

    sizes = list(range(1, 129))  # 1 to 128
    G_values = list(range(1, 11))  # 1 to 10

    results = {}

    for size in sizes:
        if size % 16 == 0:
            print(f"Testing size: {size}")

        results[size] = {}
        A = [random.randint(1, 50) for _ in range(size)]

        for G in G_values:
            if G > size:
                continue

            try:
                start_time = time.time()

                if hasattr(sys, 'getallocatedblocks'):
                    memory_before = sys.getallocatedblocks()

                result = FL_ec_ca3(A, G)

                if hasattr(sys, 'getallocatedblocks'):
                    memory_after = sys.getallocatedblocks()
                    memory_used = (memory_after - memory_before) * 1024
                else:
                    memory_used = size * G * 16

                end_time = time.time()
                execution_time = end_time - start_time

                results[size][G] = {
                    'time': execution_time,
                    'memory': memory_used,
                    'result': result
                }
            except Exception as e:
                print(f"Error with size={size}, G={G}: {e}")
                results[size][G] = {'time': 0, 'memory': 0, 'result': None}
    df=pd.DataFrame(results)
    df.to_csv("extra_credit.csv")
    return results


import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec
import seaborn as sns


if __name__ == "__main__":
    # Run experiments
    print("STARTING EXPERIMENTS...")

    # Run main assignment experiments
    main_results = run_main_experiments()

    # Run extra credit experiments
    ec_results = run_extra_credit_experiments()

    # Create comprehensive plots


    print("EXPERIMENTS AND PLOTTING COMPLETED!")



if __name__ == "__main__":
    # Run experiments directly without test examples
    print("################# STARTING EXPERIMENTS ##################")

    main_results = run_main_experiments()
    # ec_results = run_extra_credit_experiments()

    # plot_comprehensive_results(main_results, ec_results)

    print("################ EXPERIMENTS COMPLETED! ################")