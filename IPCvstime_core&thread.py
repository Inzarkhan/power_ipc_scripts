import os
import re
import matplotlib.pyplot as plt

# Define paths to data files for DVFS-enabled and DVFS-disabled scenarios
# path_dvfs_enabled = "/home/said/GEM5/ARM/gem5/output/mibench/telecom_adpcm_rawdaudiosmall2_L3_dvfsenable/stats.txt"
# path_dvfs_disabled = "/home/said/GEM5/ARM/gem5/output/mibench/telecom_adpcm_rawdaudiosmall2_L3_dvfsdisable/stats.txt"


path_dvfs_enabled = "/home/said/GEM5/ARM/gem5/output/mibench/basicmathlarge-L3_dvfsenable/stats.txt"
path_dvfs_disabled = "/home/said/GEM5/ARM/gem5/output/mibench/basicmathlarge3-L3_dvfsenable/stats.txt"
# Define CPU range
cpu_ids = range(3)  # CPUs 0, 1, and 2

# Regular expressions to capture IPC at core and thread levels
core_level_ipc_pattern = re.compile(r"system\.cpu_cluster\.cpus(\d+)\.ipc\s+([\d.]+)")
thread_level_ipc_pattern = re.compile(r"system\.cpu_cluster\.cpus(\d+)\.commitStats(\d+)\.ipc\s+([\d.]+)")

# Function to extract IPC data from log file
def extract_ipc_data(file_path):
    core_ipc_data = {f'cpu{i}': [] for i in cpu_ids}
    thread_ipc_data = {f'cpu{i}_thread{j}': [] for i in cpu_ids for j in range(2)}  # Assuming 2 threads per CPU

    with open(file_path, 'r') as file:
        for line in file:
            core_match = core_level_ipc_pattern.search(line)
            if core_match:
                cpu_id, ipc_value = int(core_match.group(1)), float(core_match.group(2))
                if f'cpu{cpu_id}' in core_ipc_data:
                    core_ipc_data[f'cpu{cpu_id}'].append(ipc_value)
            
            thread_match = thread_level_ipc_pattern.search(line)
            if thread_match:
                cpu_id, thread_id, ipc_value = int(thread_match.group(1)), int(thread_match.group(2)), float(thread_match.group(3))
                if f'cpu{cpu_id}_thread{thread_id}' in thread_ipc_data:
                    thread_ipc_data[f'cpu{cpu_id}_thread{thread_id}'].append(ipc_value)

    print("Core-level IPC data extracted:")
    for cpu_id in cpu_ids:
        print(f"cpu{cpu_id}: {core_ipc_data[f'cpu{cpu_id}']}")
    
    print("Thread-level IPC data extracted:")
    for cpu_id in cpu_ids:
        for thread_id in range(2):
            print(f"cpu{cpu_id}_thread{thread_id}: {thread_ipc_data[f'cpu{cpu_id}_thread{thread_id}']}")

    return core_ipc_data, thread_ipc_data

# Load data for both DVFS-enabled and DVFS-disabled cases
core_ipc_dvfs_enabled, thread_ipc_dvfs_enabled = extract_ipc_data(path_dvfs_enabled)
core_ipc_dvfs_disabled, thread_ipc_dvfs_disabled = extract_ipc_data(path_dvfs_disabled)

# Synchronize the lengths of IPC data and time steps
def synchronize_data_lengths(data_enabled, data_disabled):
    lengths = [len(data_enabled[key]) for key in data_enabled if data_enabled[key]] + \
              [len(data_disabled[key]) for key in data_disabled if data_disabled[key]]
    
    if not lengths:
        print("Error: No data available for synchronization.")
        return None, None, None

    min_len = min(lengths)

    for key in data_enabled:
        if data_enabled[key]:
            data_enabled[key] = data_enabled[key][:min_len]
    for key in data_disabled:
        if data_disabled[key]:
            data_disabled[key] = data_disabled[key][:min_len]

    time_steps = list(range(min_len))
    return data_enabled, data_disabled, time_steps

# Synchronize data lengths
core_ipc_dvfs_enabled, core_ipc_dvfs_disabled, core_time_steps = synchronize_data_lengths(core_ipc_dvfs_enabled, core_ipc_dvfs_disabled)
thread_ipc_dvfs_enabled, thread_ipc_dvfs_disabled, thread_time_steps = synchronize_data_lengths(thread_ipc_dvfs_enabled, thread_ipc_dvfs_disabled)

# Plot IPC data
def plot_ipc(data_enabled, data_disabled, time_steps, title):
    if not time_steps:
        print(f"Error: time_steps is empty for {title}. No data to plot.")
        return

    plt.figure(figsize=(14, 8))
    for key in data_enabled:
        if data_enabled[key] and data_disabled[key]:
            plt.plot(time_steps, data_enabled[key], label=f'{key} - DVFS Enabled', linestyle='-', marker='o')
            plt.plot(time_steps, data_disabled[key], label=f'{key} - DVFS Disabled', linestyle='--', marker='x')
        else:
            print(f"Warning: No data for {key}. Skipping this entry.")
    
    plt.xlabel("Time Steps")
    plt.ylabel("IPC")
    plt.title(title)
    plt.legend()
    plt.grid()
    plt.show()

# Generate plots
if core_time_steps:
    plot_ipc(core_ipc_dvfs_enabled, core_ipc_dvfs_disabled, core_time_steps, "Core Level IPC over Time (DVFS Enabled vs Disabled)")
else:
    print("Error: Unable to generate core-level plot due to lack of data.")

if thread_time_steps:
    plot_ipc(thread_ipc_dvfs_enabled, thread_ipc_dvfs_disabled, thread_time_steps, "Thread Level IPC over Time (DVFS Enabled vs Disabled)")
else:
    print("Error: Unable to generate thread-level plot due to lack of data.")