import random
import time
import os
import json
from itertools import combinations
import numpy as np

elements = ['P', 'T', 'R', 'E']
bias_weights = {
    "police": [0.7, 0.1, 0.1, 0.1],
    "thief": [0.1, 0.7, 0.1, 0.1],
    "rookie": [0.1, 0.1, 0.7, 0.1],
    "random":[0.25, 0.25, 0.25, 0.25]
}

# Global variables to replace class attributes
results = {
    'random': {'sizes': [], 'greedy_time': [], 'brute_time': [], 'greedy_caught': [], 'brute_caught': []},
    'police': {'sizes': [], 'greedy_time': [], 'brute_time': [], 'greedy_caught': [], 'brute_caught': []},
    'thief': {'sizes': [], 'greedy_time': [], 'brute_time': [], 'greedy_caught': [], 'brute_caught': []},
    'rookie': {'sizes': [], 'greedy_time': [], 'brute_time': [], 'greedy_caught': [], 'brute_caught': []}
}
datasets = {}


def store_datasets(sizes, trials=3):
    global datasets, weights
    if not os.path.exists('datasets'):
        os.makedirs('datasets')
    for size in sizes:
        for bias in results.keys():
            datasets[f'{bias}_{size}'] = []
            for trial in range(trials):
                weights = bias_weights[bias]
                print(weights)
                print(type(weights))
                # grid = create_grid_data(size, size, bias)
                grid = [[random.choices(elements, weights=weights)[0] for _ in range(size)] for _ in range(size)]
                K = random.randint(1, max(2, size // 3))
                filename = f'datasets/{bias}_{size}_{trial}.txt'
                with open(filename, 'w') as f:
                    f.write(f"K: {K}\n")
                    for row in grid:
                        f.write(' '.join(row) + '\n')
                datasets[f'{bias}_{size}'].append((grid, K))


def display_grid(grid):
    for row in grid:
        print(' '.join(row))
    print()


def implement_greedy_approach(M, K):
    start_time = time.time()
    caught = 0
    grid = [row[:] for row in M]
    catch_log = []

    for col in range(len(grid[0])):
        police = []
        thieves = []
        for row in range(len(grid)):
            if grid[row][col] == 'P':
                police.append(row)
            elif grid[row][col] == 'T':
                thieves.append(row)
        police.sort()
        thieves.sort()
        p_idx = t_idx = 0
        while p_idx < len(police) and t_idx < len(thieves):
            if abs(police[p_idx] - thieves[t_idx]) <= K:
                caught += 1
                grid[thieves[t_idx]][col] = 'C'
                catch_log.append(f"Police at ({police[p_idx]}, {col}) caught Thief at ({thieves[t_idx]}, {col})")
                p_idx += 1
                t_idx += 1
            elif police[p_idx] < thieves[t_idx]:
                p_idx += 1
            else:
                t_idx += 1

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for i in range(len(grid)):
        for j in range(len(grid[0])):
            if grid[i][j] == 'T':
                rookies = []
                for di, dj in directions:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < len(grid) and 0 <= nj < len(grid[0]) and grid[ni][nj] == 'R':
                        rookies.append((ni, nj))
                if len(rookies) >= 3:
                    caught += 1
                    grid[i][j] = 'C'
                    for k in range(3):
                        ri, rj = rookies[k]
                        grid[ri][rj] = 'U'
                    catch_log.append(f"Thief at ({i}, {j}) caught by Rookies at {rookies[:3]}")
    return caught, time.time() - start_time, catch_log


def implement_brute_force_approach(M, K):
    start_time = time.time()
    max_caught = 0
    grid = [row[:] for row in M]
    catch_log = []

    police_caught = 0
    for col in range(len(grid[0])):
        police = []
        thieves = []
        for row in range(len(grid)):
            if grid[row][col] == 'P':
                police.append(row)
            elif grid[row][col] == 'T':
                thieves.append(row)
        used_police = set()
        used_thieves = set()
        for p in police:
            for t in thieves:
                if abs(p - t) <= K and p not in used_police and t not in used_thieves:
                    police_caught += 1
                    used_police.add(p)
                    used_thieves.add(t)
                    catch_log.append(f"Police at ({p}, {col}) caught Thief at ({t}, {col})")
                    break

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    rookie_caught = 0
    thief_positions = [(i, j) for i in range(len(grid)) for j in range(len(grid[0])) if grid[i][j] == 'T']
    for i, j in thief_positions:
        rookies = []
        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < len(grid) and 0 <= nj < len(grid[0]) and grid[ni][nj] == 'R':
                rookies.append((ni, nj))
        if len(rookies) >= 3:
            for combo in combinations(rookies, 3):
                if all(grid[r][c] == 'R' for r, c in combo):
                    rookie_caught += 1
                    for r, c in combo:
                        grid[r][c] = 'U'
                    catch_log.append(f"Thief at ({i}, {j}) caught by Rookies at {combo}")
                    break

    total_caught = police_caught + rookie_caught
    return total_caught, time.time() - start_time, catch_log


def execute_experiments(sizes, trials=3):
    global results, datasets
    store_datasets(sizes, trials=trials)
    for size in sizes:
        print(f"\n>>Running experiments for grid size {size}x{size}")
        for bias in results.keys():
            print(">>")
            if bias == "random":
                print(f">>Processing Random grids.")
            else:
                print(f">>Processing {bias} bias.")
            greedy_times = []
            brute_times = []
            greedy_counts = []
            brute_counts = []
            for idx, (grid, K) in enumerate(datasets[f'{bias}_{size}']):
                print(f"\nGrid {idx + 1} (Bias: {bias}, Size: {size}x{size}, K: {K}):")
                display_grid(grid)

                g_count, g_time, g_log = implement_greedy_approach(grid, K)
                greedy_counts.append(g_count)
                greedy_times.append(g_time)
                print("Greedy Solution:")
                for log in g_log:
                    print(f">>{log}")
                print(f">>Total Thieves Caught: {g_count}")

                b_count, b_time, b_log = implement_brute_force_approach(grid, K)
                brute_counts.append(b_count)
                brute_times.append(b_time)
                print("Brute-force Solution:")
                for log in b_log:
                    print(f">>{log}")
                print(f">>Total Thieves Caught: {b_count}")

            results[bias]['sizes'].append(size)
            results[bias]['greedy_time'].append(sum(greedy_times) / len(greedy_times))
            results[bias]['brute_time'].append(sum(brute_times) / len(brute_times))
            results[bias]['greedy_caught'].append(sum(greedy_counts) / len(greedy_counts))
            results[bias]['brute_caught'].append(sum(brute_counts) / len(brute_counts))


def save_experiment_results():
    global results
    with open("results.json", "w") as f:
        json.dump(results, f, indent=4)


import matplotlib.pyplot as plt

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
        sizes = data['sizes']

        plt.figure(figsize=(10, 5))
        plt.plot(sizes, data['greedy_time'], label='Greedy Time', marker='o')
        plt.plot(sizes, data['brute_time'], label='Brute Time', marker='x')
        plt.title(f'Execution Time vs Grid Size ({bias} bias)')
        plt.xlabel('Grid Size')
        plt.ylabel('Time (s)')
        plt.legend()
        plt.grid(True)
        plt.savefig(f"Execution_Time_vs_Grid_Size_{bias}_bias.png")
        plt.close()

        plt.figure(figsize=(10, 5))
        plt.plot(sizes, data['greedy_caught'], label='Greedy Caught', marker='o')
        plt.plot(sizes, data['brute_caught'], label='Brute Caught', marker='x')
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
        sizes = data['sizes']
        plt.plot(sizes, data['greedy_time'], label=f'{bias} (Greedy)', color=colors[bias], linestyle='-', marker="o")
        plt.plot(sizes, data['brute_time'], label=f'{bias} (Brute)', color=colors[bias], linestyle='--', marker="x")
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
        sizes = data['sizes']
        plt.plot(sizes, data['greedy_caught'], label=f'{bias} (Greedy)', color=colors[bias], linestyle='-', marker="o")
        plt.plot(sizes, data['brute_caught'], label=f'{bias} (Brute)', color=colors[bias], linestyle='--', marker="x")
    plt.title('Thieves Caught Comparison Across Biases')
    plt.xlabel('Grid Size')
    plt.ylabel('Thieves Caught')
    plt.legend()
    plt.grid(True)
    plt.savefig("Thieves_Caught_Comparison_Across_Biases.png")
    plt.close()


def main_procedural():
    grid_sizes = [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
    print(">>Welcome to the Policemen Catching Thieves Program!")
    execute_experiments(grid_sizes, trials=3)
    save_experiment_results()

    with open("results.json", "r") as f:
        results_data = json.load(f)
    visualize_results(results_data)


if __name__ == '__main__':
    main_procedural()
