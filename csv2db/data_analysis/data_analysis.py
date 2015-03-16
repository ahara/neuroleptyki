import math
import json
import datetime
from collections import Counter

import graph
import consts
import networkx as nx
import matplotlib.pyplot as plt

def read_json(path):
    """Read object from json file.

    Parameters:
    json - path to json file
    """

    print 'Reading json'
    with open(path, 'rb') as f:
        return json.load(f)

def save_json(object, path):
    """Write object to json file.

    Parameters:
    object - object to write
    path   - path to json file
    """

    print 'Saving to json'
    with open(path, 'w') as f:
        json.dump(object, f)

def date_diff(date1, date2):
    """Calculate difference in days between to dates. It's not absolute value.

    Parameters:
    date1 - first date
    date2 - second date
    """

    d1 = datetime.datetime.strptime(date1, '%Y/%m/%d')
    d2 = datetime.datetime.strptime(date2, '%Y/%m/%d')
    delta = d2 - d1
    return delta.days

def date_month_interval(date1, date2):
    """Calculate absolute difference in months (without using day in month information) between two dates.

    Parameters:
    date1 - first date
    date2 - second date
    """

    difference = (int(date2[0:4]) - int(date1[0:4])) * 12
    difference += int(date2[5:7]) - int(date1[5:7])
    return abs(difference)

def date_year_interval(date1, date2):
    """Calculate absolute difference in years (using only year information) between two dates.

    Parameters:
    date1 - first date
    date2 - second date
    """
    return abs(int(date2[0:4]) - int(date1[0:4]))

def prescription_chains(patient, last_medicine_to_death_intervals, cut_chains, max_date_diff_cut=90, max_date_diff_heart=183):
    """Create prescription chains for one patient.

    Parameters:
    patient                          - patient vector
    last_medicine_to_death_intervals - array of intervals between last prescription date and death date
    cut_chains                       - flag indicating whether chains should be cut when date difference between to consecutive prescriptions is higher then max_date_diff_cut
    max_date_diff_cut                - maximum number of days between two consecutive prescriptions that doesn't cut chain
    max_date_diff_heart              - maximum number of days between first cardio and neuroleptic prescription that assign then to group 1
    """

    chains = []
    c = []
    last_prescription = None
    age = date_year_interval(patient['birth'], patient['died'] if patient['died'] else '2012')
    patient_cardio_group = 0
    if len(patient['prescriptions_heart']) > 0:
        if abs(date_diff(patient['prescriptions'][0][0], patient['prescriptions_heart'][0][0])) < max_date_diff_heart:
            patient_cardio_group = 1
        elif patient['prescriptions'][0][0] < patient['prescriptions_heart'][0][0]:
            patient_cardio_group = 2
        else:
            patient_cardio_group = 3
    for p in patient['prescriptions']:
        if cut_chains and last_prescription and date_diff(last_prescription[0], p[0]) > max_date_diff_cut:
            # Starting new chain
            c.append([bool(patient['died']), patient['sex'], age, patient_cardio_group])
            if patient['died']:
                last_medicine_to_death_intervals.append(date_month_interval(last_prescription[0], patient['died']))
            chains.append(c)
            c = []
        last_prescription = p
        c.append(p)
    c.append([bool(patient['died']), patient['sex'], age, patient_cardio_group])
    if patient['died']:
        last_medicine_to_death_intervals.append(date_month_interval(last_prescription[0], patient['died']))
    chains.append(c)
    return chains

def create_and_show_histogram(data, range_interval, normalized, cumulative):
    """Create histogram of provided data and show it.

    Parameters:
    data - input data for histogram
    range_interval - length of each histogram bin
    normalized - flag setting whether histogram should be normalized
    cumulative - flag setting whether histogram should be cumulative
    """

    histogram_range = range(0, int(math.ceil(max(data) / float(range_interval)) + 1) * range_interval, range_interval)
    histogram = plt.hist(data, histogram_range, normed = normalized, cumulative = cumulative)
    for i, j in zip(histogram[1], histogram[0]):
        print i, j * (range_interval if normalized and not cumulative else 1)
        plt.text(i, j, '{0:0.2}'.format(j) if normalized else str(j))
    plt.show()

