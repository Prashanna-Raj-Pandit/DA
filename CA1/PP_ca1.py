import random
import time
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations
from copy import deepcopy

# Constants
K_VALUES = [ 5, 6, 7, 8, 9, 10]
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
                K = size // 2  # Fixed K value for main experiments
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



def extra_credit_exp():
    """Extra Credit Experiment: Varying K values"""
    print("\n" + "*" * 50)
    print("\tExtra Credit Experiment: Varying K Values")
    print("*" * 50)

    results = []

    for K in K_VALUES:
        for sample, (grid, _) in enumerate(datasets['k_distance'][K]):
            print(f"\nProcessing 10x10 grid (K={K})")
            if sample == 0:  # Print sample grid for first sample
                grid_display(grid)

            # Run both approaches
            g_count, g_time, g_log = implement_greedy_approach([row[:] for row in grid], K)
            b_count, b_time, b_log = implement_brute_force_approach([row[:] for row in grid], K)

            # Count police vs rookie catches and extract details
            g_police_logs = [log for log in g_log if "Police" in log]
            g_rookie_logs = [log for log in g_log if "Rookies" in log]
            g_police = len(g_police_logs)
            g_rookie = len(g_rookie_logs)

            b_police_logs = [log for log in b_log if "Police" in log]
            b_rookie_logs = [log for log in b_log if "Rookies" in log]
            b_police = len(b_police_logs)
            b_rookie = len(b_rookie_logs)

            # Print detailed results for the first sample of each K value
            if sample == 0:
                print(f"\n>> K = {K} - Greedy Approach Results:")
                if g_police > 0:
                    print(f">> Police catches ({g_police} thieves):")
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
                    print(f">> Rookie squad catches ({g_rookie} thieves):")
                    for log in g_rookie_logs:
                        print(f">> {log}")

                print(f"\n>> K = {K} - Brute Force Approach Results:")
                if b_police > 0:
                    print(f">> Police catches ({b_police} thieves):")
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
                    print(f">> Rookie squad catches ({b_rookie} thieves):")
                    for log in b_rookie_logs:
                        print(f">> {log}")

            results.append({
                'K': K,
                'sample': sample,
                'greedy_time': g_time,
                'brute_time': b_time,
                'greedy_caught': g_count,
                'brute_caught': b_count,
                'greedy_police': g_police,
                'greedy_rookie': g_rookie,
                'brute_police': b_police,
                'brute_rookie': b_rookie
            })

    # Save results
    df = pd.DataFrame(results)
    agg_df = df.groupby('K').mean().reset_index()

    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)

    agg_df.to_csv(os.path.join(RESULTS_DIR, 'experiment3_results.csv'), index=False)
    print("K-value experiment results saved to experiment3_results.csv")
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

def plot_experiment3_results():
    """Plot results from Extra Credit Experiment (K-values)"""
    # Load the results
    results_file = os.path.join(RESULTS_DIR, 'experiment3_results.csv')
    if not os.path.exists(results_file):
        print("Extra Credit Experiment results not found. Run experiment first.")
        return

    df = pd.read_csv(results_file)

    # Create subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Plot 1: Execution Time vs K values
    ax1.plot(df['K'], df['greedy_time'], 'o-', label='Greedy Approach', linewidth=2, markersize=8)
    ax1.plot(df['K'], df['brute_time'], 's-', label='Brute Force Approach', linewidth=2, markersize=8)
    ax1.set_xlabel('K Value (Maximum Distance)', fontsize=12)
    ax1.set_ylabel('Execution Time (seconds)', fontsize=12)
    ax1.set_title('Execution Time vs K Value', fontsize=14)
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)

    # Plot 2: Thieves Caught vs K values
    ax2.plot(df['K'], df['greedy_caught'], 'o-', label='Greedy Approach', linewidth=2, markersize=8)
    ax2.plot(df['K'], df['brute_caught'], 's-', label='Brute Force Approach', linewidth=2, markersize=8)
    ax2.set_xlabel('K Value (Maximum Distance)', fontsize=12)
    ax2.set_ylabel('Thieves Caught', fontsize=12)
    ax2.set_title('Thieves Caught vs K Value', fontsize=14)
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'experiment3_summary.png'), dpi=300, bbox_inches='tight')
    # plt.show()

    # Additional detailed plots
    fig, (ax3, ax4) = plt.subplots(1, 2, figsize=(15, 6))

    # Plot 3: Police vs Rookie catches (Greedy)
    ax3.plot(df['K'], df['greedy_police'], 'o-', label='Police Catches', linewidth=2, markersize=8)
    ax3.plot(df['K'], df['greedy_rookie'], 's-', label='Rookie Catches', linewidth=2, markersize=8)
    ax3.set_xlabel('K Value (Maximum Distance)', fontsize=12)
    ax3.set_ylabel('Number of Catches', fontsize=12)
    ax3.set_title('Greedy Approach: Police vs Rookie Catches', fontsize=14)
    ax3.legend(fontsize=11)
    ax3.grid(True, alpha=0.3)

    # Plot 4: Police vs Rookie catches (Brute Force)
    ax4.plot(df['K'], df['brute_police'], 'o-', label='Police Catches', linewidth=2, markersize=8)
    ax4.plot(df['K'], df['brute_rookie'], 's-', label='Rookie Catches', linewidth=2, markersize=8)
    ax4.set_xlabel('K Value (Maximum Distance)', fontsize=12)
    ax4.set_ylabel('Number of Catches', fontsize=12)
    ax4.set_title('Brute Force Approach: Police vs Rookie Catches', fontsize=14)
    ax4.legend(fontsize=11)
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'experiment3_detailed.png'), dpi=300, bbox_inches='tight')
    # plt.show()

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

    # Run K-value experiment
    extra_credit_exp()

    # Save results and create visualizations
    visualize_results(results)
    plot_experiment3_results()
    save_results(results)


