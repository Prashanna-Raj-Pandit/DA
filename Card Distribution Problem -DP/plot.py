import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file
df = pd.read_csv("ec_experiment_data.csv")  # replace with your filename

# --- Plot 1: Runtime vs Deck Size for each G ---
plt.figure(figsize=(12, 6))
for g in sorted(df['G'].unique()):
    subset = df[df['G'] == g]
    plt.plot(subset['n'], subset['time_s'], marker='o', label=f"G={g}")

# plt.xscale('log')
# plt.yscale('log')
plt.xlabel("Deck Size (n)")
plt.ylabel("Runtime (seconds)")
plt.title("Runtime vs Deck Size for Different Numbers of Grandchildren (Extra Credit)")
plt.legend(title="G")
# plt.grid(True, which="both", ls="--", alpha=0.7)
plt.tight_layout()
plt.savefig("extra_credit_runtime.png", dpi=300)
plt.show()

# --- Plot 2: Memory vs Deck Size for each G ---
plt.figure(figsize=(12, 6))
for g in sorted(df['G'].unique()):
    subset = df[df['G'] == g]
    plt.plot(subset['n'], subset['memory_kb'], marker='s', label=f"G={g}")

# plt.xscale('log')
# plt.yscale('log')
plt.xlabel("Deck Size (n)")
plt.ylabel("Memory Usage (KB)")
plt.title("Memory Usage vs Deck Size for Different Numbers of Grandchildren (Extra Credit)")
plt.legend(title="G")
# plt.grid(True, which="both", ls="--", alpha=0.7)
plt.tight_layout()
plt.savefig("extra_credit_memory.png", dpi=300)
plt.show()