def data_to_chains(data, cut_chains=False, show_ages_histogram=False, show_death_histogram=False, show_ages_death_histogram=False, show_patient_sequences_count_histogram=False, show_patient_sequences_lengths_histogram=False, show_patient_intervals_histogram=False, ages_histogram_interval=5, death_histogram_months_interval=6, patient_sequences_lengths_histogram_interval=183, patient_intervals_histogram_interval=30, histogram_normalized=False, histogram_cumulative=False):
    """Convert vectors to chains.

    Parameters:
    data                                         - input vectors
    cut_chains                                   - flag setting whether chains should be cut when date difference between consecutive prescriptions exceed specified time
    show_ages_histogram                          - flag setting whether patients' ages histogram should be shown
    show_death_histogram                         - flag setting whether intervals to death histogram should be shown
    show_ages_death_histogram                    - flag setting whether dead patients' ages histogram should be shown
    show_patient_sequences_count_histogram       - flag setting whether patients' sequences count histogram should be shown
    show_patient_sequences_lengths_histogram     - flag setting whether patients' sequences lengths histogram should be shown
    show_patient_intervals_histogram             - flag setting whether intervals between sequences histogram should be shown
    ages_histogram_interval                      - length of histogram bins of patients' ages histogram
    death_histogram_months_interval              - length in months of histogram bins of intervals to death histogram
    patient_sequences_lengths_histogram_interval - length of histogram bins of patients' sequences lengths histogram
    patient_intervals_histogram_interval         - length of histogram bins of intervals between sequences histogram
    histogram_normalized                         - flag setting whether histograms should be normalized
    histogram_cumulative                         - flag setting whether histograms should be cumulative
    """

    print 'Chains creation'
    chains = []
    i = 0
    multiple_chains_patients = 0
    first_month_chains = 0
    last_month_chains = 0
    first_and_last_month_patients = 0
    last_medicine_to_death_intervals = []
    patient_sequences_counts = []
    patient_sequences_lengths_in_days = []
    patient_sequences_intervals_in_days = []
    patient_ages = []
    patient_ages_man = []
    patient_ages_woman = []
    patient_ages_deaths_only = []
    patient_ages_deaths_only_man = []
    patient_ages_deaths_only_woman = []
    for d in data:
        patient_chains = prescription_chains(d, last_medicine_to_death_intervals, cut_chains)
        if len(patient_chains) > 1:
            multiple_chains_patients += 1
        first_month = reduce(lambda a, b: a + (1 if b[0][0][0:7] == '2008/01' else 0), patient_chains, 0)
        last_month = reduce(lambda a, b: a + (1 if b[-2][0][0:7] == '2012/12' else 0), patient_chains, 0)
        first_month_chains += first_month
        last_month_chains += last_month
        if first_month:
            if last_month:
                first_and_last_month_patients += 1
        #if not first_month and not last_month:
        chains += patient_chains
        age = date_year_interval(d['birth'], d['died'] if d['died'] else '2012');
        patient_ages.append(age)
        if d['sex'] == 'm':
            patient_ages_man.append(age)
        else:
            patient_ages_woman.append(age)
        if d['died']:
            patient_ages_deaths_only.append(age)
            if d['sex'] == 'm':
                patient_ages_deaths_only_man.append(age)
            else:
                patient_ages_deaths_only_woman.append(age)
        patient_sequences_counts.append(len(patient_chains))
        last_sequence = None
        for sequence in patient_chains:
            patient_sequences_lengths_in_days.append(date_diff(sequence[0][0], sequence[-2][0]))
            if last_sequence:
                patient_sequences_intervals_in_days.append(date_diff(last_sequence[-2][0], sequence[0][0]))
            last_sequence = sequence
        i += 1
        if i % 1000 == 0:
            print '{0}/{1}'.format(i, len(data)), 'patients done'
    print '{0}/{1}'.format(multiple_chains_patients, len(data)), 'patients with multiple chains'
    print '{0}/{1}'.format(first_month_chains, len(chains)), 'chains starting in 2008/01'
    print '{0}/{1}'.format(last_month_chains, len(chains)), 'chains ending in 2012/12'
    print '{0}/{1}'.format(first_and_last_month_patients, len(data)), 'patients treated over whole period'
    print '{0}/{1}'.format(len(last_medicine_to_death_intervals), len(chains)), 'chains ends with death'
    if show_ages_histogram:
        create_and_show_histogram(patient_ages, ages_histogram_interval, histogram_normalized, histogram_cumulative)
        print 'MAN'
        create_and_show_histogram(patient_ages_man, ages_histogram_interval, histogram_normalized, histogram_cumulative)
        print 'WOMAN'
        create_and_show_histogram(patient_ages_woman, ages_histogram_interval, histogram_normalized, histogram_cumulative)
    if show_death_histogram:
        create_and_show_histogram(last_medicine_to_death_intervals, death_histogram_months_interval, histogram_normalized, histogram_cumulative)
    if show_ages_death_histogram:
        create_and_show_histogram(patient_ages_deaths_only, ages_histogram_interval, histogram_normalized, histogram_cumulative)
        print 'MAN'
        create_and_show_histogram(patient_ages_deaths_only_man, ages_histogram_interval, histogram_normalized, histogram_cumulative)
        print 'WOMAN'
        create_and_show_histogram(patient_ages_deaths_only_woman, ages_histogram_interval, histogram_normalized, histogram_cumulative)
    if show_patient_sequences_count_histogram:
        create_and_show_histogram(patient_sequences_counts, 1, histogram_normalized, histogram_cumulative)
    if show_patient_sequences_lengths_histogram:
        create_and_show_histogram(patient_sequences_lengths_in_days, patient_sequences_lengths_histogram_interval, histogram_normalized, histogram_cumulative)
    if show_patient_intervals_histogram:
        create_and_show_histogram(patient_sequences_intervals_in_days, patient_intervals_histogram_interval, histogram_normalized, histogram_cumulative)
    return chains

