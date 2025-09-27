import random
import time
import matplotlib.pyplot as plt
import numpy as np
from typing import List, Tuple, Dict, Set
import pandas as pd
import sys
from functools import lru_cache


def FL_ca3(A: List[int], G: int, favorite: str) -> Dict:
    """
    Main function for Grandma Rosa's card distribution problem
    Uses proper Dynamic Programming for all partitioning
    """
    grandchildren = ['melanie', 'selena', 'camila']

    print(f">> Grandma Rosa has a deck of {len(A)} cards and wants to distribute it to {G} grandchildren.")
    print(f">> When she passed, her favorite grandchild was {favorite}.")

    if G == 1:
        return handle_one_grandchild(A, favorite, grandchildren)
    elif G == 2:
        return handle_two_grandchildren_dp(A, favorite, grandchildren)
    elif G == 3:
        return handle_three_grandchildren_dp(A, favorite, grandchildren)


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


def handle_two_grandchildren_dp(A: List[int], favorite: str, grandchildren: List[str]) -> Dict:
    """G=2: Proper DP for 2-partition problem"""
    if len(A) < 2:
        print(">> No distribution is possible (A < G)")
        return {'assignments': {}, 'excluded_cards': [], 'scenario': '2_invalid'}

    other_child = [child for child in grandchildren if child != favorite][0]

    print(">> Scenario 1 -- With favourite child")
    result1 = handle_two_with_favorite_dp(A, favorite, other_child, grandchildren)

    print("\n>> Scenario 2 -- Without favorite child")
    second_favorite = 'selena'
    other = 'camila'
    result2 = handle_two_without_favorite_dp(A, second_favorite, other, grandchildren)

    return result1


def handle_two_with_favorite_dp(A: List[int], favorite: str, other: str, grandchildren: List[str]) -> Dict:
    """DP for 2-partition where favorite gets higher value"""
    total = sum(A)
    n = len(A)

    # Proper DP table for subset sum
    target = total // 2
    dp = [[False] * (target + 1) for _ in range(n + 1)]
    dp[0][0] = True

    # Fill DP table
    for i in range(1, n + 1):
        for j in range(target + 1):
            if A[i - 1] <= j:
                dp[i][j] = dp[i - 1][j] or dp[i - 1][j - A[i - 1]]
            else:
                dp[i][j] = dp[i - 1][j]

    # Find best partition where favorite gets more
    best_diff = float('inf')
    best_j = -1

    for j in range(target, -1, -1):
        if dp[n][j]:
            favorite_value = total - j
            diff = favorite_value - j
            if diff >= 0 and diff < best_diff:  # Favorite should have more or equal
                best_diff = diff
                best_j = j

    if best_j == -1:  # No valid partition found
        return handle_two_without_favorite_dp(A, favorite, other, grandchildren)

    # Reconstruct favorite's subset (the larger subset)
    favorite_indices = set()
    j = best_j
    for i in range(n, 0, -1):
        if not dp[i - 1][j]:
            favorite_indices.add(i - 1)
            j -= A[i - 1]

    other_indices = set(range(n)) - favorite_indices

    favorite_cards = [i + 1 for i in favorite_indices]
    other_cards = [i + 1 for i in other_indices]
    favorite_value = total - best_j
    other_value = best_j

    # Ensure favorite has strictly more by discarding if needed
    excluded_cards = []
    if favorite_value <= other_value:
        # Discard from other to make favorite have more
        other_cards, excluded = discard_cards_dp(A, other_cards, favorite_value - 1)
        excluded_cards.extend(excluded)
        other_value = favorite_value - 1

    assignments = create_assignments(favorite, other, favorite_cards, other_cards,
                                     favorite_value, other_value, grandchildren)

    print_assignment_result(favorite, other, assignments, excluded_cards)
    return {'assignments': assignments, 'excluded_cards': excluded_cards, 'scenario': '2_with_favorite'}


