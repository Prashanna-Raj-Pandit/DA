# Name: Prashanna Raj Pandit
# Coding Assignment 1 - Policemen Catching Thieves
# Modifications 1 :policemen catch thieves in the same column
# Modification 3: set of three adjacent rookies catch a thief
# Modification 4: (Extra Credit) Policeman can catch a thief within the distanceK

import csv
import random
import time
import os
import numpy as np
import pandas as pd
from itertools import combinations

# Constants
K_Distance = [1, 2, 3, 4, 5, 6, 7]  # maximum allowed distance police can move
SAMPLE = 5  # Number of samples/grids to generate per configuration
BALANCED_WEIGHTS = [0.25, 0.25, 0.25, 0.25]  # Uniform distribution weights (all elements equally likely)
FIXED_GRID_DATASET_DIR = 'datasets/k_distance'
metrics_DIR = 'metrics'
grid_dimensions = np.arange(5, 21, 1)  # Range of grid dimensions from 5x5 up to 20x20
grid_dimensions = grid_dimensions.tolist()
trials = 2  # Number of trials to run for each main assignment configuration
fixed_dimension = 10  # Fixed grid dimension for K experiment

# Elements and biased weights
elements = ['P', 'T', 'R', 'X']  # P = Police, T = Thief, R = Rookie squad, X = Empty space
distribution = {
    "police": [0.7, 0.1, 0.1, 0.1],  # Heavily biased toward placing Police
    "empty": [0.1, 0.1, 0.1, 0.7],  # Mostly empty spaces
    "rookie": [0.1, 0.1, 0.7, 0.1],  # Mostly Rookies
    "balanced": [0.25, 0.25, 0.25, 0.25]  # Equal chance for all elements
}

metrics = {
    profile: {
        'dimension': [], 'g_exe_time': [], 'b_exe_time': [],
        'g_caught': [], 'b_caught': []
    }
    for profile in distribution.keys()
}

datasets = {
    'k_distance': {k: [] for k in K_Distance}
}


def create_datasets(dimensions, trials=3):
    global datasets, distribution

    if not os.path.exists('datasets'):
        os.makedirs('datasets')
    if not os.path.exists(FIXED_GRID_DATASET_DIR):
        os.makedirs(FIXED_GRID_DATASET_DIR)

    # Create datasets for each biased and dimension
    for dimension in dimensions:
        for biased in metrics.keys():
            datasets[f'{biased}_{dimension}'] = []
            for trial in range(trials):
                current_weights = distribution[biased]
                grid = [[random.choices(elements, weights=current_weights)[0] for _ in range(dimension)] for _ in
                        range(dimension)]
                K = dimension // 2  # Fixed K value for main experiments
                # K=1
                filename = f'datasets/{biased}_{dimension}_{trial}.txt'
                with open(filename, 'w') as f:
                    f.write(f"K: {K}\n")
                    for row in grid:
                        f.write(' '.join(row) + '\n')
                datasets[f'{biased}_{dimension}'].append((grid, K))


def fixed_dataset(datasets):
    # Extra Credit Experiment datasets (fixed dimension, varying K)
    for k in K_Distance:
        for s in range(SAMPLE):
            grid = [[random.choices(elements, weights=BALANCED_WEIGHTS)[0] for _ in range(fixed_dimension)] for _ in
                    range(fixed_dimension)]
            file = os.path.join(FIXED_GRID_DATASET_DIR, f'k_distance_{k}_sample{s}.txt')
            with open(file, 'w') as f:
                f.write(f"K: {k}\n")
                f.write('\n'.join(' '.join(row) for row in grid))
            datasets['k_distance'][k].append((grid, k))


def grid_display(grid):
    for r in grid:
        print(' '.join(r))
    print()


def implement_greedy_approach(M, K, dir):
    grid = [r.copy() for r in M]
    start_time = time.perf_counter()
    caught = 0
    logs = []
    rows, cols = len(grid), len(grid[0])
    # Process each column for police catching  in the same column
    for col in range(cols):
        # Collect all police and  in this column
        police_positions = [row_idx for row_idx in range(rows) if grid[row_idx][col] == 'P']
        thief_positions = [row_idx for row_idx in range(rows) if grid[row_idx][col] == 'T']

        # Sort positions
        police_positions.sort()
        thief_positions.sort()

        # Use two pointers to match police with
        p_idx = t_idx = 0
        while p_idx < len(police_positions) and t_idx < len(thief_positions):
            police_row = police_positions[p_idx]
            thief_row = thief_positions[t_idx]
            distance = abs(police_row - thief_row)

            if distance <= K:
                caught += 1
                grid[thief_row][col] = 'C'  # Mark as caught
                logs.append(f">>Thief at ({thief_row}, {col}) was caught by Police at ({police_row}, {col})")
                p_idx += 1
                t_idx += 1
            elif police_row < thief_row:
                p_idx += 1
            else:
                t_idx += 1

    # Process rookies catching  (3 rookies needed)
    caught = rookie_catch_greedy(caught, cols, dir, grid, logs, rows)

    return caught, time.perf_counter() - start_time, logs


