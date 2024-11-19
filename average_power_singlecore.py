import re
import matplotlib.pyplot as plt
from tabulate import tabulate

# Function to read and extract power data from a 'stats.txt' file for a single core
def extract_dynamic_power_data(file_path):
    with open(file_path, 'r') as file:
        stats_data = file.readlines()

    dynamic_power_data = []
    time_seconds = []

    for line in stats_data:
        if line.startswith("simSeconds"):
            time_seconds.append(float(re.search(r'\d+\.\d+', line).group()))
        elif "system.cpu_cluster.cpus.power_model.dynamicPower" in line:
            power = float(re.search(r'(\d+\.\d+)', line).group())
            dynamic_power_data.append(power)

    # Ensure both lists have the same length
    min_length = min(len(time_seconds), len(dynamic_power_data))
    time_seconds = time_seconds[:min_length]
    dynamic_power_data = dynamic_power_data[:min_length]

    return time_seconds, dynamic_power_data

# File paths for the two 'stats.txt' files
file_path_dvfs = '/home/said/GEM5/ARM/gem5/output/mibench/telecomFFT4_w4_s32768_core1_L3_dvfsenable/stats.txt'
file_path_no_dvfs = '/home/said/GEM5/ARM/gem5/output/mibench/telecomFFT4_w4_s32768_core1_L3_dvfsdisable/stats.txt'

# Extract data from both files
time_dvfs, dynamic_power_dvfs = extract_dynamic_power_data(file_path_dvfs)
time_no_dvfs, dynamic_power_no_dvfs = extract_dynamic_power_data(file_path_no_dvfs)

# Find the common minimum length between time arrays and power data
min_length = min(len(time_dvfs), len(time_no_dvfs))

# Trim both time and power data to the same minimum length
time_dvfs = time_dvfs[:min_length]
dynamic_power_dvfs = dynamic_power_dvfs[:min_length]
dynamic_power_no_dvfs = dynamic_power_no_dvfs[:min_length]

# Calculate total average power consumption over the entire time period
total_average_power_dvfs = sum(dynamic_power_dvfs) / len(dynamic_power_dvfs)
total_average_power_no_dvfs = sum(dynamic_power_no_dvfs) / len(dynamic_power_no_dvfs)

# Prepare table for comparison
table_data = []
headers = ["Time (s)", "Dynamic Power (W) with DVFS", "Dynamic Power (W) without DVFS"]
for i in range(min_length):
    row = [f"{time_dvfs[i]:.6f}", 
           f"{dynamic_power_dvfs[i]:.6f}", 
           f"{dynamic_power_no_dvfs[i]:.6f}"]
    table_data.append(row)

print(tabulate(table_data, headers=headers, tablefmt="grid"))

# Print total average power consumption
print(f"\nTotal Average Power Consumption:")
print(f"  With DVFS: {total_average_power_dvfs:.6f} W")
print(f"  Without DVFS: {total_average_power_no_dvfs:.6f} W")

# Plot dynamic power for both states
plt.figure(figsize=(10, 6))

# Use only lines for the plots, no markers
plt.plot(time_dvfs, dynamic_power_dvfs, '-', label='Dynamic Power with DVFS', color='blue', linewidth=2)
plt.plot(time_no_dvfs, dynamic_power_no_dvfs, '--', label='Dynamic Power without DVFS', color='red', linewidth=2)

# Add labels, title, and legend
plt.xlabel('Time (s)', fontsize=14)
plt.ylabel('Dynamic Power (W)', fontsize=14)
plt.title('Dynamic Power Consumption for Single Core', fontsize=16)
plt.grid(True)
plt.legend(fontsize=12)

# Display the plot
plt.tight_layout()
plt.show()