def handle_two_without_favorite_dp(A: List[int], child1: str, child2: str, grandchildren: List[str]) -> Dict:
    """DP for equal 2-partition"""
    total = sum(A)
    n = len(A)

    # DP for equal partition
    target = total // 2
    dp = [[False] * (target + 1) for _ in range(n + 1)]
    dp[0][0] = True

    for i in range(1, n + 1):
        for j in range(target + 1):
            if A[i - 1] <= j:
                dp[i][j] = dp[i - 1][j] or dp[i - 1][j - A[i - 1]]
            else:
                dp[i][j] = dp[i - 1][j]

    # Find closest to equal partition
    best_j = 0
    min_diff = float('inf')

    for j in range(target, -1, -1):
        if dp[n][j]:
            diff = abs(2 * j - total)
            if diff < min_diff:
                min_diff = diff
                best_j = j

    # Reconstruct partition
    child1_indices = set()
    j = best_j
    for i in range(n, 0, -1):
        if not dp[i - 1][j]:
            child1_indices.add(i - 1)
            j -= A[i - 1]

    child2_indices = set(range(n)) - child1_indices

    child1_cards = [i + 1 for i in child1_indices]
    child2_cards = [i + 1 for i in child2_indices]
    child1_value = best_j
    child2_value = total - best_j

    # Equalize by discarding
    excluded_cards = []
    target_value = min(child1_value, child2_value)

    if child1_value > target_value:
        child1_cards, excluded = discard_cards_dp(A, child1_cards, target_value)
        excluded_cards.extend(excluded)

    if child2_value > target_value:
        child2_cards, excluded = discard_cards_dp(A, child2_cards, target_value)
        excluded_cards.extend(excluded)

    assignments = create_assignments(child1, child2, child1_cards, child2_cards,
                                     target_value, target_value, grandchildren)

    print_assignment_result(child1, child2, assignments, excluded_cards)
    return {'assignments': assignments, 'excluded_cards': excluded_cards, 'scenario': '2_without_favorite'}


def handle_three_grandchildren_dp(A: List[int], favorite: str, grandchildren: List[str]) -> Dict:
    """Proper DP for 3-partition problem with memoization"""
    total = sum(A)
    n = len(A)

    if n < 3:
        print(">> Not enough cards for 3 grandchildren")
        return balanced_three_split_fallback(A, favorite, grandchildren)

    # Use DP with memoization for 3-partition
    target = total // 3
    memo = {}

    def dp_3partition(idx, sums):
        """Memoized DP function for 3-partition"""
        if idx == n:
            return sums[0] == target and sums[1] == target and sums[2] == target

        key = (idx, tuple(sorted(sums)))
        if key in memo:
            return memo[key]

        # Try assigning current card to each partition
        for i in range(3):
            if sums[i] + A[idx] <= target:
                new_sums = list(sums)
                new_sums[i] += A[idx]
                if dp_3partition(idx + 1, new_sums):
                    memo[key] = True
                    return True

        memo[key] = False
        return False

    # Check if exact 3-partition exists
    if total % 3 == 0 and dp_3partition(0, [0, 0, 0]):
        # Reconstruct the partition
        sums = [0, 0, 0]
        partitions = [[] for _ in range(3)]

        for idx in range(n):
            for i in range(3):
                if sums[i] + A[idx] <= target:
                    new_sums = sums.copy()
                    new_sums[i] += A[idx]
                    if dp_3partition(idx + 1, new_sums):
                        partitions[i].append(idx + 1)
                        sums[i] += A[idx]
                        break

        # Sort partitions by value descending
        values = [sum(A[i - 1] for i in part) for part in partitions]
        sorted_parts = sorted(zip(partitions, values, ['melanie', 'selena', 'camila']),
                              key=lambda x: x[1], reverse=True)

        assignments = {}
        for i, (cards, value, child) in enumerate(sorted_parts):
            assignments[child] = {'cards': cards, 'value': value}

        # Ensure favorite gets highest
        if favorite != sorted_parts[0][2]:
            # Swap to make favorite have highest
            fav_value = assignments[favorite]['value']
            highest_child = sorted_parts[0][2]
            highest_value = assignments[highest_child]['value']

            assignments[favorite]['value'] = highest_value
            assignments[highest_child]['value'] = fav_value
            assignments[favorite]['cards'], assignments[highest_child]['cards'] = \
                assignments[highest_child]['cards'], assignments[favorite]['cards']

        print_three_assignment_result(assignments, grandchildren, [])
        return {'assignments': assignments, 'excluded_cards': [], 'scenario': '3_grandchildren'}

    else:
        # Fallback to approximate 3-partition with DP
        return approximate_three_partition_dp(A, favorite, grandchildren)


