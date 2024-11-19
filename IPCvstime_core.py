import os
import re
import matplotlib.pyplot as plt

# Define paths to data files for DVFS-enabled and DVFS-disabled scenarios
path_dvfs_enabled = "/home/said/GEM5/ARM/gem5/output/mibench/networkdijkstralarge_L3_dvfsenable/stats.txt"
path_dvfs_disabled = "/home/said/GEM5/ARM/gem5/output/mibench/networkdijkstralarge_L3_dvfsdisable/stats.txt"

# Define CPU range (adjust according to your setup)
cpu_ids = range(3)  # Changed to range(3) as there's no data for CPU 3

# Regular expression to capture IPC at core level
core_level_ipc_pattern = re.compile(r"system\.cpu_cluster\.cpus(\d+)\.ipc\s+([\d.]+)")

# Function to extract IPC data from log file
def extract_ipc_data(file_path):
    core_ipc_data = {f'cpu{i}': [] for i in cpu_ids}

    # Read log file line-by-line
    with open(file_path, 'r') as file:
        for line in file:
            # Check for core-level IPC
            core_match = core_level_ipc_pattern.search(line)
            if core_match:
                cpu_id, ipc_value = int(core_match.group(1)), float(core_match.group(2))
                if f'cpu{cpu_id}' in core_ipc_data:
                    core_ipc_data[f'cpu{cpu_id}'].append(ipc_value)

    # Debugging: Print the extracted data
    print("Core-level IPC data extracted:")
    for cpu_id in cpu_ids:
        print(f"cpu{cpu_id}: {core_ipc_data[f'cpu{cpu_id}']}")

    return core_ipc_data

# Load data for both DVFS-enabled and DVFS-disabled cases
core_ipc_dvfs_enabled = extract_ipc_data(path_dvfs_enabled)
core_ipc_dvfs_disabled = extract_ipc_data(path_dvfs_disabled)

# Synchronize the lengths of IPC data and time steps
def synchronize_data_lengths(core_ipc_enabled, core_ipc_disabled):
    # Get the minimum length across all non-empty core IPC lists
    lengths_enabled = [len(core_ipc_enabled[f'cpu{i}']) for i in cpu_ids if core_ipc_enabled[f'cpu{i}']]
    lengths_disabled = [len(core_ipc_disabled[f'cpu{i}']) for i in cpu_ids if core_ipc_disabled[f'cpu{i}']]
    
    if not lengths_enabled or not lengths_disabled:
        print("Error: No data available for synchronization.")
        return None, None, None

    min_len = min(min(lengths_enabled), min(lengths_disabled))

    # Truncate the IPC lists to the minimum length
    for i in cpu_ids:
        if core_ipc_enabled[f'cpu{i}']:
            core_ipc_enabled[f'cpu{i}'] = core_ipc_enabled[f'cpu{i}'][:min_len]
        if core_ipc_disabled[f'cpu{i}']:
            core_ipc_disabled[f'cpu{i}'] = core_ipc_disabled[f'cpu{i}'][:min_len]

    # Create a time_steps list based on the minimum length
    time_steps = list(range(min_len))
    return core_ipc_enabled, core_ipc_disabled, time_steps

# Synchronize data lengths for core-level IPC
core_ipc_dvfs_enabled, core_ipc_dvfs_disabled, time_steps = synchronize_data_lengths(core_ipc_dvfs_enabled, core_ipc_dvfs_disabled)

# Plot core-level IPC on a single figure
def plot_core_ipc(core_ipc_enabled, core_ipc_disabled):
    if not time_steps:
        print("Error: time_steps is empty. No data to plot.")
        return

    plt.figure(figsize=(14, 8))
    for cpu_id in cpu_ids:
        if core_ipc_enabled[f'cpu{cpu_id}'] and core_ipc_disabled[f'cpu{cpu_id}']:
            plt.plot(time_steps, core_ipc_enabled[f'cpu{cpu_id}'], label=f'CPU {cpu_id} - DVFS Enabled', linestyle='-', marker='o')
            plt.plot(time_steps, core_ipc_disabled[f'cpu{cpu_id}'], label=f'CPU {cpu_id} - DVFS Disabled', linestyle='--', marker='x')
        else:
            print(f"Warning: No data for CPU {cpu_id}. Skipping this CPU.")
    
    plt.xlabel("Time Steps")
    plt.ylabel("IPC")
    plt.title("Core Level IPC over Time (DVFS Enabled vs Disabled)")
    plt.legend()
    plt.grid()
    plt.show()

# Generate plot
if time_steps:
    plot_core_ipc(core_ipc_dvfs_enabled, core_ipc_dvfs_disabled)
else:
    print("Error: Unable to generate plot due to lack of data.")