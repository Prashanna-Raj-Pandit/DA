import random
import time
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations
from copy import deepcopy

# Constants
K_VALUES = [5, 6, 7, 8, 9, 10]
SAMPLE = 1
BALANCED_WEIGHTS = [0.25, 0.25, 0.25, 0.25]
FIXED_GRID_DATASET_DIR = 'datasets/k_distance'
RESULTS_DIR = 'results'

# Elements and bias weights
elements = ['P', 'T', 'R', 'E']
bias_weights = {
    "police": [0.7, 0.1, 0.1, 0.1],
    "thief": [0.1, 0.7, 0.1, 0.1],
    "rookie": [0.1, 0.1, 0.7, 0.1],
    "random": [0.25, 0.25, 0.25, 0.25]
}

# Global variables
results = {
    'police': {'size': [], 'g_runtime': [], 'b_runtime': [], 'g_caught': [], 'b_caught': []},
    'thief': {'size': [], 'g_runtime': [], 'b_runtime': [], 'g_caught': [], 'b_caught': []},
    'random': {'size': [], 'g_runtime': [], 'b_runtime': [], 'g_caught': [], 'b_caught': []},
    'rookie': {'size': [], 'g_runtime': [], 'b_runtime': [], 'g_caught': [], 'b_caught': []}
}

datasets = {
    'k_distance': {k: [] for k in K_VALUES}
}


