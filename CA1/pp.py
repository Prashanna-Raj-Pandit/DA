import random
import time
import os
import pandas as pd
from itertools import combinations

# Constants
K_VALUES = [1,2, 3,4,5,6,7]
SAMPLE = 5
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
    'police':
        {'size': [], 'g_runtime': [], 'b_runtime': [], 'g_caught': [], 'b_caught': []},
    'thief':
        {'size': [], 'g_runtime': [], 'b_runtime': [], 'g_caught': [], 'b_caught': []},
    'random':
        {'size': [], 'g_runtime': [], 'b_runtime': [], 'g_caught': [], 'b_caught': []},
    'rookie':
        {'size': [], 'g_runtime': [], 'b_runtime': [], 'g_caught': [], 'b_caught': []}
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
                K = size //2  # Fixed K value for main experiments
                # K=1
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
            if sample == 0:  # Print sample grid for first sample
                print(f"\n>>Processing 10x10 grid (K={K})")
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
#         sizes = data['size']
#
#         plt.figure(figsize=(10, 5))
#         plt.plot(sizes, data['g_runtime'], label='Greedy Time', marker='o')
#         plt.plot(sizes, data['b_runtime'], label='Brute Time', marker='x')
#         plt.title(f'Execution Time vs Grid Size ({bias} bias)')
#         plt.xlabel('Grid Size')
#         plt.ylabel('Time (s)')
#         plt.legend()
#         plt.grid(True)
#         plt.savefig(f"Execution_Time_vs_Grid_Size_{bias}_bias.png")
#         plt.close()
#
#         plt.figure(figsize=(10, 5))
#         plt.plot(sizes, data['g_caught'], label='Greedy Caught', marker='o')
#         plt.plot(sizes, data['b_caught'], label='Brute Caught', marker='x')
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
#         sizes = data['size']
#         plt.plot(sizes, data['g_runtime'], label=f'{bias} (Greedy)', color=colors[bias], linestyle='-', marker="o")
#         plt.plot(sizes, data['b_runtime'], label=f'{bias} (Brute)', color=colors[bias], linestyle='--', marker="x")
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
#         sizes = data['size']
#         plt.plot(sizes, data['g_caught'], label=f'{bias} (Greedy)', color=colors[bias], linestyle='-', marker="o")
#         plt.plot(sizes, data['b_caught'], label=f'{bias} (Brute)', color=colors[bias], linestyle='--', marker="x")
#     plt.title('Thieves Caught Comparison Across Biases')
#     plt.xlabel('Grid Size')
#     plt.ylabel('Thieves Caught')
#     plt.legend()
#     plt.grid(True)
#     plt.savefig("Thieves_Caught_Comparison_Across_Biases.png")
#     plt.close()
#
#
# def plot_experiment3_results():
#     """Plot results from Extra Credit Experiment (K-values)"""
#     # Load the results
#     results_file = os.path.join(RESULTS_DIR, 'experiment3_results.csv')
#     if not os.path.exists(results_file):
#         print("Extra Credit Experiment results not found. Run experiment first.")
#         return
#
#     df = pd.read_csv(results_file)
#
#     # Create subplots
#     fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
#
#     # Plot 1: Execution Time vs K values
#     ax1.plot(df['K'], df['greedy_time'], 'o-', label='Greedy Approach', linewidth=2, markersize=8)
#     ax1.plot(df['K'], df['brute_time'], 's-', label='Brute Force Approach', linewidth=2, markersize=8)
#     ax1.set_xlabel('K Value (Maximum Distance)', fontsize=12)
#     ax1.set_ylabel('Execution Time (seconds)', fontsize=12)
#     ax1.set_title('Execution Time vs K Value', fontsize=14)
#     ax1.legend(fontsize=11)
#     ax1.grid(True, alpha=0.3)
#
#     # Plot 2: Thieves Caught vs K values
#     ax2.plot(df['K'], df['greedy_caught'], 'o-', label='Greedy Approach', linewidth=2, markersize=8)
#     ax2.plot(df['K'], df['brute_caught'], 's-', label='Brute Force Approach', linewidth=2, markersize=8)
#     ax2.set_xlabel('K Value (Maximum Distance)', fontsize=12)
#     ax2.set_ylabel('Thieves Caught', fontsize=12)
#     ax2.set_title('Thieves Caught vs K Value', fontsize=14)
#     ax2.legend(fontsize=11)
#     ax2.grid(True, alpha=0.3)
#
#     plt.tight_layout()
#     plt.savefig(os.path.join(RESULTS_DIR, 'experiment3_summary.png'), dpi=300, bbox_inches='tight')
#     # plt.show()
#
#     # Additional detailed plots
#     fig, (ax3, ax4) = plt.subplots(1, 2, figsize=(15, 6))
#
#     # Plot 3: Police vs Rookie catches (Greedy)
#     ax3.plot(df['K'], df['greedy_police'], 'o-', label='Police Catches', linewidth=2, markersize=8)
#     ax3.plot(df['K'], df['greedy_rookie'], 's-', label='Rookie Catches', linewidth=2, markersize=8)
#     ax3.set_xlabel('K Value (Maximum Distance)', fontsize=12)
#     ax3.set_ylabel('Number of Catches', fontsize=12)
#     ax3.set_title('Greedy Approach: Police vs Rookie Catches', fontsize=14)
#     ax3.legend(fontsize=11)
#     ax3.grid(True, alpha=0.3)
#
#     # Plot 4: Police vs Rookie catches (Brute Force)
#     ax4.plot(df['K'], df['brute_police'], 'o-', label='Police Catches', linewidth=2, markersize=8)
#     ax4.plot(df['K'], df['brute_rookie'], 's-', label='Rookie Catches', linewidth=2, markersize=8)
#     ax4.set_xlabel('K Value (Maximum Distance)', fontsize=12)
#     ax4.set_ylabel('Number of Catches', fontsize=12)
#     ax4.set_title('Brute Force Approach: Police vs Rookie Catches', fontsize=14)
#     ax4.legend(fontsize=11)
#     ax4.grid(True, alpha=0.3)
#
#     plt.tight_layout()
#     plt.savefig(os.path.join(RESULTS_DIR, 'experiment3_detailed.png'), dpi=300, bbox_inches='tight')
#     # plt.show()
#


