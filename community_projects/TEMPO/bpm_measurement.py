import time
import board
import busio
import adafruit_ads1x15.ads1015 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import numpy as np
from scipy.signal import butter, filtfilt
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Configuration parameters
SAMPLE_RATE = 10   # Samples per second
WINDOW_SIZE = 2    # Seconds of data for analysis
THRESHOLD = 0.6    # adjust threshold for detecting peaks (depends on signal amplitude)
INPUT_GAIN = 2/3
FILTER_SIZE = SAMPLE_RATE * 1

#Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
adc = ADS.ADS1015(i2c)
adc.gain = INPUT_GAIN  # Adjust gain based on your ADC input voltage range
 
# Create single-ended input on channel 0
channel = AnalogIn(adc, ADS.P0)
 
# Create differential input between channel 0 and 1
#chan = AnalogIn(ads, ADS.P0, ADS.P1)

##################
#### basic code ##
##################
#print("{:>5}\t{:>5}".format('raw', 'v'))
 
#while True:
#    print("{:>5}\t{:>5.3f}".format(channel.value, channel.voltage))
#    time.sleep(0.5)


# fig, ax = plt.subplots()
# x = [1]
# y = [1.6]
# graph = ax.plot(x,y,color = 'b')[0]

# def update(frame):
#     global graph
#     x.append(x[-1]+1)
#     y.append(frame)

#     graph.set_xdata(x)
#     graph.set_ydata(y)
#     plt.xlim(x[0],x[-1])
#     plt.ylim(0,3.3)

# anim = FuncAnimation(fig,update,frames=[1.6])

def moving_average(data, window_size):
    return np.convolve(data, np.ones(window_size) / window_size, mode = 'valid')

def new_plot_data(data_1, data_2):       
    # Create Plot

    fig, ax1 = plt.subplots() 
    
    ax1.set_xlabel('X-axis') 
    ax1.set_ylabel('Voltage', color = 'red') 
    ax1.plot(data_1, color = 'red') 
    ax1.tick_params(axis ='y', labelcolor = 'red') 
    
    # Adding Twin Axes

    ax2 = ax1.twinx() 
    
    ax2.set_ylabel('BPM', color = 'blue') 
    ax2.plot(data_2, color = 'blue') 
    ax2.tick_params(axis ='y', labelcolor = 'blue') 
    
    # Show plot
    plt.show()


def plot_data(data1, data2):
    """Function to plot the raw data."""
    plt.plot(data1)
    plt.plot(data2)
    plt.title("Raw Signal from PulseSensor")
    plt.xlabel("Time (samples)")
    plt.ylabel("Voltage (V)")
    plt.show(block=True)
    # anim = FuncAnimation(fig,update,frames=data)
    # plt.show(block=False)

def butter_lowpass(cutoff, fs, order=4):
    nyquist = 0.5 * fs
    normal_cutoff = cutoff / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=4):
    b, a = butter_lowpass(cutoff, fs, order)
    y = filtfilt(b, a, data)
    return y

def calculate_bpm(raw_data, sample_rate):
    """Calculate BPM from peak intervals in the data."""
    peaks = []
    data = moving_average(raw_data, FILTER_SIZE)

    # Apply low-pass filtering to smooth the signal
    #filtered_data = butter_lowpass_filter(data, cutoff=2.0, fs=SAMPLE_RATE)
    
    # Adaptive threshold based on signal range
    #signal_range = max(filtered_data) - min(filtered_data)
    #adaptive_threshold = min(filtered_data) + 0.5 * signal_range

    data = raw_data
    adaptive_threshold = THRESHOLD
    agc = np.mean(data)
    for i in range(len(data)):
        data[i] = data[i] * 1.6 / agc
    signal_range = max(data)-min(data)
    adaptive_threshold = min(data) + 0.5 * signal_range
    for i in range(1, len(data) - 1):
        if data[i - 1] < data[i] > data[i + 1] and data[i] > adaptive_threshold and ((data[i]-data[i-1]) > 0.2 or (data[i]-data[i+1])>0.2) :
            peaks.append(i)


    # Calculate intervals (in seconds) between peaks
    intervals = np.diff(peaks) / sample_rate
    if len(intervals) > 0:
        avg_interval = np.mean(intervals)
        bpm = 60 / avg_interval
        return bpm
    else:
        return 0  # Return 0 if no peaks detected

def calc_median_bpm(bpm_vector):
    bpm_vec = np.array(bpm_vector)
    bpm_vec = bpm_vec[bpm_vec > 60]
    bpm_vec = bpm_vec[bpm_vec < 150]
    return np.median(bpm_vec)


def get_bpm():
    print("Starting Pulse Sensor BPM measurement...")
    data = []
    start_time = time.time()
    plot_data_vec = []
    plot_bpm_vec = []

    while True:
        try:
            # Read value from ADC
            raw_value = channel.voltage  # Get voltage value
            data.append(raw_value)

            # Maintain rolling window of data
            if len(data) == SAMPLE_RATE * WINDOW_SIZE + 1:
                plot_data_vec.append(data.pop(0))
                plot_bpm_vec.append(bpm)

            # Calculate BPM every second
            if time.time() - start_time >= 1:
                if len(data) == WINDOW_SIZE * SAMPLE_RATE :
                    bpm = calculate_bpm(data, SAMPLE_RATE)
                    print(f"BPM: {bpm:.2f}")
                    start_time = time.time()


            if len(plot_data_vec) == SAMPLE_RATE * 20:
                # Plot the data periodically (e.g., every second)
                new_plot_data(plot_data_vec, plot_bpm_vec)  # Plot the raw data over the past second
                median_bpm = calc_median_bpm(plot_bpm_vec)
                print(f'median bpm: {median_bpm}')
                # Compute the FFT of the signal
                plot_data_vec = np.array(plot_data_vec)
                plot_data_vec = plot_data_vec - np.mean(plot_data_vec)
                fft_signal = np.fft.fft(plot_data_vec)
                frequencies = np.fft.fftfreq(len(plot_data_vec), 1/SAMPLE_RATE)
                fft_magnitude = np.abs(fft_signal)[:len(plot_data_vec)//2]
                max_magnitude_index = 6
                for i in range(6, 20):
                    if (fft_magnitude[max_magnitude_index] < fft_magnitude[i]):
                        max_magnitude_index = i
                calc_bpm = 60 / frequencies[i]
                print(f'frequency: {calc_bpm}')
                #break
                return median_bpm

            # Small delay to match sample rate
            time.sleep(1 / SAMPLE_RATE)
        except KeyboardInterrupt:
            print("Exiting...")
            break

def main():
    return get_bpm()

if __name__ == "__main__":
    main()