def rookie_catch_greedy(caught, cols, dir, M, logs, rows):
    for i in range(rows):
        for j in range(cols):
            if M[i][j] == 'T':  # Only process  that haven't been caught
                nearby_rookies = []

                # Check all four directions for rookies
                for dx, dy in dir:
                    ni, nj = i + dx, j + dy
                    if (0 <= ni < rows and 0 <= nj < cols and
                            M[ni][nj] == 'R'):
                        nearby_rookies.append((ni, nj))

                # If at least 3 rookies are adjacent, catch the thief
                if len(nearby_rookies) >= 3:
                    caught += 1
                    M[i][j] = 'C'  # Mark thief as caught

                    # Use the first 3 rookies and mark them as used
                    used_rookies = nearby_rookies[:3]
                    for r_i, r_j in used_rookies:
                        M[r_i][r_j] = 'U'  # Mark rookie as used

                    logs.append(f">>Thief at ({i}, {j}) was caught by Rookies at {used_rookies}")
    return caught


def implement_brute_force_approach(matrix, dist, dir):
    t0 = time.perf_counter()
    board = [row.copy() for row in matrix]
    log_entries = []

    # --- Police vs  ---
    P_caught = 0
    n_rows, n_cols = len(board), len(board[0])
    for c in range(n_cols):
        P = [r for r in range(n_rows) if board[r][c] == 'P']
        robbers = [r for r in range(n_rows) if board[r][c] == 'T']
        matched_P, matched_ = set(), set()
        for cop in P:
            for thief in robbers:
                if abs(cop - thief) <= dist and cop not in matched_P and thief not in matched_:
                    P_caught += 1
                    matched_P.add(cop)
                    matched_.add(thief)
                    log_entries.append(f">>Thief at ({thief}, {c}) was caught by Police at ({cop}, {c})")
                    break

    # --- Rookie squads ---
    caught_by_rookies = rookie_catch_brute(board, dir, log_entries, n_cols, n_rows)

    total_caught = P_caught + caught_by_rookies
    elapsed = time.time() - t0
    return total_caught, elapsed, log_entries


def rookie_catch_brute(M, dir, log_entries, n_cols, n_rows):
    caught_by_rookies = 0
    thief_cells = [(r, c) for r in range(n_rows) for c in range(n_cols) if M[r][c] == 'T']
    for tr, tc in thief_cells:
        nearby_rookies = []
        for dr, dc in dir:
            nr, nc = tr + dr, tc + dc
            if 0 <= nr < n_rows and 0 <= nc < n_cols and M[nr][nc] == 'R':
                nearby_rookies.append((nr, nc))

        if len(nearby_rookies) >= 3:
            for triple in combinations(nearby_rookies, 3):
                if all(M[r][c] == 'R' for r, c in triple):
                    caught_by_rookies += 1
                    for r, c in triple:
                        M[r][c] = 'U'
                    log_entries.append(f">>Thief at ({tr}, {tc}) caught by Rookies at {triple}")
                    break
    return caught_by_rookies


def PP_ca1(M, K):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    g_count, g_time, g_log = implement_greedy_approach(M, K, directions)
    print("Greedy Solution:")
    for log in g_log:
        print(f">>{log}")
    print(f">>Total  Caught: {g_count}")

    b_count, b_time, b_log = implement_brute_force_approach(M, K, directions)
    print("Brute-force Solution:")
    for log in b_log:
        print(f">>{log}")
    print(f">>Total  Caught: {b_count}")
    return [(g_count, g_time), (b_count, b_time)]