def create_datasets(sizes, trials=3):
    global datasets, bias_weights

    if not os.path.exists('datasets'):
        os.makedirs('datasets')
    if not os.path.exists(FIXED_GRID_DATASET_DIR):
        os.makedirs(FIXED_GRID_DATASET_DIR)

    # Create datasets for each bias and size
    for size in sizes:
        for bias in results.keys():
            datasets[f'{bias}_{size}'] = []
            for trial in range(trials):
                current_weights = bias_weights[bias]
                grid = [[random.choices(elements, weights=current_weights)[0] for _ in range(size)] for _ in
                        range(size)]
                K = random.randint(1, max(2, size // 3))
                filename = f'datasets/{bias}_{size}_{trial}.txt'
                with open(filename, 'w') as f:
                    f.write(f"K: {K}\n")
                    for row in grid:
                        f.write(' '.join(row) + '\n')
                datasets[f'{bias}_{size}'].append((grid, K))

    # Extra Credit Experiment datasets (fixed size, varying K)
    size = 10  # Fixed grid size for K experiment
    for K in K_VALUES:
        for sample in range(SAMPLE):
            grid = [[random.choices(elements, weights=BALANCED_WEIGHTS)[0] for _ in range(size)] for _ in range(size)]
            filename = os.path.join(FIXED_GRID_DATASET_DIR, f'k_distance_{K}_sample{sample}.txt')
            with open(filename, 'w') as f:
                f.write(f"K: {K}\n")
                f.write('\n'.join(' '.join(row) for row in grid))
            datasets['k_distance'][K].append((grid, K))


def grid_display(grid):
    for r in grid:
        print(' '.join(r))
    print()


def implement_greedy_approach(M, K):
    start_time = time.time()
    caught = 0
    grid = [row[:] for row in M]
    catch_log = []

    rows, cols = len(grid), len(grid[0])

    # Process each column for police catching thieves in the same column
    for col in range(cols):
        police_positions = []
        thief_positions = []

        # Collect all police and thieves in this column
        for row in range(rows):
            if grid[row][col] == 'P':
                police_positions.append(row)
            elif grid[row][col] == 'T':
                thief_positions.append(row)

        # Sort positions for optimal matching
        police_positions.sort()
        thief_positions.sort()

        # Use two pointers to match police with thieves
        p_idx = t_idx = 0
        while p_idx < len(police_positions) and t_idx < len(thief_positions):
            police_row = police_positions[p_idx]
            thief_row = thief_positions[t_idx]
            distance = abs(police_row - thief_row)

            if distance <= K:
                caught += 1
                grid[thief_row][col] = 'C'  # Mark as caught
                catch_log.append(f">>Thief at ({thief_row}, {col}) was caught by Police at ({police_row}, {col})")
                p_idx += 1
                t_idx += 1
            elif police_row < thief_row:
                p_idx += 1
            else:
                t_idx += 1

    # Process rookies catching thieves (3 rookies needed)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == 'T':  # Only process thieves that haven't been caught
                adjacent_rookies = []

                # Check all four directions for rookies
                for dx, dy in directions:
                    ni, nj = i + dx, j + dy
                    if (0 <= ni < rows and 0 <= nj < cols and
                            grid[ni][nj] == 'R'):
                        adjacent_rookies.append((ni, nj))

                # If at least 3 rookies are adjacent, catch the thief
                if len(adjacent_rookies) >= 3:
                    caught += 1
                    grid[i][j] = 'C'  # Mark thief as caught

                    # Use the first 3 rookies and mark them as used
                    used_rookies = adjacent_rookies[:3]
                    for r_i, r_j in used_rookies:
                        grid[r_i][r_j] = 'U'  # Mark rookie as used

                    catch_log.append(f">>Thief at ({i}, {j}) was caught by Rookies at {used_rookies}")

    return caught, time.time() - start_time, catch_log


def implement_brute_force_approach(matrix, dist_limit):
    t0 = time.time()
    board = [row.copy() for row in matrix]
    log_entries = []

    # --- Police vs Thieves ---
    P_caught = 0
    n_rows, n_cols = len(board), len(board[0])
    for c in range(n_cols):
        P = [r for r in range(n_rows) if board[r][c] == 'P']
        robbers = [r for r in range(n_rows) if board[r][c] == 'T']
        matched_P, matched_thieves = set(), set()
        for cop in P:
            for thief in robbers:
                if abs(cop - thief) <= dist_limit and cop not in matched_P and thief not in matched_thieves:
                    P_caught += 1
                    matched_P.add(cop)
                    matched_thieves.add(thief)
                    log_entries.append(f">>Thief at ({thief}, {c}) was caught by Police at ({cop}, {c})")
                    break

    # --- Rookie squads ---
    caught_by_rookies = 0
    neighbor_offsets = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    thief_cells = [(r, c) for r in range(n_rows) for c in range(n_cols) if board[r][c] == 'T']

    for tr, tc in thief_cells:
        nearby_rookies = []
        for dr, dc in neighbor_offsets:
            nr, nc = tr + dr, tc + dc
            if 0 <= nr < n_rows and 0 <= nc < n_cols and board[nr][nc] == 'R':
                nearby_rookies.append((nr, nc))

        if len(nearby_rookies) >= 3:
            for triple in combinations(nearby_rookies, 3):
                if all(board[r][c] == 'R' for r, c in triple):
                    caught_by_rookies += 1
                    for r, c in triple:
                        board[r][c] = 'U'
                    log_entries.append(f">>Thief at ({tr}, {tc}) caught by Rookies at {triple}")
                    break

    total_caught = P_caught + caught_by_rookies
    elapsed = time.time() - t0
    return total_caught, elapsed, log_entries


def PP_ca1(M, K):
    g_count, g_time, g_log = implement_greedy_approach(M, K)
    print("Greedy Solution:")
    for log in g_log:
        print(f">>{log}")
    print(f">>Total Thieves Caught: {g_count}")

    b_count, b_time, b_log = implement_brute_force_approach(M, K)
    print("Brute-force Solution:")
    for log in b_log:
        print(f">>{log}")
    print(f">>Total Thieves Caught: {b_count}")
    return [(g_count, g_time), (b_count, b_time)]


def save_results(results_dict):
    # Convert the dictionary to a list of records
    records = []
    filename = "results.csv"
    for bias, data in results_dict.items():
        for i in range(len(data['size'])):
            records.append({
                'Bias': bias,
                'Size': data['size'][i],
                'g_runtime': data['g_runtime'][i],
                'b_runtime': data['b_runtime'][i],
                'g_caught': data['g_caught'][i],
                'b_caught': data['b_caught'][i]
            })

    # Create DataFrame and save to CSV
    df = pd.DataFrame(records)
    df.to_csv(filename, index=False)
    print(f"Results saved to {filename}")

    # Also save separate files for each bias
    for bias in results_dict.keys():
        bias_df = df[df['Bias'] == bias]
        bias_df.to_csv(f"results_{bias}.csv", index=False)

def visualize_results(results_data):
    colors = {
        'random': 'blue',
        'police': 'green',
        'rookie': 'red',
        'thief': 'purple'
    }

    # Individual plots for each bias
    for bias in results_data.keys():
        data = results_data[bias]
        sizes = data['size']

        plt.figure(figsize=(10, 5))
        plt.plot(sizes, data['g_runtime'], label='Greedy Time', marker='o')
        plt.plot(sizes, data['b_runtime'], label='Brute Time', marker='x')
        plt.title(f'Execution Time vs Grid Size ({bias} bias)')
        plt.xlabel('Grid Size')
        plt.ylabel('Time (s)')
        plt.legend()
        plt.grid(True)
        plt.savefig(f"Execution_Time_vs_Grid_Size_{bias}_bias.png")
        plt.close()

        plt.figure(figsize=(10, 5))
        plt.plot(sizes, data['g_caught'], label='Greedy Caught', marker='o')
        plt.plot(sizes, data['b_caught'], label='Brute Caught', marker='x')
        plt.title(f'Thieves Caught vs Grid Size ({bias} bias)')
        plt.xlabel('Grid Size')
        plt.ylabel('Thieves Caught')
        plt.legend()
        plt.grid(True)
        plt.savefig(f"Thieves_Caught_vs_Grid_Size_{bias}_bias.png")
        plt.close()

    # Combined plot: Execution time
    plt.figure(figsize=(12, 6))
    for bias in ['random', 'police', 'rookie', 'thief']:
        data = results_data[bias]
        sizes = data['size']
        plt.plot(sizes, data['g_runtime'], label=f'{bias} (Greedy)', color=colors[bias], linestyle='-', marker="o")
        plt.plot(sizes, data['b_runtime'], label=f'{bias} (Brute)', color=colors[bias], linestyle='--', marker="x")
    plt.title('Execution Time Comparison Across Biases')
    plt.xlabel('Grid Size')
    plt.ylabel('Time (s)')
    plt.legend()
    plt.grid(True)
    plt.savefig("Execution_Time_Comparison_Across_Biases.png")
    plt.close()

    # Combined plot: Thieves caught
    plt.figure(figsize=(12, 6))
    for bias in ['random', 'police', 'rookie', 'thief']:
        data = results_data[bias]
        sizes = data['size']
        plt.plot(sizes, data['g_caught'], label=f'{bias} (Greedy)', color=colors[bias], linestyle='-', marker="o")
        plt.plot(sizes, data['b_caught'], label=f'{bias} (Brute)', color=colors[bias], linestyle='--', marker="x")
    plt.title('Thieves Caught Comparison Across Biases')
    plt.xlabel('Grid Size')
    plt.ylabel('Thieves Caught')
    plt.legend()
    plt.grid(True)
    plt.savefig("Thieves_Caught_Comparison_Across_Biases.png")
    plt.close()


def main():
    grid_sizes = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    trials = 2
    print(">>Welcome to the Policemen Catching Thieves Program!")
    print("\n" + "*" * 50)
    print("\tMain Assignment: Varying K Values")
    print("*" * 50)

    # Create all datasets
    create_datasets(grid_sizes, trials=trials)

    # Run main experiments
    for size in grid_sizes:
        print(f"\n>>Running experiments for grid size {size}x{size}")
        for bias in results.keys():
            print(">>")
            if bias == "random":
                print(f">>Processing Random grids.")
            else:
                print(f">>Processing {bias} bias.")
            g_runtimes = []
            b_runtimes = []
            greedy_counts = []
            brute_counts = []
            for idx, (grid, K) in enumerate(datasets[f'{bias}_{size}']):
                print(f"\nGrid {idx + 1} (Bias: {bias}, Size: {size}x{size}, K: {K}):")
                grid_display(grid)
                values = PP_ca1(grid, K)
                greedy_counts.append(values[0][0])
                g_runtimes.append(values[0][1])
                brute_counts.append(values[1][0])
                b_runtimes.append(values[1][1])

            results[bias]['size'].append(size)
            results[bias]['g_runtime'].append(sum(g_runtimes) / len(g_runtimes))
            results[bias]['b_runtime'].append(sum(b_runtimes) / len(b_runtimes))
            results[bias]['g_caught'].append(sum(greedy_counts) / len(greedy_counts))
            results[bias]['b_caught'].append(sum(brute_counts) / len(brute_counts))

    # Save results and create visualizations
    visualize_results(results)
    save_results(results)


if __name__ == '__main__':
    main()