if __name__ == '__main__':
    main()


# import random
# import time
# import os
# import json
# import pandas as pd
# import matplotlib.pyplot as plt
# import time
# from itertools import combinations
#
#
# elements = ['P', 'T', 'R', 'E']
# datasets = {}
# bias_weights = {
#     "police": [0.7, 0.1, 0.1, 0.1],
#     "thief": [0.1, 0.7, 0.1, 0.1],
#     "rookie": [0.1, 0.1, 0.7, 0.1],
#     "random": [0.25, 0.25, 0.25, 0.25]
# }
#
# # Global variables to replace class attributes
# results = {
#     'police': {'size': [], 'g_runtime': [], 'b_runtime': [], 'g_caught': [], 'b_caught': []},
#     'thief': {'size': [], 'g_runtime': [], 'b_runtime': [], 'g_caught': [], 'b_caught': []},
#     'random': {'size': [], 'g_runtime': [], 'b_runtime': [], 'g_caught': [], 'b_caught': []},
#     'rookie': {'size': [], 'g_runtime': [], 'b_runtime': [], 'g_caught': [], 'b_caught': []}
# }
#
# def create_datasets(size, trials=3):
#     global datasets, weights
#     if not os.path.exists('datasets'):
#         os.makedirs('datasets')
#     for size in size:
#         for bias in results.keys():
#             datasets[f'{bias}_{size}'] = []
#             for trial in range(trials):
#                 weights = bias_weights[bias]
#                 print(weights)
#                 print(type(weights))
#                 grid = [[random.choices(elements, weights=weights)[0] for _ in range(size)] for _ in range(size)]
#                 # K = random.randint(1, max(2, size // 3))
#                 K=size//2
#                 filename = f'datasets/{bias}_{size}_{trial}.txt'
#                 with open(filename, 'w') as f:
#                     f.write(f"K: {K}\n")
#                     for row in grid:
#                         f.write(' '.join(row) + '\n')
#                 datasets[f'{bias}_{size}'].append((grid, K))
#
# def save_results(results_dict):
#     # Convert the dictionary to a list of records
#     records = []
#     filename = "results.csv"
#     for bias, data in results_dict.items():
#         for i in range(len(data['size'])):
#             records.append({
#                 'Bias': bias,
#                 'Size': data['size'][i],
#                 'g_runtime': data['g_runtime'][i],
#                 'b_runtime': data['b_runtime'][i],
#                 'g_caught': data['g_caught'][i],
#                 'b_caught': data['b_caught'][i]
#             })
#
#     # Create DataFrame and save to CSV
#     df = pd.DataFrame(records)
#     df.to_csv(filename, index=False)
#     print(f"Results saved to {filename}")
#
#     # Also save separate files for each bias
#     for bias in results_dict.keys():
#         bias_df = df[df['Bias'] == bias]
#         bias_df.to_csv(f"results_{bias}.csv", index=False)
#
#
#
# def implement_greedy_approach(M, K):
#     start_time = time.time()
#     caught = 0
#     grid = [row[:] for row in M]
#     catch_log = []
#
#     rows, cols = len(grid), len(grid[0])
#
#     # Process each column for police catching thieves in the same column
#     for col in range(cols):
#         police_positions = []
#         thief_positions = []
#
#         # Collect all police and thieves in this column
#         for row in range(rows):
#             if grid[row][col] == 'P':
#                 police_positions.append(row)
#             elif grid[row][col] == 'T':
#                 thief_positions.append(row)
#
#         # Sort positions for optimal matching
#         police_positions.sort()
#         thief_positions.sort()
#
#         # Use two pointers to match police with thieves
#         p_idx = t_idx = 0
#         while p_idx < len(police_positions) and t_idx < len(thief_positions):
#             police_row = police_positions[p_idx]
#             thief_row = thief_positions[t_idx]
#             distance = abs(police_row - thief_row)
#
#             if distance <= K:
#                 caught += 1
#                 grid[thief_row][col] = 'C'  # Mark as caught
#                 catch_log.append(f">>Thief at ({thief_row}, {col}) was caught by Police at ({police_row}, {col})")
#                 p_idx += 1
#                 t_idx += 1
#             elif police_row < thief_row:
#                 p_idx += 1
#             else:
#                 t_idx += 1
#
#     # Process rookies catching thieves (3 rookies needed)
#     dir = [(-1, 0), (1, 0), (0, -1), (0, 1)]
#
#     for i in range(rows):
#         for j in range(cols):
#             if grid[i][j] == 'T':  # Only process thieves that haven't been caught
#                 adjacent_rookies = []
#
#                 # Check all four dir for rookies
#                 for dx, dy in dir:
#                     ni, nj = i + dx, j + dy
#                     if (0 <= ni < rows and 0 <= nj < cols and
#                             grid[ni][nj] == 'R'):
#                         adjacent_rookies.append((ni, nj))
#
#                 # If at least 3 rookies are adjacent, catch the thief
#                 if len(adjacent_rookies) >= 3:
#                     caught += 1
#                     grid[i][j] = 'C'  # Mark thief as caught
#
#                     # Use the first 3 rookies and mark them as used
#                     used_rookies = adjacent_rookies[:3]
#                     for r_i, r_j in used_rookies:
#                         grid[r_i][r_j] = 'U'  # Mark rookie as used
#
#                     catch_log.append(f">>Thief at ({i}, {j}) was caught by Rookies at {used_rookies}")
#
#     return caught, time.time() - start_time, catch_log
#
#
#
# def implement_brute_force_approach(matrix, dist_limit):
#     t0 = time.time()
#     board = [row.copy() for row in matrix]
#     log_entries = []
#
#     # --- Police vs Thieves ---
#     P_caught = 0
#     n_rows, n_cols = len(board), len(board[0])
#     for c in range(n_cols):
#         P = [r for r in range(n_rows) if board[r][c] == 'P']
#         robbers = [r for r in range(n_rows) if board[r][c] == 'T']
#         matched_P, matched_thieves = set(), set()
#         for cop in P:
#             for thief in robbers:
#                 if abs(cop - thief) <= dist_limit and cop not in matched_P and thief not in matched_thieves:
#                     P_caught += 1
#                     matched_P.add(cop)
#                     matched_thieves.add(thief)
#                     log_entries.append(f">>Thief at ({thief}, {c}) was caught by Police at ({cop}, {c})")
#                     break
#
#     # --- Rookie squads ---
#     caught_by_rookies = 0
#     neighbor_offsets = [(0,1), (0,-1), (1,0), (-1,0)]
#     thief_cells = [(r, c) for r in range(n_rows) for c in range(n_cols) if board[r][c] == 'T']
#
#     for tr, tc in thief_cells:
#         nearby_rookies = []
#         for dr, dc in neighbor_offsets:
#             nr, nc = tr + dr, tc + dc
#             if 0 <= nr < n_rows and 0 <= nc < n_cols and board[nr][nc] == 'R':
#                 nearby_rookies.append((nr, nc))
#
#         if len(nearby_rookies) >= 3:
#             for triple in combinations(nearby_rookies, 3):
#                 if all(board[r][c] == 'R' for r, c in triple):
#                     caught_by_rookies += 1
#                     for r, c in triple:
#                         board[r][c] = 'U'
#                     log_entries.append(f">>Thief at ({tr}, {tc}) caught by Rookies at {triple}")
#                     break
#
#     total_caught = P_caught + caught_by_rookies
#     elapsed = time.time() - t0
#     return total_caught, elapsed, log_entries
#
# def PP_ca1(M, K):
#     g_count, g_time, g_log = implement_greedy_approach(M, K)
#     print("Greedy Solution:")
#     for log in g_log:
#         print(f">>{log}")
#     print(f">>Total Thieves Caught: {g_count}")
#
#     b_count, b_time, b_log = implement_brute_force_approach(M, K)
#     print("Brute-force Solution:")
#     for log in b_log:
#         print(f">>{log}")
#     print(f">>Total Thieves Caught: {b_count}")
#     return [(g_count, g_time), (b_count, b_time)]
#
#
# def visualize_results(results_data):
#     colors = {
#         'random': 'blue',
#         'police': 'green',
#         'rookie': 'red',
#         'thief': 'purple'
#     }
#
#     # Individual plots for each bias
#     for bias in results_data.keys():
#         data = results_data[bias]
#         size = data['size']
#
#         plt.figure(figsize=(10, 5))
#         plt.plot(size, data['g_runtime'], label='Greedy Time', marker='o')
#         plt.plot(size, data['b_runtime'], label='Brute Time', marker='x')
#         plt.title(f'Execution Time vs Grid Size ({bias} bias)')
#         plt.xlabel('Grid Size')
#         plt.ylabel('Time (s)')
#         plt.legend()
#         plt.grid(True)
#         plt.savefig(f"Execution_Time_vs_Grid_Size_{bias}_bias.png")
#         plt.close()
#
#         plt.figure(figsize=(10, 5))
#         plt.plot(size, data['g_caught'], label='Greedy Caught', marker='o')
#         plt.plot(size, data['b_caught'], label='Brute Caught', marker='x')
#         plt.title(f'Thieves Caught vs Grid Size ({bias} bias)')
#         plt.xlabel('Grid Size')
#         plt.ylabel('Thieves Caught')
#         plt.legend()
#         plt.grid(True)
#         plt.savefig(f"Thieves_Caught_vs_Grid_Size_{bias}_bias.png")
#         plt.close()
#
#     # Combined plot: Execution time
#     plt.figure(figsize=(12, 6))
#     for bias in ['random', 'police', 'rookie', 'thief']:
#         data = results_data[bias]
#         size = data['size']
#         plt.plot(size, data['g_runtime'], label=f'{bias} (Greedy)', color=colors[bias], linestyle='-', marker="o")
#         plt.plot(size, data['b_runtime'], label=f'{bias} (Brute)', color=colors[bias], linestyle='--', marker="x")
#     plt.title('Execution Time Comparison Across Biases')
#     plt.xlabel('Grid Size')
#     plt.ylabel('Time (s)')
#     plt.legend()
#     plt.grid(True)
#     plt.savefig("Execution_Time_Comparison_Across_Biases.png")
#     plt.close()
#
#     # Combined plot: Thieves caught
#     plt.figure(figsize=(12, 6))
#     for bias in ['random', 'police', 'rookie', 'thief']:
#         data = results_data[bias]
#         size = data['size']
#         plt.plot(size, data['g_caught'], label=f'{bias} (Greedy)', color=colors[bias], linestyle='-', marker="o")
#         plt.plot(size, data['b_caught'], label=f'{bias} (Brute)', color=colors[bias], linestyle='--', marker="x")
#     plt.title('Thieves Caught Comparison Across Biases')
#     plt.xlabel('Grid Size')
#     plt.ylabel('Thieves Caught')
#     plt.legend()
#     plt.grid(True)
#     plt.savefig("Thieves_Caught_Comparison_Across_Biases.png")
#     plt.close()
#
# def grid_display(M):
#     for r in M:
#         print(' '.join(r))
#     print()
#
# def main():
#     grid_size = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
#     trials = 2
#     print(">>Welcome to the Policemen Catching Thieves Program!")
#     # execute_experiments(grid_size, trials=3)
#     global results, datasets
#     create_datasets(grid_size, trials=trials)
#     for size in grid_size:
#         print(f"\n>>Running experiments for grid size {size}x{size}")
#         for bias in results.keys():
#             print(">>")
#             if bias == "random":
#                 print(f">>Processing Random grids.")
#             else:
#                 print(f">>Processing {bias} bias.")
#             g_runtimes = []
#             b_runtimes = []
#             greedy_counts = []
#             brute_counts = []
#             for idx, (grid, K) in enumerate(datasets[f'{bias}_{size}']):
#                 print(f"\nGrid {idx + 1} (Bias: {bias}, Size: {size}x{size}, K: {K}):")
#                 grid_display(grid)
#                 values = PP_ca1(grid, K)
#                 greedy_counts.append(values[0][0])
#                 g_runtimes.append(values[0][1])
#                 brute_counts.append(values[1][0])
#                 b_runtimes.append(values[1][1])
#
#             results[bias]['size'].append(size)
#             results[bias]['g_runtime'].append(sum(g_runtimes) / len(g_runtimes))
#             results[bias]['b_runtime'].append(sum(b_runtimes) / len(b_runtimes))
#             results[bias]['g_caught'].append(sum(greedy_counts) / len(greedy_counts))
#             results[bias]['b_caught'].append(sum(brute_counts) / len(brute_counts))
#
#     visualize_results(results)
#     save_results(results)
#
#
# if __name__ == '__main__':
#     main()
