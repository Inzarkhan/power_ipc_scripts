import re
import matplotlib.pyplot as plt
from tabulate import tabulate

# Read the 'stats.txt' file
file_path = '/home/said/GEM5/ARM/gem5/output/Splash/DVFS_nonpinning_powermodel_raspberrypi4_barnes_8p_twice_DVFSdenable/stats.txt'
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

# Calculate total dynamic power for each time step
total_dynamic_power_per_step = [sum(powers) for powers in zip(*dynamic_power_data.values())]

# Calculate total dynamic power
total_dynamic_power = sum(total_dynamic_power_per_step)

# Calculate average total dynamic power
average_total_dynamic_power = total_dynamic_power / len(total_dynamic_power_per_step)

# Print total dynamic power
print(f"Total Dynamic Power: {total_dynamic_power:.6f} W")

# Print average total dynamic power
print(f"Average Total Dynamic Power: {average_total_dynamic_power:.6f} W")

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
plt.figure(figsize=(10, 6))

for cpu_id, power_values in dynamic_power_data.items():
    plt.plot(time_seconds, power_values, '-', label=f'CPU {cpu_id} Dynamic Power')

plt.xlabel('Time (s)')
plt.ylabel('Power (Watt)')
plt.title('Dynamic Power vs Time for All CPUs')
plt.legend()
plt.grid(True)
plt.show()