def data_to_statuses(data):
    """Convert vectors to array of information whether patient is dead.

    Parameters:
    data - input vectors
    """

    return [d['died'] for d in data]

def map_medicine_to_group(prescription):
    """Changes medicine name in prescription to group that medicine belongs to. Designed to be used in map() operation.

    Parameters:
    prescription - prescription to modify
    """

    if prescription[1] in consts.GENERATION_1:
        prescription[1] = '1'
    elif prescription[1] in consts.GENERATION_2:
        prescription[1] = '2'
    elif prescription[1] in consts.CLOZAPINE:
        pass
    elif prescription[1] in consts.LITHIUM:
        pass
    else:
        print prescription[1], 'not in list of available medicines'
    return prescription

def reduce_parallel_medicines(prescriptions, new_prescription, max_date_diff=1):
    """Reduces prescriptions list by creating list of medicines taken in parallel instead of medicine name. Designed to be used in reduce() operation.

    Parameters:
    prescriptions    - list of already reduced prescriptions
    new_prescription - next prescription in input list
    max_date_diff    - maximum difference in days that accepts medicines as taken in parallel
    """

    if prescriptions == []:
        return [new_prescription]
    

    if date_diff(prescriptions[-1][0], new_prescription[0]) < max_date_diff:
        last_prescription = prescriptions[-1]
        if not isinstance(last_prescription[1], list):
            last_prescription[1] = [last_prescription[1]]
        if new_prescription[1] not in last_prescription[1]:
            last_prescription[1] = last_prescription[1] + [new_prescription[1]]
        return prescriptions
    else:
        return prescriptions + [new_prescription]

def map_parallel_prescription(prescription):
    """Maps medicines list created by reduce_parallel_medicines to single medicine name. Designed to be used in map() operation.

    Parameters:
    prescription - input prescription with possible medicines list in place of medicine name
    """

    if isinstance(prescription[1], list):
        prescription[1].sort()
        prescription[1] = '_'.join(prescription[1])
    return prescription

def reduce_repeating_medicines(prescriptions, new_prescription, grouping_interval_in_days=183):
    """Reduces prescriptions list by removing repeating medicines in list and adding time interval in which the medicine was taken. Designed to be used in reduce() operation.

    Parameters:
    prescriptions             - already reduced prescriptions
    new_prescription          - next prescription in input list
    grouping_interval_in_days - interval in time that is used as single unit when adding time interval in which the medicine was taken
    """

    if new_prescription[1] != '0':
        new_prescription[2] = 0
    if prescriptions == []:
        return [new_prescription]

    if prescriptions[-1][1] == new_prescription[1]:
        prescriptions[-1][2] = date_diff(prescriptions[-1][0], new_prescription[0]) / grouping_interval_in_days
        return prescriptions
    else:
        return prescriptions + [new_prescription]

