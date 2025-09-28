# Full Name: Prashanna Raj Pandit
# Coding Assignment 3: Optimized Card Distribution Problem Using Dynamic Programming
# Implemented main assignment and Extra Credit assignment

import random
import time
import tracemalloc
import csv
import pandas as pd
import io
from itertools import combinations

sizes = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]  # Deck size


def subset_sum_dp(nums, target, indices=None):
    # Dynamic programming to find subset sum closest to target <= target
    if indices is None:
        indices = list(range(len(nums)))
    n = len(nums)
    total = sum(nums)
    target = min(target, total)
    # DP table: dp[i][j] = True if sum j can be formed using first i items
    dp = [[False for _ in range(target + 1)] for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = True
    # Fill DP table
    for i in range(1, n + 1):
        for j in range(1, target + 1):
            if nums[i - 1] > j:
                dp[i][j] = dp[i - 1][j]
            else:
                dp[i][j] = dp[i - 1][j] or dp[i - 1][j - nums[i - 1]]

    # Find maximum achievable sum <= target
    max_achievable = 0
    for j in range(target, -1, -1):
        if dp[n][j]:
            max_achievable = j
            break

    # Reconstruct the subset
    subset = []
    i, j = n, max_achievable
    while i > 0 and j > 0:
        if dp[i - 1][j]:
            i -= 1
        else:
            subset.append(indices[i - 1])
            j -= nums[i - 1]
            i -= 1
    return max_achievable, sorted(subset)


def discard_cards_to_value(A, cards, target_value):
    # Discard cards to reduce sum to target_value or below
    current_sum = sum(A[i - 1] for i in cards)
    excluded = []
    while current_sum > target_value and cards:
        # Remove the smallest card greater than 0
        min_card = min(((A[i - 1], i) for i in cards if A[i - 1] > 0), default=None)
        if not min_card:
            break
        cards.remove(min_card[1])
        excluded.append(min_card[1])
        current_sum -= min_card[0]
    return cards, excluded


def PP_ca3(A, G, favorite):  # Function for the main assignment where A= list of cards, G= list of grandchild
    grandchildren = ['melanie', 'selena', 'camila']
    favorite = favorite.lower()
    if favorite not in grandchildren:
        favorite = 'melanie'

    print(
        f"\n>>Grandma Rosa has a deck of {len(A)} cards and wants to distribute it to {G} grandchild{'ren' if G > 1 else ''}.")
    print(f">> When she passed, her favorite grandchild was {favorite.capitalize()}.\n")

    if G == 1:
        return handle_one_grandchild(A, favorite, grandchildren)
    elif G == 2:
        return handle_two_grandchildren(A, favorite, grandchildren)
    elif G == 3:
        return handle_three_grandchildren(A, favorite, grandchildren)
    else:
        print(">> Invalid number of grandchildren.")
        return {'assignments': {}, 'excluded_cards': [], 'scenario': 'invalid'}


def handle_one_grandchild(A, favorite, grandchildren):
    # G=1: Assign all cards to the favorite.
    assignments = {child: {'cards': [], 'value': 0} for child in grandchildren}
    assignments[favorite]['cards'] = list(range(1, len(A) + 1))
    assignments[favorite]['value'] = sum(A)
    print(
        f">> {favorite.capitalize()} would get all cards {assignments[favorite]['cards']} with a total value of ${assignments[favorite]['value']}")
    print(">> No cards were excluded")

    return {'assignments': assignments, 'excluded_cards': [], 'scenario': '1_grandchild'}


def handle_two_grandchildren(A, favorite, grandchildren):
    # G=2: Handle both scenarios with and without favorite.
    if len(A) < 2:
        print(">> No distribution is possible (A < G)")
        return {'assignments': {}, 'excluded_cards': [], 'scenario': '2_invalid'}

    other_child = 'selena' if favorite != 'selena' else 'camila'

    print(">> Scenario 1 -- With favourite child")
    result1 = handle_two_with_favorite(A, favorite, other_child, grandchildren)

    print("\n>> Scenario 2 -- Without favorite child")
    second_favorite = 'selena'
    other = 'camila'
    result2 = handle_two_without_favorite(A, second_favorite, other, grandchildren)

    return result1


def handle_two_with_favorite(A, favorite, other, grandchildren):
    # Favorite gets higher value than other using DP subset sum.
    total_value = sum(A)
    n = len(A)
    target = total_value // 2
    # Find best split for 'other'
    best_other_sum, other_indices = subset_sum_dp(A, target)
    favorite_cards = [i + 1 for i in range(n) if i not in other_indices]
    other_cards = [i + 1 for i in other_indices]
    favorite_value = sum(A[i - 1] for i in favorite_cards)
    other_value = best_other_sum

    excluded_cards = []
    # Enforce favorite > other by discarding if needed
    if favorite_value <= other_value:
        target_other = favorite_value - 1 if favorite_value > 0 else 0
        other_cards, excluded = discard_cards_to_value(A, other_cards, target_other)
        excluded_cards.extend(excluded)
        other_value = sum(A[i - 1] for i in other_cards)

    assignments = {
        favorite: {'cards': favorite_cards, 'value': favorite_value},
        other: {'cards': other_cards, 'value': other_value},
        [child for child in grandchildren if child not in [favorite, other]][0]: {'cards': [], 'value': 0}
    }

    print(f">> If the deck were being distributed to {favorite.capitalize()} and {other.capitalize()}, then")
    for child in grandchildren[:2]:
        card_info = assignments[child]
        print(
            f">> {child.capitalize()} would get cards {card_info['cards']} with a total value of ${card_info['value']}")
    if excluded_cards:
        print(f">> Card{'s' if len(excluded_cards) > 1 else ''} excluded: {excluded_cards}")
    else:
        print(">> No cards were excluded")

    return {'assignments': assignments, 'excluded_cards': excluded_cards, 'scenario': '2_with_favorite'}


def handle_two_without_favorite(A, child1, child2, grandchildren):
    # Equal distribution between two children using DP subset sum.
    total_value = sum(A)
    n = len(A)
    target = total_value // 2

    best_sum, child1_indices = subset_sum_dp(A, target)
    child1_cards = [i + 1 for i in child1_indices]
    child2_cards = [i + 1 for i in range(n) if i not in child1_indices]
    child1_value = best_sum
    child2_value = total_value - best_sum

    excluded_cards = []
    target_value = min(child1_value, child2_value)
    if child1_value > target_value:
        child1_cards, excluded = discard_cards_to_value(A, child1_cards, target_value)
        child1_value = target_value
        excluded_cards.extend(excluded)
    if child2_value > target_value:
        child2_cards, excluded = discard_cards_to_value(A, child2_cards, target_value)
        child2_value = target_value
        excluded_cards.extend(excluded)

    assignments = {
        child1: {'cards': child1_cards, 'value': child1_value},
        child2: {'cards': child2_cards, 'value': child2_value},
        [child for child in grandchildren if child not in [child1, child2]][0]: {'cards': [], 'value': 0}
    }

    print(f">> If the deck were being distributed to {child1.capitalize()} and {child2.capitalize()}, then")
    for child in grandchildren[1:]:
        card_info = assignments[child]
        print(
            f">> {child.capitalize()} would get cards {card_info['cards']} with a total value of ${card_info['value']}")
    if excluded_cards:
        print(f">> Card{'s' if len(excluded_cards) > 1 else ''} excluded: {excluded_cards}")
    else:
        print(">> No cards were excluded")

    return {'assignments': assignments, 'excluded_cards': excluded_cards, 'scenario': '2_without_favorite'}


def handle_three_grandchildren(A, favorite, grandchildren):
    # G=3: Distribute to all, favorite highest, second favorite next.
    total_value = sum(A)
    n = len(A)
    target = total_value // 3
    # Step 1: Find first group
    sum1, subset1 = subset_sum_dp(A, target)
    remaining = [i for i in range(n) if i not in subset1]

    # Step 2: Find second group from remaining
    rem_vals = [A[i] for i in remaining]
    target2 = sum(rem_vals) // 2 if rem_vals else 0
    sum2, subset2 = subset_sum_dp(rem_vals, target2, remaining)

    # Remaining = third group
    subset3 = [i for i in remaining if i not in subset2]
    sum3 = sum(A[i] for i in subset3)

    groups = [(sum1, [i + 1 for i in subset1]), (sum2, [i + 1 for i in subset2]), (sum3, [i + 1 for i in subset3])]
    groups.sort(key=lambda x: x[0], reverse=True)

    # Assign groups to grandchildren in order
    second_favorite = 'selena' if favorite != 'selena' else 'camila'
    third = [child for child in grandchildren if child not in [favorite, second_favorite]][0]

    assignments = {
        favorite: {'cards': groups[0][1], 'value': groups[0][0]},
        second_favorite: {'cards': groups[1][1], 'value': groups[1][0]},
        third: {'cards': groups[2][1], 'value': groups[2][0]}
    }

    # Enforce fairness (favorite > second > third) with discards
    excluded_cards = []
    # Ensure Melanie > Selena
    if assignments[favorite]['value'] <= assignments[second_favorite]['value']:
        target_value = assignments[favorite]['value'] - 1 if assignments[favorite]['value'] > 0 else 0
        assignments[second_favorite]['cards'], excluded = discard_cards_to_value(A,
                                                                                 assignments[second_favorite]['cards'],
                                                                                 target_value)
        excluded_cards.extend(excluded)
        assignments[second_favorite]['value'] = sum(A[i - 1] for i in assignments[second_favorite]['cards'])
    # Ensure Selena > Camila
    if assignments[second_favorite]['value'] <= assignments[third]['value']:
        target_value = assignments[second_favorite]['value'] - 1 if assignments[second_favorite]['value'] > 0 else 0
        assignments[third]['cards'], excluded = discard_cards_to_value(A, assignments[third]['cards'], target_value)
        excluded_cards.extend(excluded)
        assignments[third]['value'] = sum(A[i - 1] for i in assignments[third]['cards'])

    for child in grandchildren:
        card_info = assignments[child]
        print(
            f">> {child.capitalize()} would get cards {card_info['cards']} with a total value of ${card_info['value']}")
    if excluded_cards:
        print(f">> Card{'s' if len(excluded_cards) > 1 else ''} excluded: {excluded_cards}")
    else:
        print(">> No cards were excluded")

    return {'assignments': assignments, 'excluded_cards': excluded_cards, 'scenario': '3_grandchildren'}


def PP_ec_ca3(A, G):  # Extra credit: Distribute cards equally to G grandchildren using DP
    n = len(A)
    total_sum = sum(A)
    print(f"\n>> Extra Credit: Distributing {n} cards to {G} grandchildren equally.")

    if G > n:
        print(f">> Not enough cards ({n}) for {G} grandchildren. Cannot distribute equally (G>n)")

    if G == 1:
        cards_str = ", ".join(f"{i + 1}" for i in range(n)) if n else "0 cards"
        print(f">> Grandchild 1 would get {cards_str} with a total value of ${total_sum}")
        print(">> No cards were excluded")
        return True

    # Binary search for max achievable equal sum
    def can_distribute(target, remaining_indices, g_left):
        if g_left == 0:
            return True, []
        if not remaining_indices:
            return False, []

        sum_found, subset = subset_sum_dp([A[i] for i in remaining_indices], target, remaining_indices)
        if sum_found != target:
            return False, []

        new_remaining = [i for i in remaining_indices if i not in subset]
        success, subsets = can_distribute(target, new_remaining, g_left - 1)
        if success:
            return True, [subset] + subsets
        return False, []

    low, high = 0, total_sum // G
    best_target = 0
    best_subsets = []
    while low <= high:
        mid = (low + high) // 2
        success, subsets = can_distribute(mid, list(range(n)), G)
        if success:
            best_target = mid
            best_subsets = subsets
            low = mid + 1
        else:
            high = mid - 1

    # Try discarding if no exact equal partition found
    discarded = []
    if not best_subsets:
        min_discard = n + 1
        best_discarded = []
        best_subsets = []
        for d in range(n - G + 1):
            for disc_comb in combinations(range(n), d):
                rem_indices = [i for i in range(n) if i not in disc_comb]
                rem_vals = [A[i] for i in rem_indices]
                rem_total = sum(rem_vals)
                target = rem_total // G
                success, subsets = can_distribute(target, rem_indices, G)
                if success and d < min_discard:
                    min_discard = d
                    best_discarded = list(disc_comb)
                    best_subsets = subsets
                    if min_discard == 0:
                        break
        discarded = best_discarded

    # Output results
    flag = 0
    for gi in range(G):
        cards = best_subsets[gi] if best_subsets else []
        cards_str = ", ".join(f"{i + 1}" for i in cards) if cards else "0 cards"
        val = sum(A[i] for i in cards)
        if val == 0:
            flag = 1
        else:
            print(f">> Grandchild {gi + 1} would get {cards_str} with a total value of ${val}")
    if flag == 1:
        print("No equal distribution possible. All the cards were discarded.")
        return True
    if discarded:
        disc_str = ", ".join(f"C{i + 1}" for i in sorted(discarded))
        print(f">> Card{'s' if len(discarded) > 1 else ''} excluded: {disc_str}")
    else:
        print(">> No cards were excluded")

    return True


def main_experiments():  # Run experiment for the main assignment
    Gs = [1, 2, 3]
    results = []

    print("\n ######### Main Assignment Experiments ############\n")
    for size in sizes:
        A = [random.randint(1, 50) for _ in range(size)]
        for g in Gs:
            if size < g:
                continue
            tracemalloc.start()
            start = time.perf_counter()
            PP_ca3(A, g, 'melanie')
            elapsed = time.perf_counter() - start
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            results.append((size, g, elapsed, peak / 1024))

    # Save results to CSV
    result_csv = io.StringIO()
    writer = csv.writer(result_csv)
    writer.writerow(['n', 'G', 'time_s', 'memory_kb'])
    writer.writerows(results)
    result_csv.seek(0)
    return pd.read_csv(result_csv)


def extra_credit_experiments():
    """Run extra credit experiments."""
    Gs = list(range(1, 11))
    results = []

    print("\n############# Extra Credit Experiments ###############")
    for size in sizes:
        A = [random.randint(1, 50) for _ in range(size)]
        for g in Gs:
            if g > size:
                continue
            tracemalloc.start()
            start = time.perf_counter()
            PP_ec_ca3(A, g)
            elapsed = time.perf_counter() - start
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            results.append((size, g, elapsed, peak / 1024))

    # Save results to CSV
    result_csv = io.StringIO()
    writer = csv.writer(result_csv)
    writer.writerow(['n', 'G', 'time_s', 'memory_kb'])
    writer.writerows(results)
    result_csv.seek(0)
    df = pd.read_csv(result_csv)
    df.to_csv('ec_experiment_data.csv', index=False)


if __name__ == "__main__":
    # call main and extra credit function
    main_experiments()
    extra_credit_experiments()
