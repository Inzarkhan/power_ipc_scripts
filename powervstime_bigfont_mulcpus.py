import re
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from tabulate import tabulate

# Read the 'stats.txt' file
file_path = '/home/said/GEM5/ARM/gem5/output/mibench/basicmathlarge-L3_dvfsdisable/stats.txt'
with open(file_path, 'r') as file:
    stats_data = file.readlines()

# Extract relevant data
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

# Print table of values
table_data = []
headers = ["Time (s)"] + [f"CPU {cpu_id} Dynamic Power (W)" for cpu_id in dynamic_power_data]
for i in range(min_length):
    row = [f"{time_seconds[i]:.6f}"]
    for cpu_id in dynamic_power_data:
        row.append(f"{dynamic_power_data[cpu_id][i]:.6f}")
    table_data.append(row)

print(tabulate(table_data, headers=headers, tablefmt="grid"))

# Plot dynamic power vs time for all CPUs
fig, ax = plt.subplots(figsize=(10, 6))

# Colors for each CPU plot
colors = plt.cm.tab10(range(len(dynamic_power_data)))

# Main plot for dynamic power
for idx, (cpu_id, power_values) in enumerate(dynamic_power_data.items()):
    ax.plot(time_seconds, power_values, 'o-', label=f'CPU {cpu_id} Dynamic Power', color=colors[idx])

# Increase the font size of labels and title
ax.set_xlabel('Time (s)', fontsize=16)
ax.set_ylabel('Dynamic Power (W)', fontsize=16)
ax.grid(True)

# Create an inset for the zoomed-in view
ax_inset = inset_axes(ax, width="32%", height="32%", loc='upper right')  # Adjust the location as needed
for idx, (cpu_id, power_values) in enumerate(dynamic_power_data.items()):
    ax_inset.plot(time_seconds, power_values, 'o-', label=f'CPU {cpu_id} Dynamic Power', color=colors[idx])

# Zooming in on a specific time range (e.g., 0 to 0.2 seconds)
ax_inset.set_xlim(-0.01, 0.25)
ax_inset.set_ylim(0, max(max(power) for power in dynamic_power_data.values()) + 0.05)  # Adjust based on your data

# Set labels for the inset
ax_inset.set_xlabel('Time (s)', fontsize=11)
ax_inset.set_ylabel('Dynamic Power (W)', fontsize=11)
ax_inset.grid(True)

# Add the legend, placing it just below the zoomed-in (inset) plot
ax_inset.legend(loc='lower center', bbox_to_anchor=(0.19, -2.0), fontsize=11, ncol=2)

# Show the plot
plt.tight_layout()
plt.show()