import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt


def visualize_results(results_data):
    # Set Seaborn style with distinct color palette
    sns.set_theme(style="whitegrid")
    distinct_palette = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#F9A602", "#6A0572", "#AB83A1"]
    sns.set_palette(distinct_palette)

    # Convert results to DataFrame for easier plotting
    records = []
    for bias, data in results_data.items():
        for i in range(len(data['size'])):
            records.append({
                'Bias': bias,
                'Size': data['size'][i],
                'Greedy_Time': data['g_runtime'][i],
                'Brute_Time': data['b_runtime'][i],
                'Greedy_Caught': data['g_caught'][i],
                'Brute_Caught': data['b_caught'][i]
            })

    df = pd.DataFrame(records)

    # 1. Execution Time vs Grid Size (Facet Grid)
    plt.figure(figsize=(14, 10))
    g = sns.FacetGrid(df, col="Bias", col_wrap=2, height=4, aspect=1.5)
    g.map_dataframe(sns.lineplot, x="Size", y="Greedy_Time", label="Greedy",
                    marker="o", linewidth=2.5, color="#FF6B6B")  # Coral red
    g.map_dataframe(sns.lineplot, x="Size", y="Brute_Time", label="Brute Force",
                    marker="s", linewidth=2.5, color="#4ECDC4")  # Teal
    g.set_axis_labels("Grid Size", "Execution Time (seconds)")
    g.add_legend()
    plt.savefig(os.path.join(RESULTS_DIR, "Execution_Time_vs_Size_Facet.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Thieves Caught vs Grid Size (Facet Grid) - with distinct colors
    plt.figure(figsize=(14, 10))
    g = sns.FacetGrid(df, col="Bias", col_wrap=2, height=4, aspect=1.5)
    g.map_dataframe(sns.lineplot, x="Size", y="Greedy_Caught", label="Greedy",
                    marker="o", linewidth=2.5, color="#45B7D1")  # Sky blue
    g.map_dataframe(sns.lineplot, x="Size", y="Brute_Caught", label="Brute Force",
                    marker="s", linewidth=2.5, color="#F9A602")  # Golden yellow
    g.set_axis_labels("Grid Size", "Thieves Caught")
    g.add_legend()
    plt.savefig(os.path.join(RESULTS_DIR, "Thieves_Caught_vs_Size_Facet.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # 3. Performance Ratio (Brute/Greedy)
    df['Time_Ratio'] = df['Brute_Time'] / df['Greedy_Time']
    df['Caught_Ratio'] = df['Brute_Caught'] / df['Greedy_Caught']

    plt.figure(figsize=(12, 8))
    for bias in df['Bias'].unique():
        bias_data = df[df['Bias'] == bias]
        plt.plot(bias_data['Size'], bias_data['Time_Ratio'],
                 marker='o', linewidth=2.5, label=f'{bias}', markersize=8)

    plt.axhline(y=1, color='red', linestyle='--', alpha=0.7, label='Equal Performance')
    plt.title('Time Ratio: Brute Force / Greedy', fontsize=16, fontweight='bold')
    plt.xlabel('Grid Size', fontsize=12)
    plt.ylabel('Time Ratio (Brute/Greedy)', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.savefig(os.path.join(RESULTS_DIR, "Time_Ratio_Comparison.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # 4. Efficiency Heatmap
    pivot_table = df.pivot_table(values='Greedy_Caught', index='Size', columns='Bias')
    plt.figure(figsize=(10, 8))
    sns.heatmap(pivot_table, annot=True, fmt='.1f', cmap='YlOrRd',
                cbar_kws={'label': 'Thieves Caught'}, square=True)
    plt.title('Greedy Algorithm Performance Heatmap', fontsize=16, fontweight='bold')
    plt.savefig(os.path.join(RESULTS_DIR, "Performance_Heatmap.png"), dpi=300, bbox_inches='tight')
    plt.close()

    # 5. Side-by-side comparison (New)
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Time comparison
    sns.barplot(data=df, x='Size', y='Greedy_Time', hue='Bias', ax=axes[0],
                palette=distinct_palette[:4], alpha=0.8)
    axes[0].set_title('Greedy Algorithm: Time by Grid Size and Bias', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Grid Size')
    axes[0].set_ylabel('Execution Time (seconds)')
    axes[0].tick_params(axis='x', rotation=45)

    # Caught comparison
    sns.barplot(data=df, x='Size', y='Greedy_Caught', hue='Bias', ax=axes[1],
                palette=distinct_palette[:4], alpha=0.8)
    axes[1].set_title('Greedy Algorithm: Thieves Caught by Grid Size and Bias', fontsize=14, fontweight='bold')
    axes[1].set_xlabel('Grid Size')
    axes[1].set_ylabel('Thieves Caught')
    axes[1].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, "Side_by_Side_Comparison.png"), dpi=300, bbox_inches='tight')
    plt.close()


def plot_experiment3_results():
    """Plot results from Extra Credit Experiment (K-values) using Seaborn"""
    # Load the results
    results_file = os.path.join(RESULTS_DIR, 'experiment3_results.csv')
    if not os.path.exists(results_file):
        print("Extra Credit Experiment results not found. Run experiment first.")
        return

    df = pd.read_csv(results_file)

    # Set Seaborn style with distinct colors
    sns.set_theme(style="whitegrid")
    k_experiment_palette = ["#E63946", "#F1FAEE", "#A8DADC", "#457B9D", "#1D3557", "#F9A602"]
    sns.set_palette(k_experiment_palette)

    # 1. Execution Time vs K values
    plt.figure(figsize=(14, 6))
    plt.subplot(1, 2, 1)
    sns.lineplot(data=df, x='K', y='greedy_time', label='Greedy',
                 marker='o', linewidth=2.5, color="#E63946")  # Red
    sns.lineplot(data=df, x='K', y='brute_time', label='Brute Force',
                 marker='s', linewidth=2.5, color="#457B9D")  # Navy blue
    plt.xlabel('K Value (Maximum Distance)', fontweight='bold')
    plt.ylabel('Execution Time (seconds)', fontweight='bold')
    plt.title('Execution Time vs K Value', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)

    # 2. Thieves Caught vs K values
    plt.subplot(1, 2, 2)
    sns.lineplot(data=df, x='K', y='greedy_caught', label='Greedy',
                 marker='o', linewidth=2.5, color="#E63946")  # Red
    sns.lineplot(data=df, x='K', y='brute_caught', label='Brute Force',
                 marker='s', linewidth=2.5, color="#457B9D")  # Navy blue
    plt.xlabel('K Value (Maximum Distance)', fontweight='bold')
    plt.ylabel('Thieves Caught', fontweight='bold')
    plt.title('Thieves Caught vs K Value', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'K_Experiment_Summary_Seaborn.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # 3. Catch Type Breakdown (Bar Chart)
    plt.figure(figsize=(14, 10))

    # Greedy approach
    plt.subplot(2, 1, 1)
    x_pos = np.arange(len(df['K']))
    width = 0.35

    plt.bar(x_pos - width / 2, df['greedy_police'], width, label='Police Catches', color='#A8DADC', alpha=0.8)
    plt.bar(x_pos + width / 2, df['greedy_rookie'], width, label='Rookie Catches', color='#1D3557', alpha=0.8)
    plt.xlabel('K Value', fontweight='bold')
    plt.ylabel('Number of Catches', fontweight='bold')
    plt.title('Greedy Approach: Catch Type Distribution', fontsize=14, fontweight='bold')
    plt.xticks(x_pos, df['K'])
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Brute Force approach
    plt.subplot(2, 1, 2)
    plt.bar(x_pos - width / 2, df['brute_police'], width, label='Police Catches', color='#A8DADC', alpha=0.8)
    plt.bar(x_pos + width / 2, df['brute_rookie'], width, label='Rookie Catches', color='#1D3557', alpha=0.8)
    plt.xlabel('K Value', fontweight='bold')
    plt.ylabel('Number of Catches', fontweight='bold')
    plt.title('Brute Force Approach: Catch Type Distribution', fontsize=14, fontweight='bold')
    plt.xticks(x_pos, df['K'])
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'Catch_Type_Distribution.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # 4. Performance Comparison (Subplot Matrix)
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    # Time comparison
    axes[0, 0].bar(df['K'] - 0.2, df['greedy_time'], 0.4, label='Greedy', color='#E63946', alpha=0.8)
    axes[0, 0].bar(df['K'] + 0.2, df['brute_time'], 0.4, label='Brute Force', color='#457B9D', alpha=0.8)
    axes[0, 0].set_title('Execution Time Comparison', fontweight='bold')
    axes[0, 0].set_xlabel('K Value')
    axes[0, 0].set_ylabel('Time (seconds)')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # Catch comparison
    axes[0, 1].bar(df['K'] - 0.2, df['greedy_caught'], 0.4, label='Greedy', color='#E63946', alpha=0.8)
    axes[0, 1].bar(df['K'] + 0.2, df['brute_caught'], 0.4, label='Brute Force', color='#457B9D', alpha=0.8)
    axes[0, 1].set_title('Thieves Caught Comparison', fontweight='bold')
    axes[0, 1].set_xlabel('K Value')
    axes[0, 1].set_ylabel('Thieves Caught')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # Police catches
    axes[1, 0].plot(df['K'], df['greedy_police'], marker='o', label='Greedy',
                    color='#E63946', linewidth=2.5, markersize=8)
    axes[1, 0].plot(df['K'], df['brute_police'], marker='s', label='Brute Force',
                    color='#457B9D', linewidth=2.5, markersize=8)
    axes[1, 0].set_title('Police Catches Comparison', fontweight='bold')
    axes[1, 0].set_xlabel('K Value')
    axes[1, 0].set_ylabel('Police Catches')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # Rookie catches
    axes[1, 1].plot(df['K'], df['greedy_rookie'], marker='o', label='Greedy',
                    color='#E63946', linewidth=2.5, markersize=8)
    axes[1, 1].plot(df['K'], df['brute_rookie'], marker='s', label='Brute Force',
                    color='#457B9D', linewidth=2.5, markersize=8)
    axes[1, 1].set_title('Rookie Catches Comparison', fontweight='bold')
    axes[1, 1].set_xlabel('K Value')
    axes[1, 1].set_ylabel('Rookie Catches')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(RESULTS_DIR, 'K_Experiment_Matrix.png'), dpi=300, bbox_inches='tight')
    plt.close()

    # 5. Correlation Heatmap
    plt.figure(figsize=(10, 8))
    correlation = df[['K', 'greedy_time', 'brute_time', 'greedy_caught', 'brute_caught',
                      'greedy_police', 'greedy_rookie', 'brute_police', 'brute_rookie']].corr()
    sns.heatmap(correlation, annot=True, cmap='RdBu_r', center=0, fmt='.2f',
                square=True, cbar_kws={'label': 'Correlation Coefficient'})
    plt.title('Correlation Matrix of K-Experiment Results', fontsize=16, fontweight='bold')
    plt.savefig(os.path.join(RESULTS_DIR, 'Correlation_Matrix.png'), dpi=300, bbox_inches='tight')
    plt.close()
def main():
    grid_sizes=np.arange(5,21,1)
    grid_sizes=grid_sizes.tolist()
    trials = 2
    print(">>Welcome to the Policemen Catching Thieves Program!")
    print("\n" + "*" * 50)
    print("\tMain Assignment: Modification,1,3, and 4 with Fixed K value")
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