def reduce_add_long_intervals(prescriptions, new_prescription, grouping_interval_in_days=183, min_date_diff=90):
    """Adds to prescriptions list intervals in time when no medicine was taken. Designed to be used in reduce() operation.

    Parameters:
    prescriptions             - already reduced prescriptions
    new_prescription          - next prescription in input list
    grouping_interval_in_days - interval in time that is used as single unit when adding intervals
    min_date_diff             - minimum time in days that need to appear between two consecutive prescriptions to consider it as interval without medicines
    """

    if prescriptions == []:
        return [new_prescription]

    datediff = date_diff(prescriptions[-1][0], new_prescription[0])
    if datediff > min_date_diff:
        return prescriptions + [[prescriptions[-1][0], '0', datediff / grouping_interval_in_days], new_prescription]
    else:
        return prescriptions + [new_prescription]

def reduce_total(prescriptions, new_prescription):
    """Reduces prescriptions list to list of medicines taken by patient. Designed to be used in reduce() operation.

    Parameters:
    prescriptions    - already reduced prescriptions
    new_prescription - next prescription in input list
    """

    if prescriptions == []:
        return [new_prescription[1]]

    if new_prescription[1] not in prescriptions:
        return prescriptions + [new_prescription[1]]
    else:
        return prescriptions

def convert_age_to_range(age):
    """Converts age to one of specified age ranges.

    Parameters:
    age - age to convert
    """

    for max_age in consts.AGE_RANGES:
        if age < max_age:
            return max_age
    return consts.AGE_RANGES[-1] + 1

def get_age_range_string(age_range):
    """Converts age range to string.

    Parameters:
    age_range - age range to convert
    """

    min_age = 0
    age_range = int(age_range)
    for max_age in consts.AGE_RANGES:
        if age_range == max_age:
            return '{0}-{1}'.format(min_age, max_age - 1)
        min_age = max_age
    return '>={0}'.format(consts.AGE_RANGES[-1])

def analyse_medicine_sequences(chains, consider_age, consider_sex=False, map_to_groups=False, total_reduce=False, reduce_parallel=False, reduce_repeating=False, add_long_intervals=False, remove_short=False, minimum_treatment_time=31):
    """Analyse medicine sequences and create counters for sequences ending with death, cardio etc.

    Parameters:
    chains                 - input sequences
    consider_age           - specifies whether sequences should be split depending on patient's age
    consider_sex           - specifies whether sequences should be split depending on patient's sex
    map_to_groups          - specifies whether medicines should be mapped to their groups
    total_reduce           - specifies whether sequences should be reduced to just medicines taken without considering time and order (if set to true all other flags except map_to_groups are ignored)
    reduce_parallel        - specifies whether parallel prescriptions should be reduced
    reduce_repeating       - specifies whether repeating prescriptions should be reduced
    add_long_intervals     - specifies whether long time intervals between consecutive prescriptions should be added to chains
    remove_short           - specifies whether short sequences should be removed
    minimum_treatment_time - specifies minimum treatment time when remove_short is set to True
    """

    print 'Starting analysis'
    counter_total = Counter()
    counter_lives = Counter()
    counter_deaths = Counter()
    counter_cardio = Counter()
    counter_cardio_deaths = Counter()
    counters_cardio_groups = [Counter(), Counter(), Counter()]
    i = 0
    for c in chains:
        i += 1
        if i % 1000 == 0:
            print '{0}/{1} chains done'.format(i, len(chains))
        if remove_short:
            time_diff = date_diff(c[0][0], c[-2][0]) + 30
            if time_diff < minimum_treatment_time:
                continue
        medicines = c[0:-1]
        if map_to_groups:
            medicines = map(map_medicine_to_group, medicines)
        if total_reduce:
            medicines = reduce(reduce_total, medicines, [])
            medicines.sort()
            medicines = ['_'.join(medicines)]
        else:
            if reduce_parallel:
                medicines = reduce(reduce_parallel_medicines, medicines, [])
                medicines = map(map_parallel_prescription, medicines)
            if add_long_intervals:
                medicines = reduce(reduce_add_long_intervals, medicines, [])
            if reduce_repeating:
                medicines = reduce(reduce_repeating_medicines, medicines,[])
            if reduce_repeating:
                medicines = ['{0}/{1}'.format(p[1], p[2]) for p in medicines]
            elif add_long_intervals:
                medicines = ['{0}/{1}'.format(p[1], p[2]) if p[1] == '0' else p[1] for p in medicines]
            else:
                medicines = [p[1] for p in medicines]
        if consider_sex:
            medicines.append(c[-1][1])
        if consider_age:
            medicines.append(str(convert_age_to_range(c[-1][2])))
        key = ';'.join(medicines)
        counter_total[key] += 1
        if c[-1][0]:
            counter_deaths[key] += 1
        else:
            counter_lives[key] += 1
        if c[-1][3] > 0:
            counter_cardio[key] += 1
            counters_cardio_groups[c[-1][3] - 1][key] += 1
            if c[-1][0]:
                counter_cardio_deaths[key] += 1
    return counter_total, counter_lives, counter_deaths, counter_cardio, counter_cardio_deaths, counters_cardio_groups

