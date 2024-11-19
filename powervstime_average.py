import re
import matplotlib.pyplot as plt

# Initialize lists to store power and time values
dynamic_power = []
static_power = []
time = None

# Read the text file
with open("/home/said/Desktop/Programs/ocean_non_contig/core_b2l3p8/1800MHz0.98100/stats.txt", "r") as file:
    data = file.read()

# Extract dynamic power, static power, and time values using regular expressions
dynamic_power_matches = re.findall(r'dynamicPower\s+(\d+\.\d+)', data)
static_power_matches = re.findall(r'staticPower\s+(\d+\.\d+)', data)
time_match = re.search(r'simSeconds\s+(\d+\.\d+)', data)

# Convert extracted values to floats
dynamic_power = [float(power) for power in dynamic_power_matches]
static_power = [float(power) for power in static_power_matches]
time = float(time_match.group(1)) * 1000  # Convert time to milliseconds

# Determine the number of measurements
num_measurements = min(len(dynamic_power), len(static_power))

# Define the time interval for averaging (in milliseconds)
time_interval = 1  # Set the time interval to 1 millisecond

# Calculate the number of bins
num_bins = int(time / time_interval)

# Initialize lists to store averaged power values
averaged_dynamic_power = [0] * num_bins
averaged_static_power = [0] * num_bins

# Initialize variables to track the number of measurements in each bin
num_measurements_in_bin = [0] * num_bins

# Aggregate power values into bins
for i in range(num_measurements):
    bin_index = int(i * num_bins / num_measurements)
    averaged_dynamic_power[bin_index] += dynamic_power[i]
    averaged_static_power[bin_index] += static_power[i]
    num_measurements_in_bin[bin_index] += 1

# Calculate the average power values
averaged_dynamic_power = [power / count if count != 0 else 0 for power, count in zip(averaged_dynamic_power, num_measurements_in_bin)]
averaged_static_power = [power / count if count != 0 else 0 for power, count in zip(averaged_static_power, num_measurements_in_bin)]

# Create an array of time values for each bin
time_values = [i * time_interval for i in range(num_bins)]

# Plot the data
plt.plot(time_values, averaged_dynamic_power, label='Dynamic Power')
plt.plot(time_values, averaged_static_power, label='Static Power')
plt.xlabel('Time (Milliseconds)')
plt.ylabel('Power (Watts)')
plt.title('Average Power vs Time')
plt.legend()
plt.grid(True)
plt.show()
