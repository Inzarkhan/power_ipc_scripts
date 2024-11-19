import re
import matplotlib.pyplot as plt
from tabulate import tabulate

# Read the 'stats.txt' file
file_path = '/home/said/Desktop/stats.txt'
with open(file_path, 'r') as file:
    stats_data = file.readlines()

# Extract relevant data
dynamic_power_data = {}
ipc_data = {}
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
    elif "system.cpu_cluster.cpus" in line and "ipc" in line:
        cpu_match = re.search(r'system\.cpu_cluster\.cpus(\d+)\.ipc', line)
        if cpu_match:
            cpu_id = cpu_match.group(1)
            ipc_value = float(re.search(r'(\d+\.\d+)', line).group())
            if cpu_id not in ipc_data:
                ipc_data[cpu_id] = []
            ipc_data[cpu_id].append(ipc_value)

# Ensure all lists have the same length
min_length = min(len(time_seconds), *[len(powers) for powers in dynamic_power_data.values()],
                 *[len(ipcs) for ipcs in ipc_data.values()])

time_seconds = time_seconds[:min_length]
for cpu_id in dynamic_power_data:
    dynamic_power_data[cpu_id] = dynamic_power_data[cpu_id][:min_length]
for cpu_id in ipc_data:
    ipc_data[cpu_id] = ipc_data[cpu_id][:min_length]

# Print table of power and IPC values per CPU
table_data = []
headers = ["Time (s)"] + [f"CPU {cpu_id} Power (W)" for cpu_id in dynamic_power_data] + \
           [f"CPU {cpu_id} IPC" for cpu_id in ipc_data]
for i in range(min_length):
    row = [f"{time_seconds[i]:.6f}"]
    for cpu_id in dynamic_power_data:
        row.append(f"{dynamic_power_data[cpu_id][i]:.6f}")
    for cpu_id in ipc_data:
        row.append(f"{ipc_data[cpu_id][i]:.6f}")
    table_data.append(row)

print(tabulate(table_data, headers=headers, tablefmt="grid"))

# Plot Power vs IPC for each CPU with different colors
plt.figure(figsize=(10, 6))

colors = plt.cm.get_cmap('tab10', len(dynamic_power_data))  # Use a color map to get different colors

for idx, cpu_id in enumerate(dynamic_power_data):
    # Plot IPC vs Power for each CPU core without averaging
    plt.plot(ipc_data[cpu_id], dynamic_power_data[cpu_id], 'o-', label=f'CPU {cpu_id}', color=colors(idx))

# Increase the font size of labels and title
plt.xlabel('IPC (Instructions Per Cycle)', fontsize=16)
plt.ylabel('Dynamic Power (W)', fontsize=16)
plt.title('Power vs IPC for Each CPU', fontsize=18)
plt.grid(True)

# Add a legend to differentiate between the CPUs
plt.legend(fontsize=12, title="CPU Cores")

# Show the plot
plt.tight_layout()
plt.show()
