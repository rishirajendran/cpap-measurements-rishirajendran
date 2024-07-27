# imports
import json
from scipy.signal import find_peaks
import logging
import math
import matplotlib.pyplot as plt
# import numpy as np

# define globals
ro = 1.199  # kg/m^3
d1 = 0.015  # meters
d2 = 0.012  # meters


def get_pressure_data(file_name):
    """Read and store lines of data from input file

    The input file, consisting of several rows of data separated by commas,
    is read and processed. Each row is checked to ensure it has 7 numbers,
    and valid data rows are stored in a list and all valid rows are returned.

    Parameters
    ----------
    file_name : String
        Contains the name of the file to read.

    Returns
    -------
    data : list
        Contains rows of valid data from input file

    """
    data = []
    with open(file_name, "r") as file:
        next(file)
        for line in file:
            error_flag = False
            values = line.strip().split(',')

            if len(values) != 7:
                error_flag = True
                logging.error("Missing or additional values")
            else:
                for v in values:
                    try:
                        float_v = float(v)
                    except ValueError:
                        error_flag = True
                        logging.error("Non-numerical string found")
                        break
                    if math.isnan(float_v):
                        error_flag = True
                        logging.error("Element is NaN")
                        break

            if not error_flag:
                data.append(values)

    return data


def calc_flow(p1, p2):
    """Calculate flow rate based on input pressures

    Volumetric flow rate through a venturi tube can be calculated using
    the formula Q = 1000 * A1 * sqrt(2/ro * (p1-p2)/((A1/A2)^2 - 1)). The
    units for Q are L/sec.

    Parameters
    ----------
    p1 : float
    p2 : float

    Returns
    -------
    Q : float

    """
    A1 = math.pi * ((d1/2)**2)
    A2 = math.pi * ((d2/2)**2)
    numer = 2*(p1-p2)
    denom = ro * ((A1/A2) ** 2 - 1)
    Q = 1000 * A1 * math.sqrt(numer/denom)
    return Q


def get_flow_vs_time(pressure_data):
    """Get flow and time measurements from input pressure data

    A list of lists containing data from the input file is parsed to isolate
    the relevant pressures and time values. The inspiratory and expiratory
    pressures are compared and the larger one is used to calculate
    the volumetric flow rate in the venturi tube.

    Parameters
    ----------
    pressure_data : list

    Returns
    -------
    time : list
    flow : list

    """
    time = []
    flow = []
    for line in pressure_data:
        t = float(line[0])
        time.append(t)
        p2, p1_ins, p1_exp = convert_ADC_to_pressure([float(line[1]),
                                                     float(line[2]),
                                                     float(line[3])])

        if p1_ins >= p1_exp:
            f = calc_flow(p1_ins, p2)
        else:
            f = -1 * calc_flow(p1_exp, p2)

        flow.append(f)

    return time, flow


def convert_ADC_to_pressure(vals):
    """Convert ADC values into pressure readings.

    Pressure measurements from the input data are reported in ADC units and
    are converted to pressure readings with units cm-H2O using the formula,
    Pressure (cm-H2O) = [(25.4) / (14745 - 1638)] * (ADC_value - 1638), as
    given in the ADC spec sheet. Pressures of cm-H2O are then converted to Pa
    using the conversion rate 1 cm-H2O = 98.0665 Pa.

    Parameters
    ----------
    vals : list

    Returns
    -------
    pressures : list

    """
    pressures = []
    for v in vals:
        pressure = ((25.4) / (14745 - 1638)) * (v - 1638)  # cm-H2O
        pressure_pa = pressure * 98.0665  # Pa
        pressures.append(pressure_pa)
    return pressures


def get_breaths(flow):
    """Detect breath peaks from flow data

    A breath can be identified by a positive peak in volumetric flow
    (the inhalation) followed by a return to zero or negative flow
    (the exhalation).

    Parameters
    ----------
    flow : list

    Returns
    -------
    breath_indices : list

    """
    peak_indices, _ = find_peaks(flow, height=0.1)

    breath_indices = []

    if (len(peak_indices) > 0):
        for i in range(len(peak_indices) - 1):
            for j in range(peak_indices[i], peak_indices[i+1]):
                if flow[j] <= 0:
                    breath_indices.append(peak_indices[i])
                    break

        # Check if data returns to 0 or negative after the last peak
        for j in range(peak_indices[-1], len(flow)):
            if flow[j] <= 0:
                breath_indices.append(peak_indices[-1])
                break

    return breath_indices


def count_apneas(breath_times):
    """Count number of apnea events between breath times

    An apnea event occurs when the time elapsed between breaths
    (the time between observed peaks) is more than 10 seconds.

    Parameters
    ----------
    breath_times : list

    Returns
    -------
    apnea_count : int

    """
    apnea_count = 0
    for i in range(len(breath_times)-1):
        if breath_times[i+1] - breath_times[i] > 10:
            apnea_count += 1
    return apnea_count


def calc_leakage(time, flow):
    """Calculate the total amount of mask leakage observed in the data (L)

    The leakage is calculated by determining the total net flow through
    Venturi 1. If more flow is observed going to the patient than coming
    back from the patient, the difference is volume lost due to leaks in
    the mask seal.

    Parameters
    ----------
    time : list
    flow : list

    Returns
    -------
    leakage : float

    """
    leakage = 0
    for i in range(len(time)-1):
        flow_diff = flow[i+1] - flow[i]
        time_diff = time[i+1] - time[i]
        leakage += flow_diff * time_diff

    if (leakage < 0):
        logging.warning("Leakage is negative")

    return leakage


def analyze_flow(time, flow):
    """Analyze flow rate to calculate desired metrics

    Flow rate over time data is analyzed to calculate the total duration of
    the raw data (s), the number of breaths, the average breathing rate (bpm),
    the times at which each breath occurs (s), the number of apnea events,
    and the total amount of leakage from the mask (L).

    Parameters
    ----------
    time : list
    flow : list

    Returns
    -------
    metrics : dict

    """
    duration = time[-1] - time[0]

    breath_indices = get_breaths(flow)

    breaths = len(breath_indices)
    breath_times = [time[i] for i in breath_indices]
    apnea_count = count_apneas(breath_times)
    breath_rate_bpm = (breaths/duration) * 60
    leakage = calc_leakage(time, flow)

    metrics = {"duration": duration,
               "breaths": breaths,
               "breath_rate_bpm": breath_rate_bpm,
               "breath_times": breath_times,
               "apnea_count": apnea_count,
               "leakage": leakage}

    return metrics


def output_file(file_name, metrics):
    """Output metrics dictionary to .json file.

    Populate .json file with contents of metrics dictionary.

    Parameters
    ----------
    file_name : String
    metrics : dict

    Returns
    -------
    f_name : String
    """
    f_name = file_name[:-4]
    out_file = open(f"{f_name}.json", "w")
    json.dump(metrics, out_file)
    out_file.close()
    return f_name


def main():
    logging.basicConfig(filename="pressure_analysis.log", filemode="w",
                        level=logging.INFO)

    file_name = "patient_01.txt"
    path_name = "sample_data\\" + file_name

    logging.info("Starting data analysis. Input file name is: " + file_name)

    pressure_data = get_pressure_data(path_name)

    time, flow = get_flow_vs_time(pressure_data)

    metrics = analyze_flow(time, flow)

    json_name = output_file(file_name, metrics)

    logging.info("Ended data analysis. Output file name is: " + json_name)


if __name__ == "__main__":
    main()