def approximate_three_partition_dp(A: List[int], favorite: str, grandchildren: List[str]) -> Dict:
    """DP approach for approximate 3-partition when exact partition doesn't exist"""
    n = len(A)
    total = sum(A)
    target = total // 3

    # DP to minimize maximum partition sum
    dp = [[[False] * (target + 1) for _ in range(target + 1)] for _ in range(n + 1)]
    dp[0][0][0] = True

    for i in range(1, n + 1):
        for s1 in range(target + 1):
            for s2 in range(target + 1):
                if dp[i - 1][s1][s2]:
                    # Assign to first partition
                    if s1 + A[i - 1] <= target:
                        dp[i][s1 + A[i - 1]][s2] = True
                    # Assign to second partition
                    if s2 + A[i - 1] <= target:
                        dp[i][s1][s2 + A[i - 1]] = True
                    # Assign to third partition
                    dp[i][s1][s2] = True

    # Find best achievable sums
    best_s1, best_s2 = 0, 0
    min_max_sum = float('inf')

    for s1 in range(target + 1):
        for s2 in range(target + 1):
            if dp[n][s1][s2]:
                s3 = total - s1 - s2
                max_sum = max(s1, s2, s3)
                if max_sum < min_max_sum:
                    min_max_sum = max_sum
                    best_s1, best_s2 = s1, s2

    # Reconstruct partitions
    s1, s2 = best_s1, best_s2
    partitions = [[] for _ in range(3)]

    for i in range(n, 0, -1):
        if s1 >= A[i - 1] and dp[i - 1][s1 - A[i - 1]][s2]:
            partitions[0].append(i)
            s1 -= A[i - 1]
        elif s2 >= A[i - 1] and dp[i - 1][s1][s2 - A[i - 1]]:
            partitions[1].append(i)
            s2 -= A[i - 1]
        else:
            partitions[2].append(i)

    # Assign to grandchildren with favorite getting highest
    values = [sum(A[i - 1] for i in part) for part in partitions]
    sorted_indices = sorted(range(3), key=lambda i: values[i], reverse=True)

    assignments = {}
    child_order = ['melanie', 'selena', 'camila']

    # Ensure favorite gets highest
    if favorite != child_order[sorted_indices[0]]:
        # Find favorite's position and swap
        fav_idx = child_order.index(favorite)
        for i in range(3):
            if sorted_indices[i] == fav_idx:
                sorted_indices[0], sorted_indices[i] = sorted_indices[i], sorted_indices[0]
                break

    for i, idx in enumerate(sorted_indices):
        assignments[child_order[i]] = {
            'cards': partitions[idx],
            'value': values[idx]
        }

    print_three_assignment_result(assignments, grandchildren, [])
    return {'assignments': assignments, 'excluded_cards': [], 'scenario': '3_grandchildren'}


def balanced_three_split_fallback(A: List[int], favorite: str, grandchildren: List[str]) -> Dict:
    """Fallback when DP fails for small inputs"""
    n = len(A)
    indices = sorted(range(n), key=lambda i: A[i], reverse=True)

    sums = [0, 0, 0]
    partitions = [[] for _ in range(3)]

    for idx in indices:
        min_idx = np.argmin(sums)
        partitions[min_idx].append(idx + 1)
        sums[min_idx] += A[idx]

    # Assign with favorite getting highest
    values = [sum(A[i - 1] for i in part) for part in partitions]
    sorted_indices = sorted(range(3), key=lambda i: values[i], reverse=True)

    assignments = {}
    child_order = ['melanie', 'selena', 'camila']

    if favorite != child_order[sorted_indices[0]]:
        fav_idx = child_order.index(favorite)
        for i in range(3):
            if sorted_indices[i] == fav_idx:
                sorted_indices[0], sorted_indices[i] = sorted_indices[i], sorted_indices[0]
                break

    for i, idx in enumerate(sorted_indices):
        assignments[child_order[i]] = {
            'cards': partitions[idx],
            'value': values[idx]
        }

    print_three_assignment_result(assignments, grandchildren, [])
    return {'assignments': assignments, 'excluded_cards': [], 'scenario': '3_grandchildren'}


