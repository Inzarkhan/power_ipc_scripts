import re
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from tabulate import tabulate

# Function to read and extract power data from a 'stats.txt' file
def extract_dynamic_power_data(file_path):
    with open(file_path, 'r') as file:
        stats_data = file.readlines()

    dynamic_power_data = {}
    time_seconds = []

    for line in stats_data:
        if line.startswith("simSeconds"):
            time_seconds.append(float(re.search(r'\d+\.\d+', line).group()))
        elif "power_model.dynamicPower" in line:
            cpu_match = re.search(r'system\.cpu_cluster\.cpus(\d+)\.power_model\.dynamicPower', line)
            if cpu_match:
                cpu_id = cpu_match.group(1)
                power = float(re.search(r'(\d+\.\d+)', line).group())
                if cpu_id not in dynamic_power_data:
                    dynamic_power_data[cpu_id] = []
                dynamic_power_data[cpu_id].append(power)

    # Ensure all lists have the same length
    min_length = min(len(time_seconds), *[len(powers) for powers in dynamic_power_data.values()])
    time_seconds = time_seconds[:min_length]
    for cpu_id in dynamic_power_data:
        dynamic_power_data[cpu_id] = dynamic_power_data[cpu_id][:min_length]

    return time_seconds, dynamic_power_data

# File paths for the two 'stats.txt' files
file_path_dvfs = '/home/said/GEM5/ARM/gem5/output/mibench/networkdijkstralarge_L3_dvfsenable/stats.txt'
file_path_no_dvfs = '/home/said/GEM5/ARM/gem5/output/mibench/networkdijkstralarge_L3_dvfsdisable/stats.txt'

# Extract data from both files
time_dvfs, dynamic_power_dvfs = extract_dynamic_power_data(file_path_dvfs)
time_no_dvfs, dynamic_power_no_dvfs = extract_dynamic_power_data(file_path_no_dvfs)

# Find the common minimum length between time arrays and power data
min_length = min(len(time_dvfs), len(time_no_dvfs))
time_dvfs, time_no_dvfs = time_dvfs[:min_length], time_no_dvfs[:min_length]

for core_id in dynamic_power_dvfs:
    dynamic_power_dvfs[core_id] = dynamic_power_dvfs[core_id][:min_length]
    dynamic_power_no_dvfs[core_id] = dynamic_power_no_dvfs[core_id][:min_length]

# Calculate average dynamic power for each core
average_dynamic_power_dvfs = {
    core_id: sum(powers) / len(powers) for core_id, powers in dynamic_power_dvfs.items()
}
average_dynamic_power_no_dvfs = {
    core_id: sum(powers) / len(powers) for core_id, powers in dynamic_power_no_dvfs.items()
}

# Calculate the average total dynamic power across all cores
total_dynamic_power_dvfs = [
    sum(powers) for powers in zip(*dynamic_power_dvfs.values())
]
total_dynamic_power_no_dvfs = [
    sum(powers) for powers in zip(*dynamic_power_no_dvfs.values())
]
average_total_dynamic_power_dvfs = sum(total_dynamic_power_dvfs) / len(total_dynamic_power_dvfs)
average_total_dynamic_power_no_dvfs = sum(total_dynamic_power_no_dvfs) / len(total_dynamic_power_no_dvfs)

# Print detailed dynamic power values along with averages
print("\nDetailed Dynamic Power Values:")
for core_id in dynamic_power_dvfs:
    print(f"\nCore {core_id}:")
    print("Time (s) | Dynamic Power with DVFS (W) | Dynamic Power without DVFS (W)")
    print("-" * 55)
    for t, p_dvfs, p_no_dvfs in zip(time_dvfs, dynamic_power_dvfs[core_id], dynamic_power_no_dvfs[core_id]):
        print(f"{t:8.3f} | {p_dvfs:26.6f} | {p_no_dvfs:29.6f}")

# Print average dynamic power values in tabular format
print("\nAverage Dynamic Power (W) with and without DVFS per Core:")
print(tabulate(
    [(core_id, f"{average_dynamic_power_dvfs[core_id]:.6f}", f"{average_dynamic_power_no_dvfs[core_id]:.6f}") 
     for core_id in dynamic_power_dvfs],
    headers=["Core", "Average Power with DVFS (W)", "Average Power without DVFS (W)"],
    tablefmt="grid"
))

# Print the average total dynamic power
print("\nAverage Total Dynamic Power (W) across All Cores:")
print(f"With DVFS: {average_total_dynamic_power_dvfs:.6f} W")
print(f"Without DVFS: {average_total_dynamic_power_no_dvfs:.6f} W")

# Plot dynamic power for each core separately
for core_id in dynamic_power_dvfs:
    fig, ax = plt.subplots(figsize=(10, 6))

    # Plot dynamic power with and without DVFS for the current core
    ax.plot(time_dvfs, dynamic_power_dvfs[core_id], 'o-', label=f'Core {core_id} with DVFS')
    ax.plot(time_no_dvfs, dynamic_power_no_dvfs[core_id], 'x--', label=f'Core {core_id} without DVFS')

    ax.set_xlabel('Time (s)', fontsize=16)
    ax.set_ylabel('Dynamic Power (W)', fontsize=16)
    ax.set_title(f'Dynamic Power for Core {core_id}', fontsize=18)
    ax.grid(True)

    # Create an inset for zoomed-in view
    ax_inset = inset_axes(ax, width="32%", height="32%", loc='upper right')
    ax_inset.plot(time_dvfs, dynamic_power_dvfs[core_id], 'o-', color='tab:blue')
    ax_inset.plot(time_no_dvfs, dynamic_power_no_dvfs[core_id], 'x--', color='tab:orange')

    ax_inset.set_xlim(-0.01, 0.25)
    ax_inset.set_ylim(0, max(dynamic_power_dvfs[core_id]) + 0.05)
    ax_inset.set_xlabel('Time (s)', fontsize=11)
    ax_inset.set_ylabel('Dynamic Power (W)', fontsize=11)
    ax_inset.grid(True)

    ax.legend(loc='lower right', fontsize=12)
    plt.tight_layout()
    plt.show()