def extra_credit_exp():
    """Extra Credit Experiment: with varying K values"""
    print("\n" + "#" * 70)
    print("\tExtra Credit Experiment: Varying K Values")
    print("#" * 70)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    if not os.path.exists(metrics_DIR):
        os.makedirs(metrics_DIR)

    csv_path = os.path.join(metrics_DIR, 'experiment3_metrics.csv')
    fixed_dataset(datasets)
    # Open CSV once and write header
    with open(csv_path, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'K', 'sample',
            'greedy_time', 'brute_time',
            'greedy_caught', 'brute_caught',
            'greedy_police', 'greedy_rookie',
            'brute_police', 'brute_rookie'
        ])

        for K in K_Distance:
            for sample, (grid, _) in enumerate(datasets['k_distance'][K]):
                if sample == 0:  # Printing only first sample
                    print(f"\n>>Processing 10x10 grid (K={K})")
                    grid_display(grid)

                # Run both approaches
                g_count, g_time, g_log = implement_greedy_approach([row[:] for row in grid], K, directions)
                b_count, b_time, b_log = implement_brute_force_approach([row[:] for row in grid], K, directions)
                # Count police vs rookie catches and extract details
                g_police_logs = [log for log in g_log if "Police" in log]
                g_rookie_logs = [log for log in g_log if "Rookies" in log]
                g_police = len(g_police_logs)
                g_rookie = len(g_rookie_logs)

                b_police_logs = [log for log in b_log if "Police" in log]
                b_rookie_logs = [log for log in b_log if "Rookies" in log]
                b_police = len(b_police_logs)
                b_rookie = len(b_rookie_logs)

                # Print detailed metrics for the first sample of each K value
                if sample == 0:
                    print(f"\n>> K = {K} - Greedy Approach Method:")
                    if g_police > 0:
                        print(f">> Police catches ({g_police} ):")
                        for log in g_police_logs:
                            # Extract and reformat the message
                            message = log.replace(">>Thief at (", "").replace(") was caught by Police at (",
                                                                              " catch Thief at (")
                            message = message.replace(")", "").replace(", ", ",")
                            parts = message.split(" catch Thief at ")
                            police_pos = parts[0].replace(",", ",")
                            thief_pos = parts[1].replace(",", ",")
                            print(f">> Police at ({thief_pos}) catch Thief at ({police_pos})")

                    if g_rookie > 0:
                        print(f">> Rookie squad catches ({g_rookie} ):")
                        for log in g_rookie_logs:
                            print(f">> {log}")

                    print(f"\n>> K = {K} - Brute Force Approach Method:")
                    if b_police > 0:
                        print(f">> Police catches ({b_police} ):")
                        for log in b_police_logs:
                            # Extract and reformat the message
                            message = log.replace(">>Thief at (", "").replace(") was caught by Police at (",
                                                                              " catch Thief at (")
                            message = message.replace(")", "").replace(", ", ",")
                            parts = message.split(" catch Thief at ")
                            police_pos = parts[0].replace(",", ",")
                            thief_pos = parts[1].replace(",", ",")
                            print(f">> Police at ({thief_pos}) catch Thief at ({police_pos})")

                    if b_rookie > 0:
                        print(f">> Rookie squad catches ({b_rookie} ):")
                        for log in b_rookie_logs:
                            print(f">> {log}")
                writer.writerow([
                    K, sample,
                    g_time, b_time,
                    g_count, b_count,
                    g_police, g_rookie,
                    b_police, b_rookie
                ])


def save_metrics(metrics_dict):
    # Convert the dictionary to a list of records
    records = []
    filename = os.path.join(metrics_DIR, "metrics.csv")
    for biased, data in metrics_dict.items():
        for i in range(len(data['dimension'])):
            records.append({
                'biased': biased,
                'dimension': data['dimension'][i],
                'g_exe_time': data['g_exe_time'][i],
                'b_exe_time': data['b_exe_time'][i],
                'g_caught': data['g_caught'][i],
                'b_caught': data['b_caught'][i]
            })

    # Create DataFrame and save to CSV
    df = pd.DataFrame(records)
    df.to_csv(filename, index=False)
    print(f"metrics saved to {filename}")

    # Also save separate files for each biased
    for biased in metrics_dict.keys():
        biased_df = df[df['biased'] == biased]
        path = os.path.join(metrics_DIR, f"metrics_{biased}.csv")
        biased_df.to_csv(path, index=False)


def main_assignment():
    for dimension in grid_dimensions:
        print(f"\n>>Running experiments for grid dimension {dimension}x{dimension}")
        for biased in metrics.keys():
            print(">>")
            if biased == "balanced":
                print(f">>Processing balanced grids.")
            else:
                print(f">>Processing {biased} biased.")
            g_exe_time = []
            b_exe_time = []
            greedy_counts = []
            brute_counts = []
            for idx, (grid, K) in enumerate(datasets[f'{biased}_{dimension}']):
                print(f"\nGrid {idx + 1} (biased: {biased}, dimension: {dimension}x{dimension}, K: {K}):")
                grid_display(grid)
                values = PP_ca1(grid, K)
                greedy_counts.append(values[0][0])
                g_exe_time.append(values[0][1])
                brute_counts.append(values[1][0])
                b_exe_time.append(values[1][1])

            metrics[biased]['dimension'].append(dimension)
            metrics[biased]['g_exe_time'].append(sum(g_exe_time) / len(g_exe_time))
            metrics[biased]['b_exe_time'].append(sum(b_exe_time) / len(b_exe_time))
            metrics[biased]['g_caught'].append(sum(greedy_counts) / len(greedy_counts))
            metrics[biased]['b_caught'].append(sum(brute_counts) / len(brute_counts))


def main():
    print(">>Welcome to the Policemen Catching  Program!")
    print("\n" + "#" * 70)
    print("\tMain Assignment: Modification,1,3, and 4 with Fixed K value")
    print("#" * 70)
    # Create all datasets
    create_datasets(grid_dimensions, trials=trials)
    # Run main experiments
    main_assignment()
    # Run K-distance experiment
    extra_credit_exp()
    save_metrics(metrics)


if __name__ == '__main__':
    main()
