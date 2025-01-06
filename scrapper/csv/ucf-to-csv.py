#!/usr/bin/env python

import json
import csv
import sys

def ucf_to_csv(ucf_data):
    # Dictionaries to hold data
    gates = {}              # key: gate_name, value: gate data
    response_functions = {} # key: gate_name, value: response function data
    gate_parts = {}         # key: gate_name, value: gate parts data
    parts = {}              # key: part_name, value: part data

    # Process UCF data
    for item in ucf_data:
        collection = item.get('collection', '')
        if collection == 'gates':
            gate_name = item.get('gate_name') or item.get('name')
            if gate_name is None:
                print("Warning: Gate item without 'gate_name' or 'name':", item)
                continue
            gates[gate_name] = item
        elif collection == 'response_functions':
            gate_name = item.get('gate_name') or item.get('name')
            if gate_name is None:
                print("Warning: Response function without 'gate_name' or 'name':", item)
                continue
            response_functions[gate_name] = item
        elif collection == 'gate_parts':
            gate_name = item.get('gate_name') or item.get('name')
            if gate_name is None:
                print("Warning: Gate parts without 'gate_name' or 'name':", item)
                continue
            gate_parts[gate_name] = item
        elif collection == 'parts':
            part_name = item.get('name')
            if part_name is None:
                print("Warning: Part without 'name':", item)
                continue
            parts[part_name] = item

    def get_dna_sequence(part):
        return part.get('dnasequence') or part.get('dna_sequence') or part.get('sequence') or ''

    headers = [
        'name',
        'cds',
        'type',
        'ribozyme',
        'ribozymeDNA',
        'rbs',
        'rbsDNA',
        'cdsDNA',
        'terminator',
        'terminatorDNA',
        'promoter',
        'promoterDNA',
        'equation',
        'ymax',
        'ymin',
        'K',
        'n',
        'IL',
        'IH'
    ]

    rows = []
    for gate_name in gates.keys():
        row = {}

        gate = gates.get(gate_name, {})
        response_function = response_functions.get(gate_name, {})
        gate_part = gate_parts.get(gate_name, {})

        # Gate data
        row['name'] = gate_name
        row['cds'] = gate.get('regulator', '')
        row['type'] = gate.get('gate_type', '')

        # Gate parts data
        promoter_name = gate_part.get('promoter', '')
        cassettes = gate_part.get('expression_cassettes', [])
        ribozyme_name = ''
        rbs_name = ''
        cds_cassette_name = ''
        terminator_name = ''

        if cassettes:
            cassette = cassettes[0]
            cassette_parts = cassette.get('cassette_parts', [])

            print(f"\nProcessing gate: {gate_name}")
            print(f"Cassette parts: {cassette_parts}")

            for part_name in cassette_parts:
                part = parts.get(part_name, {})
                if not part:
                    print(f"Warning: Part '{part_name}' not found in 'parts' collection for gate '{gate_name}'.")
                    continue
                part_type = part.get('type', '').lower()
                if not part_type:
                    part_name_lower = part_name.lower()
                    if 'ribozyme' in part_name_lower:
                        part_type = 'ribozyme'
                    elif 'rbs' in part_name_lower:
                        part_type = 'rbs'
                    elif 'terminator' in part_name_lower:
                        part_type = 'terminator'
                    elif 'cds' in part_name_lower or part_name == row['cds'].lower():
                        part_type = 'cds'
                    else:
                        print(f"Warning: Unable to determine type for part '{part_name}' in gate '{gate_name}'.")
                        continue

                if part_type == 'ribozyme':
                    ribozyme_name = part_name
                elif part_type == 'rbs':
                    rbs_name = part_name
                elif part_type == 'cds':
                    cds_cassette_name = part_name
                elif part_type == 'terminator':
                    terminator_name = part_name

                print(f"Identified part '{part_name}' as type '{part_type}'.")

        else:
            print(f"Warning: No expression cassettes found for gate '{gate_name}'.")

        row['ribozyme'] = ribozyme_name
        row['rbs'] = rbs_name
        row['cds'] = cds_cassette_name or row['cds']
        row['terminator'] = terminator_name
        row['promoter'] = promoter_name

        # Parts data
        ribozyme_part = parts.get(ribozyme_name, {})
        rbs_part = parts.get(rbs_name, {})
        cds_part = parts.get(row['cds'], {})
        terminator_part = parts.get(terminator_name, {})
        promoter_part = parts.get(promoter_name, {})

        # Assign DNA sequences
        row['ribozymeDNA'] = get_dna_sequence(ribozyme_part)
        row['rbsDNA'] = get_dna_sequence(rbs_part)
        row['cdsDNA'] = get_dna_sequence(cds_part)
        row['terminatorDNA'] = get_dna_sequence(terminator_part)
        row['promoterDNA'] = get_dna_sequence(promoter_part)

        # Response function data
        row['equation'] = response_function.get('equation', '')
        parameters = response_function.get('parameters', [])
        for param in parameters:
            param_name = param.get('name', '').lower()
            param_value = param.get('value', '')
            if param_name in ['ymax', 'ymin', 'k', 'n']:
                row[param_name] = param_value

        variables = response_function.get('variables', [])
        for var in variables:
            var_name = var.get('name', '')
            if var_name == 'x':
                row['IL'] = var.get('off_threshold', '')
                row['IH'] = var.get('on_threshold', '')

        # Debugging output
        print(f"Row data for gate {gate_name}: {row}")

        # Append row to list
        rows.append(row)

    return headers, rows

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python ucf_to_csv.py Eco1C1G1T1.UCF.json > gates.csv')
        sys.exit()

    ucfpath = sys.argv[1]

    # Read UCF JSON file
    with open(ucfpath) as ucf_file:
        ucf_data = json.load(ucf_file)

    # Convert UCF to CSV data
    headers, rows = ucf_to_csv(ucf_data)

    # Write CSV data to stdout
    writer = csv.DictWriter(sys.stdout, fieldnames=headers)
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
