import re
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from tabulate import tabulate

# Read the 'stats.txt' file
file_path = '/home/said/GEM5/ARM/gem5/output/mibench/basicmathlarge-L3_dvfsdisable/stats.txt'
with open(file_path, 'r') as file:
    stats_data = file.readlines()

# Extract relevant data
ipc_data = {}
time_seconds = []

for line in stats_data:
    # Extract simulation time
    if line.startswith("simSeconds"):
        time_seconds.append(float(re.search(r'\d+\.\d+', line).group()))
    
    # Extract IPC values for each CPU
    elif "system.cpu_cluster.cpus" in line and "ipc" in line:
        cpu_match = re.search(r'system\.cpu_cluster\.cpus(\d+)\.ipc', line)
        if cpu_match:
            cpu_id = cpu_match.group(1)
            ipc_value = float(re.search(r'(\d+\.\d+)', line).group())
            if cpu_id not in ipc_data:
                ipc_data[cpu_id] = []
                
            ipc_data[cpu_id].append(ipc_value)

# Ensure all lists have the same length
min_length = min(len(time_seconds), *[len(ipcs) for ipcs in ipc_data.values()])
time_seconds = time_seconds[:min_length]
for cpu_id in ipc_data:
    ipc_data[cpu_id] = ipc_data[cpu_id][:min_length]

# Print table of values
table_data = []
headers = ["Time (s)"] + [f"CPU {cpu_id} IPC" for cpu_id in ipc_data]
for i in range(min_length):
    row = [f"{time_seconds[i]:.6f}"]
    for cpu_id in ipc_data:
        row.append(f"{ipc_data[cpu_id][i]:.6f}")
    table_data.append(row)

print(tabulate(table_data, headers=headers, tablefmt="grid"))

# Plot IPC vs time for all CPUs
fig, ax = plt.subplots(figsize=(10, 6))

# Colors for each CPU plot
colors = plt.cm.tab10(range(len(ipc_data)))

# Main plot for IPC
for idx, (cpu_id, ipc_values) in enumerate(ipc_data.items()):
    ax.plot(time_seconds, ipc_values, 'o-', label=f'CPU {cpu_id} IPC', color=colors[idx])

# Increase the font size of labels and title
ax.set_xlabel('Time (s)', fontsize=16)
ax.set_ylabel('IPC (Instructions Per Cycle)', fontsize=16)
ax.grid(True)

# Create an inset for the zoomed-in view
ax_inset = inset_axes(ax, width="35%", height="35%", loc='upper right')  # Adjust the location as needed
for idx, (cpu_id, ipc_values) in enumerate(ipc_data.items()):
    ax_inset.plot(time_seconds, ipc_values, 'o-', label=f'CPU {cpu_id} IPC', color=colors[idx])

# Zooming in on the area from 0 to 0.2 seconds
ax_inset.set_xlim(-0.01, 0.25)
ax_inset.set_ylim(0, max(max(ipc) for ipc in ipc_data.values()) + 0.05)  # Adjust based on your data

# Set labels for the inset
ax_inset.set_xlabel('Time (s)', fontsize=10)
ax_inset.set_ylabel('IPC', fontsize=10)
ax_inset.grid(True)

# Add the legend, placing it just below the zoomed-in (inset) plot
ax_inset.legend(loc='lower center', bbox_to_anchor=(0.45, -0.75), fontsize=13, ncol=2)  # Adjusted to appear below the inset

# Show the plot
plt.tight_layout()
plt.show()