def print_stat(counter_total, counter_lives, counter_deaths, counter_cardio, counter_cardio_deaths, counters_cardio_groups, consider_age, minimum_count=10, n=10, path=None):
    """Print statistics obtained after invoking analyse_medicine_sequences.

    Parameters:
    counter_total          - Counter object with total number of sequences
    counter_lives          - Counter object with number of sequences without death date
    counter_deaths         - Counter object with number of sequences with death date
    counter_cardio         - Counter object with number of sequences with patient also taking cardio medicines
    counter_cardio_deaths  - Counter object with number of sequences with patient also taking cardio medicines and with death date
    counters_cardio_groups - list of three Counter objects with number of sequences with patient also taking cardio medicines classified to appropriate group
    consider_age           - specifies whether patient age appears in input, so it should be properly formatted in output
    minimum_count          - specifies minimum number of sequence occurences to appear in output
    n                      - specifies how many of the sequences with highest death rate should be printed to output. If set to 0 then all sequences will be printed
    path                   - specifies path to output file. If set to None then data are printed to standard output
    """

    print 'Creating final file'
    #total_sequence_count = sum(counter_total.values())
    lines = []
    lines.append('Number of sequences;%d' % len(counter_total.keys()))
    lines.append('Minimum sequence count;%d' % minimum_count)
    lines.append('Sequence;Count;Death percentage;Cardio percentage;Cardio in death percentage;Cardio 1;Cardio 2;Cardio 3')
    result_list = [(pair[0], pair[1], 100 * counter_deaths[pair[0]] / pair[1], 100 * counter_cardio[pair[0]] / pair[1],
                    100 * counter_cardio_deaths[pair[0]] / counter_deaths[pair[0]] if counter_deaths[pair[0]] != 0 else 0,
                    100 * counters_cardio_groups[0][pair[0]] / counter_cardio[pair[0]] if counter_cardio[pair[0]] != 0 else 0,
                    100 * counters_cardio_groups[1][pair[0]] / counter_cardio[pair[0]] if counter_cardio[pair[0]] != 0 else 0,
                    100 * counters_cardio_groups[2][pair[0]] / counter_cardio[pair[0]] if counter_cardio[pair[0]] != 0 else 0) for pair in counter_total.items()]
    if minimum_count > 0:
        result_list = [x for x in result_list if x[1] >= minimum_count]
        #result_list = [x for x in result_list if x[1] >= minimum_count * total_sequence_count / 100]
    result_list.sort(key = lambda a: (a[2], a[1]), reverse = True)
    for key, total, death_risk, cardio_risk, cardio_death_risk, cardio_1, cardio_2, cardio_3 in result_list[:n] if n else result_list:
        medicines = key.split(';')
        if consider_age:
            medicines[-1] = get_age_range_string(medicines[-1])
        lines.append('%s:;%s;%d%%;%d%%;%d%%;%d%%;%d%%;%d%%' % (' '.join(medicines), total, death_risk, cardio_risk, cardio_death_risk, cardio_1, cardio_2, cardio_3))
    output = '\n'.join(lines)
    if path:
        with open(path, 'w') as f:
            f.writelines(output)
    else:
        print output

