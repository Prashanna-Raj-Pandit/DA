
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
