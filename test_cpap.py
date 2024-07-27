import pytest


@pytest.mark.parametrize("input, expected", [
    ([5, 10, 15, 100, 37, 63, 75], []),
    ([5, 10, -10, 7], [1]),
    ([5, 10, 3, 20, -10, 7], [3]),
    ([0, 1, 0], [1]),
    ([5, 10, -10, -8, -20, 7], [1]),
    ([5, 10, 0, -5, -10], [1]),
    ([0, 5, 0, -5, 10], [1]),
    ([10, 5, 0, -5, -10], []),
    ([10, 5, -5, 1, -10], [3]),
    ([0, 0, 0, 0, 0], []),
    ])
def test_get_breaths(input, expected):
    from cpap import get_breaths
    answer = get_breaths(input)
    assert answer == expected


@pytest.mark.parametrize("input1, input2, expected", [
    (0, 0, 0),
    (10, 10, 0),
    (20, 10, 0.601),
    ])
def test_calc_flow(input1, input2, expected):
    from cpap import calc_flow
    answer = round(calc_flow(input1, input2), 3)
    assert answer == expected


@pytest.mark.parametrize("input, expected_time, expected_flow", [
    ([[0.0, 5018, 1638, 5039],
      [1.0, 5051, 1638, 5071],
      [2.0, 5014, 1638, 5033]], [0.0, 1.0, 2.0], [-0.380, -0.371, -0.361]),
    ])
def test_get_flow_vs_time(input, expected_time, expected_flow):
    from cpap import get_flow_vs_time
    time, flow = get_flow_vs_time(input)
    rounded_flow = [round(x, 3) for x in flow]
    assert time == expected_time
    assert rounded_flow == expected_flow


@pytest.mark.parametrize("input, expected", [
    ([0], [-311.290]),
    ([0, 0], [-311.290, -311.290]),
    ([1000, 2000, 3000, 4000], [-121.247, 68.795, 258.838, 448.881]),
    ])
def test_convert_ADC_to_pressure(input, expected):
    from cpap import convert_ADC_to_pressure
    answer = convert_ADC_to_pressure(input)
    rounded_answer = [round(x, 3) for x in answer]
    assert rounded_answer == expected


@pytest.mark.parametrize("input, expected", [
    ([0, 0, 0, 0], 0),
    ([0, 10, 20, 30], 0),
    ([0, 11, 0, 0], 1),
    ([0, 11, 21.1, 31.1], 2),
    ])
def test_count_apneas(input, expected):
    from cpap import count_apneas
    answer = count_apneas(input)
    assert answer == expected


@pytest.mark.parametrize("input1, input2, expected", [
    ([0, 1, 2, 3], [0.1, 0.2, 0.3, 0.4], 0.300),
    ([0, 1, 2, 3], [0.1, -0.2, 0.3, -0.4], -0.500)
    ])
def test_calc_leakage(input1, input2, expected):
    from cpap import calc_leakage
    answer = round(calc_leakage(input1, input2), 3)
    assert answer == expected


@pytest.mark.parametrize("input1, input2, expected", [
    ([0, 1, 2, 3, 4], [0, 1, 0, -1, 0], {'duration': 4, 'breaths': 1,
                                         'breath_rate_bpm': 15.0,
                                         'breath_times': [1],
                                         'apnea_count': 0, 'leakage': 0}),
    ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], [10, 15, 20, 15, 10, 5, 0, 5, 10, 15],
     {'duration': 9, 'breaths': 1, 'breath_rate_bpm': 6.666666666666666,
      'breath_times': [2], 'apnea_count': 0, 'leakage': 5}),
    ([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [0]*11, {'duration': 10,
                                                  'breaths': 0,
                                                  'breath_rate_bpm': 0.0,
                                                  'breath_times': [],
                                                  'apnea_count': 0,
                                                  'leakage': 0}),
    ])
def test_analyze_flow(input1, input2, expected):
    from cpap import analyze_flow
    answer = analyze_flow(input1, input2)
    assert answer == expected


@pytest.mark.parametrize("input1, input2, expected", [
    ("patient_01.txt", {}, "patient_01"),
    ("1.txt", {}, "1"),
    ])
def test_output_file(input1, input2, expected):
    from cpap import output_file
    answer = output_file(input1, input2)
    assert answer == expected