def draw_graph(counter_total, counter_lives, counter_deaths, n=20):
    """Draw graph of survival depending on sequence.

    Parameters:
    counter_total          - Counter object with total number of sequences
    counter_lives          - Counter object with number of sequences without death date
    counter_deaths         - Counter object with number of sequences with death date
    n                      - specifies how many of the sequences with highest death rate should be printed to output. If set to 0 then all sequences will be printed
    """

    print 'Creating graph'
    node_labels = {}
    edge_labels = {}
    graph = nx.DiGraph()
    graph.add_node(0)
    node_labels[0] = 'End'

    i = 1
    for k, v in counter_total.most_common(n) if n else counter_total.most_common():
        lastI = 0
        for medicine in reversed(k.split(';')):
            graph.add_edge(i, lastI)
            edge_labels[(i, lastI)] = medicine
            lastI = i
            i += 1
        node_labels[lastI] = '{0}%'.format(100 * counter_deaths[k] / v)

    print 'Graph created'
    layout = nx.graphviz_layout(graph)
    print 'Graph layout created'
    nx.draw(graph, pos = layout, hold = True, node_color = 'w', node_size = 1000)
    nx.draw_networkx_labels(graph, layout, labels = node_labels)
    nx.draw_networkx_edge_labels(graph, layout, edge_labels = edge_labels)
    plt.show()

if __name__ == '__main__':
    # Sanity check for vectors json
    #vectors = read_json('nasercowe.json')
    #prescriptions_count = 0;
    #prescriptions_cardio_count = 0;
    #patients_without_cardio_count = 0;
    #for v in vectors:
    #    prescriptions_count += len(v['prescriptions'])
    #    prescriptions_cardio_count += len(v['prescriptions_heart'])
    #    if len(v['prescriptions_heart']) == 0:
    #        patients_without_cardio_count += 1
    #print 'Sanity check - patients {0}'.format(len(vectors))
    #print 'Sanity check - prescriptions {0}'.format(prescriptions_count)
    #print 'Sanity check - prescriptions cardio {0}'.format(prescriptions_cardio_count)
    #print 'Sanity check - patients without cardio {0}'.format(patients_without_cardio_count)

    # Convert vectors to chains
    vectors = read_json('nasercowe.json')
    chains = data_to_chains(vectors, cut_chains = True)
    #save_json(chains, 'chains_uncut_heart_183days.json')
    #chains = read_json('chains_uncut_heart_183days.json')

    # Build graph
    #medicines = [[p[1] for p in c] for c in chains]
    #statuses = data_to_statuses(vectors)
    #g = graph.Graph()
    #g.add_chains(medicines, statuses)

    # Analyse sequences
    consider_age = False
    counter_total, counter_lives, counter_deaths, counter_cardio, counter_cardio_deaths, counters_cardio_groups = analyse_medicine_sequences(chains, consider_age, consider_sex = False, map_to_groups = True, total_reduce = False, reduce_parallel = True, reduce_repeating = True, add_long_intervals = False, remove_short = False)
    #save_json((counter_total, counter_lives, counter_deaths), 'counters_1.json')
    #counter_total, counter_lives, counter_deaths = read_json('counters.json')
    print_stat(Counter(counter_total), Counter(counter_lives), Counter(counter_deaths), Counter(counter_cardio), Counter(counter_cardio_deaths), counters_cardio_groups, consider_age, 500, 0, 'top_sequences.csv')
    #draw_graph(Counter(counterTotal), Counter(counterLives),
    #Counter(counterDeaths))

    # Final sanity checks
    print 'Sanity check - number of chains (start)', len(chains)
    #print 'Sanity check - number of chains (total)', sum(counter_total.values())
    #print 'Sanity check - number of chains (d + l)', sum(counter_lives.values() + counter_deaths.values())
    #print 'Sanity check - number of vectors', len(vectors)
    #print 'Sanity check - number of prescriptions',
    #sum([len(v['prescriptions']) for v in vectors])
    #print 'Sanity check - number of prescriptions', sum([len(k.split('_')) * v
    #for k, v in counterTotal.items()])
    print 'Finished'