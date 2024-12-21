import csv
import sys
import re

LEFT_PATTERN = r'^\s*<(\w+)>\s*->\s*((?:<\w+>\s+)?[\wε](?:\s*\|\s*(?:<\w+>\s+)?[\wε])*)\s*$'
RIGHT_PATTERN = r'^\s*<(\w+)>\s*->\s*([\wε](?:\s+<\w+>)?(?:\s*\|\s*[\wε](?:\s+<\w+>)?)*)\s*$'


def print_moore(output_filename, transitions, outputs, states, input_symbols):
    with open(output_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=';')
        header1 = [''] + list(outputs.values())
        writer.writerow(header1)
        header2 = [''] + states
        writer.writerow(header2)

        for input_symbol in input_symbols:
            row = [input_symbol]
            for state in states:
                next_states = transitions[input_symbol].get(state, [])
                row.append(','.join(next_states) if next_states else '')
            writer.writerow(row)


def left_grammar_to_moore(input_file, output_file):
    data = {}
    current_key = None
    current_values = []
    current_record = ""
    matched = False

    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            current_record += " " + line

            match = re.match(LEFT_PATTERN, current_record)
            if match:
                if current_key is not None:
                    data[current_key] = current_values

                current_key = match.group(1)
                current_values = match.group(2).split('|')
                current_values = [value.strip() for value in current_values]
                if len(current_values) > 1 or len(current_values[0]) > 1:
                    matched = True

                current_record = ""

        if current_key is not None:
            data[current_key] = current_values

    if not matched:
        right_grammar_to_moore(input_file, output_file)
        return

    states_map = convert_to_states(["H"] + list(data.keys()))
    final_state = states_map[list(data.keys())[0]]

    outputs = get_outputs(states_map, final_state)
    input_symbols = get_input_symbols(data)
    transitions = create_transitions_left(data, states_map, input_symbols)
    print_moore(output_file, transitions, outputs, list(states_map.values()), input_symbols)

    return data


def right_grammar_to_moore(input_file, output_file):
    data = {}
    current_key = None
    current_values = []
    current_record = ""

    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            current_record += " " + line

            match = re.match(RIGHT_PATTERN, current_record)
            if match:
                if current_key is not None:
                    data[current_key] = current_values

                current_key = match.group(1)
                current_values = match.group(2).split('|')
                current_values = [value.strip() for value in current_values]

                current_record = ""

        if current_key is not None:
            data[current_key] = current_values

    print("data", data)

    states_map = convert_to_states(list(data.keys()) + ["F"])
    print("states_map", states_map)
    final_state = states_map["F"]
    outputs = get_outputs(states_map, final_state)
    print("outputs", outputs)

    input_symbols = get_input_symbols(data)
    print("input_symbols", input_symbols)
    transitions = create_transitions_right(data, states_map, input_symbols)
    print("transitions", transitions)
    print_moore(output_file, transitions, outputs, list(states_map.values()), input_symbols)

    return data


def convert_to_states(data):
    state_dict = {}
    state_counter = 0

    for key in data:
        state_name = f'q{state_counter}'
        state_dict[key] = state_name
        state_counter += 1

    return state_dict


def get_outputs(states_map, final_state):
    outputs = {}

    for state in states_map.values():
        if state == final_state:
            outputs[state] = 'F'
        else:
            outputs[state] = ''

    return outputs


def get_input_symbols(data):
    result = set()

    for values in data.values():
        for value in values:
            symbols = re.findall(r'(?<!<)\b\w+\b(?!>)', value)
            result.update(symbols)

    return list(result)


def create_transitions_left(data, states_map, input_symbols):
    transitions = {}

    for symbol in input_symbols:
        transitions[symbol] = {state: [] for state in states_map.values()}

        for key, values in data.items():
            for value in values:
                match = re.match(r'(<\w+>)\s*(\w+)', value)
                bracketed_symbol = ''
                if match:
                    bracketed_symbol = match.group(1).strip('<>')
                    word = match.group(2)

                if symbol in value:
                    if '<' not in value and '>' not in value:
                        transitions[symbol][states_map['H']].append(states_map[key])
                    else:
                        transitions[symbol][states_map[bracketed_symbol]].append(states_map[key])

    return transitions


def create_transitions_right(data, states_map, input_symbols):
    transitions = {}

    for symbol in input_symbols:
        transitions[symbol] = {state: [] for state in states_map.values()}

        for key, values in data.items():
            for value in values:
                match = re.match(r'(\w+)\s*(<\w+>)', value)
                bracketed_symbol = ''
                if match:
                    bracketed_symbol = match.group(2).strip('<>')

                if symbol in value:
                    if '<' not in value and '>' not in value:
                        transitions[symbol][states_map[key]].append(states_map['F'])
                    else:
                        transitions[symbol][states_map[key]].append(states_map[bracketed_symbol])

    return transitions


def main():
    if len(sys.argv) != 3:
        print("Использование:")
        print("program NFAin.csv DFAout.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    left_grammar_to_moore(input_file, output_file)


if __name__ == "__main__":
    main()
