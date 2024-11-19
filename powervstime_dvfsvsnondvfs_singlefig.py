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
file_path_dvfs = '/home/said/GEM5/ARM/gem5/output/mibench/networkdijkstralarge3_L3_dvffdisable/stats.txt'
file_path_no_dvfs = '/home/said/GEM5/ARM/gem5/output/mibench/networkdijkstralarge_L3_dvfsdisable/stats.txt'

# Extract data from both files
time_dvfs, dynamic_power_dvfs = extract_dynamic_power_data(file_path_dvfs)
time_no_dvfs, dynamic_power_no_dvfs = extract_dynamic_power_data(file_path_no_dvfs)

# Find the common minimum length between time arrays and power data
min_length = min(len(time_dvfs), len(time_no_dvfs))

# Trim both time and power data to the same minimum length
time_dvfs = time_dvfs[:min_length]
time_no_dvfs = time_no_dvfs[:min_length]

for core_id in dynamic_power_dvfs:
    dynamic_power_dvfs[core_id] = dynamic_power_dvfs[core_id][:min_length]
    dynamic_power_no_dvfs[core_id] = dynamic_power_no_dvfs[core_id][:min_length]

# Print table of values for comparison
table_data = []
headers = ["Time (s)", "Core", "Dynamic Power (W) with DVFS", "Dynamic Power (W) without DVFS"]
for core_id in dynamic_power_dvfs:
    for i in range(min_length):
        row = [f"{time_dvfs[i]:.6f}", f"Core {core_id}", 
               f"{dynamic_power_dvfs[core_id][i]:.6f}", 
               f"{dynamic_power_no_dvfs[core_id][i]:.6f}"]
        table_data.append(row)

print(tabulate(table_data, headers=headers, tablefmt="grid"))

# Plot dynamic power for cores from both stats.txt files
fig, ax = plt.subplots(figsize=(10, 6))

# Colors for each core plot
colors = plt.cm.tab10(range(len(dynamic_power_dvfs)))

# Plot dynamic power with and without DVFS for each core
for idx, (core_id, power_values_dvfs) in enumerate(dynamic_power_dvfs.items()):
    power_values_no_dvfs = dynamic_power_no_dvfs[core_id]
    
    # Plot for DVFS enabled
    ax.plot(time_dvfs, power_values_dvfs, 'o-', label=f'Core {core_id} with DVFS', color=colors[idx])
    
    # Plot for DVFS disabled
    ax.plot(time_no_dvfs, power_values_no_dvfs, 'x--', label=f'Core {core_id} without DVFS', color=colors[idx])

# Increase the font size of labels and title
ax.set_xlabel('Time (s)', fontsize=16)
ax.set_ylabel('Dynamic Power (W)', fontsize=16)
ax.grid(True)

# Create an inset for the zoomed-in view
ax_inset = inset_axes(ax, width="32%", height="32%", loc='upper right')  # Adjust the location as needed
for idx, (core_id, power_values_dvfs) in enumerate(dynamic_power_dvfs.items()):
    power_values_no_dvfs = dynamic_power_no_dvfs[core_id]
    
    # Plot for DVFS enabled
    ax_inset.plot(time_dvfs, power_values_dvfs, 'o-', color=colors[idx])
    
    # Plot for DVFS disabled
    ax_inset.plot(time_no_dvfs, power_values_no_dvfs, 'x--', color=colors[idx])

# Zooming in on a specific time range (e.g., 0 to 0.2 seconds)
ax_inset.set_xlim(-0.01, 0.25)
ax_inset.set_ylim(0, max(max(power) for power in dynamic_power_dvfs.values()) + 0.05)  # Adjust based on your data

# Set labels for the inset
ax_inset.set_xlabel('Time (s)', fontsize=11)
ax_inset.set_ylabel('Dynamic Power (W)', fontsize=11)
ax_inset.grid(True)

# Add the legend in the bottom-right corner
ax.legend(loc='lower right', fontsize=12)

# Show the plot
plt.tight_layout()
plt.show()