def discard_cards_dp(A: List[int], cards: List[int], target_value: int) -> Tuple[List[int], List[int]]:
    """DP approach for discarding cards to reach target value"""
    current_value = sum(A[i - 1] for i in cards)

    if current_value <= target_value:
        return cards, []

    # Convert to indices (0-based)
    card_indices = [i - 1 for i in cards]
    card_values = [A[i] for i in card_indices]

    # DP to find subset closest to but not exceeding target_value
    n = len(card_values)
    dp = [[0] * (target_value + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for j in range(target_value + 1):
            if card_values[i - 1] <= j:
                dp[i][j] = max(dp[i - 1][j], dp[i - 1][j - card_values[i - 1]] + card_values[i - 1])
            else:
                dp[i][j] = dp[i - 1][j]

    # Find which cards to keep
    j = target_value
    keep_indices = []
    for i in range(n, 0, -1):
        if dp[i][j] != dp[i - 1][j]:
            keep_indices.append(card_indices[i - 1])
            j -= card_values[i - 1]

    kept_cards = [i + 1 for i in keep_indices]
    discarded_cards = [i for i in cards if i - 1 not in keep_indices]

    return kept_cards, discarded_cards


def create_assignments(child1: str, child2: str, cards1: List[int], cards2: List[int],
                       value1: int, value2: int, grandchildren: List[str]) -> Dict:
    """Helper to create assignments dictionary"""
    third_child = [child for child in grandchildren if child not in [child1, child2]][0]

    return {
        child1: {'cards': cards1, 'value': value1},
        child2: {'cards': cards2, 'value': value2},
        third_child: {'cards': [], 'value': 0}
    }


def print_assignment_result(child1: str, child2: str, assignments: Dict, excluded_cards: List[int]):
    """Helper to print assignment results"""
    print(f">> If the deck were being distributed to {child1} and {child2}, then")
    for child in assignments:
        card_info = assignments[child]
        print(
            f">> {child.capitalize()} would get cards {card_info['cards']} with a total value of ${card_info['value']}")

    if excluded_cards:
        print(f">> Cards excluded: {excluded_cards}")
    else:
        print(">> No cards were excluded")


def print_three_assignment_result(assignments: Dict, grandchildren: List[str], excluded_cards: List[int]):
    """Helper to print 3-grandchild assignment results"""
    print(">> If the deck were being distributed to all three grandchildren, then")
    for child in grandchildren:
        card_info = assignments[child]
        print(
            f">> {child.capitalize()} would get cards {card_info['cards']} with a total value of ${card_info['value']}")

    if excluded_cards:
        print(f">> Cards excluded: {excluded_cards}")
    else:
        print(">> No cards were excluded")


# Extra credit function with proper DP
def FL_ec_ca3(A: List[int], G: int) -> Dict:
    """Extra credit: Proper DP for multi-way equal partitioning"""
    if G == 1:
        assignments = {'Grandchild 1': {'cards': list(range(1, len(A) + 1)), 'value': sum(A)}}
        print(f">> Grandchild 1 would get cards {list(range(1, len(A) + 1))} with a total value of ${sum(A)}")
        return {'assignments': assignments, 'excluded_cards': [], 'scenario': '1_grandchild'}

    n = len(A)
    total = sum(A)
    target = total // G

    # Use DP for multi-way partitioning
    memo = {}

    def multiway_dp(idx, sums):
        if idx == n:
            return all(s == target for s in sums)

        key = (idx, tuple(sorted(sums)))
        if key in memo:
            return memo[key]

        for i in range(G):
            if sums[i] + A[idx] <= target:
                new_sums = list(sums)
                new_sums[i] += A[idx]
                if multiway_dp(idx + 1, new_sums):
                    memo[key] = True
                    return True

        memo[key] = False
        return False

    # Try to find exact partition
    if total % G == 0 and multiway_dp(0, [0] * G):
        # Reconstruct partitions
        sums = [0] * G
        partitions = [[] for _ in range(G)]

        for idx in range(n):
            for i in range(G):
                if sums[i] + A[idx] <= target:
                    new_sums = sums.copy()
                    new_sums[i] += A[idx]
                    if multiway_dp(idx + 1, new_sums):
                        partitions[i].append(idx + 1)
                        sums[i] += A[idx]
                        break

        assignments = {}
        for i in range(G):
            value = sum(A[j - 1] for j in partitions[i])
            assignments[f'Grandchild {i + 1}'] = {
                'cards': partitions[i],
                'value': value
            }

        print_extra_credit_result(assignments, [])
        return {'assignments': assignments, 'excluded_cards': [], 'scenario': f'{G}_grandchildren'}

    else:
        # Fallback to greedy with discarding
        return greedy_multiway_partition(A, G)


def greedy_multiway_partition(A: List[int], G: int) -> Dict:
    """Greedy fallback for multi-way partitioning"""
    n = len(A)
    indices = sorted(range(n), key=lambda i: A[i], reverse=True)

    sums = [0] * G
    partitions = [[] for _ in range(G)]

    for idx in indices:
        min_idx = np.argmin(sums)
        partitions[min_idx].append(idx + 1)
        sums[min_idx] += A[idx]

    # Equalize by discarding to the minimum value
    min_value = min(sums)
    excluded_cards = []
    equalized_partitions = []

    for part in partitions:
        current_value = sum(A[i - 1] for i in part)
        if current_value > min_value:
            kept, discarded = discard_cards_dp(A, part, min_value)
            equalized_partitions.append(kept)
            excluded_cards.extend(discarded)
        else:
            equalized_partitions.append(part)

    assignments = {}
    for i in range(G):
        value = sum(A[j - 1] for j in equalized_partitions[i])
        assignments[f'Grandchild {i + 1}'] = {
            'cards': equalized_partitions[i],
            'value': value
        }

    print_extra_credit_result(assignments, excluded_cards)
    return {'assignments': assignments, 'excluded_cards': excluded_cards, 'scenario': f'{G}_grandchildren'}


def print_extra_credit_result(assignments: Dict, excluded_cards: List[int]):
    """Helper to print extra credit results"""
    for grandchild, info in assignments.items():
        print(f">> {grandchild} would get cards {info['cards']} with a total value of ${info['value']}")

    if excluded_cards:
        print(f">> Cards excluded: {excluded_cards}")
    else:
        print(">> No cards were excluded")


# Experiment functions (same as before)
def run_main_experiments():
    """Run experiments for main assignment"""
    print("=== RUNNING MAIN ASSIGNMENT EXPERIMENTS ===")

    sizes = [1, 2, 4, 8, 16, 32, 64, 128]
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
                result = FL_ca3(A, G, favorite)
                end_time = time.time()

                results[size][G] = {
                    'time': end_time - start_time,
                    'memory': len(A) * G * 8,  # Estimate
                    'result': result
                }
            except Exception as e:
                print(f"Error with size={size}, G={G}: {e}")
                results[size][G] = {'time': 0, 'memory': 0, 'result': None}

    return results


def run_ec_experiments():
    """Run experiments for extra credit"""
    print("=== RUNNING EXTRA CREDIT EXPERIMENTS ===")

    sizes = [1, 2, 4, 8, 16, 32, 64]
    G_values = list(range(1, 6))

    results = {}

    for size in sizes:
        print(f"Testing array size: {size}")
        results[size] = {}
        A = [random.randint(1, 50) for _ in range(size)]

        for G in G_values:
            if G > size:
                continue
            try:
                start_time = time.time()
                result = FL_ec_ca3(A, G)
                end_time = time.time()

                results[size][G] = {
                    'time': end_time - start_time,
                    'memory': len(A) * G * 8,
                    'result': result
                }
            except Exception as e:
                print(f"Error with size={size}, G={G}: {e}")
                results[size][G] = {'time': 0, 'memory': 0, 'result': None}

    return results


if __name__ == "__main__":
    # Test the DP implementations
    print("################# TESTING DP IMPLEMENTATIONS ##################")

    A = [2, 1, 3, 1, 5, 2, 3, 4]

    print("\n=== TESTING 2-PARTITION DP ===")
    result2 = FL_ca3(A, 2, 'melanie')

    print("\n=== TESTING 3-PARTITION DP ===")
    result3 = FL_ca3(A, 3, 'melanie')

    print("\n=== TESTING EXTRA CREDIT DP ===")
    result_ec = FL_ec_ca3(A, 3)

    print("\n################# RUNNING EXPERIMENTS ##################")
    main_results = run_main_experiments()
    ec_results = run_ec_experiments()

    print("################ EXPERIMENTS COMPLETED! ################")