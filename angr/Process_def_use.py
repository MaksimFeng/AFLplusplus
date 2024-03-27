import json
import re
from collections import OrderedDict


import re


filename = 'strip_def_use_text.txt'  
tbfilename = 'tb_strip.txt'
# generate the def-use pairs from the input text
def process_blocks(input_text):
    # Initialize lists to keep track of def-use pairs and all uses
    def_use_pairs = []
    all_uses = []

    # Variables to track the current definition and its uses
    current_def = None
    uses_for_current_def = []
    with open(filename, 'r') as file:
        input_text = file.read()
    # Process each line in the input text
    for line in input_text.split('\n'):
        # Match definitions
        
        def_match = re.search(r"def: <(0x[0-9a-f]+)", line)
        if def_match:
            # If there's a previous definition with or without uses, append it
            if current_def is not None:
                if uses_for_current_def:
                    for use in uses_for_current_def:
                        def_use_pairs.append((current_def, use))
                    uses_for_current_def = []  # Reset uses for the current definition
                # else:
                #     # If the current definition has no uses, pair it with '0'
                #     def_use_pairs.append((current_def, '0'))
            # Update the current definition
            current_def = def_match.group(1)

        # Match uses
        uses_match = re.search(r"uses: \{([^}]+)\}", line)
        if uses_match:
            current_uses = re.findall(r"<(0x[0-9a-f]+)", uses_match.group(1))
            all_uses.extend(current_uses)  # Keep track of all uses
            if current_def:
                # If there's a current definition, prepare to pair it with these uses
                uses_for_current_def.extend(current_uses)
            else:
                # If there's no current definition, pair these uses with '0'
                for use in current_uses:
                    def_use_pairs.append(('0', use))

    # After processing all lines, check if the last definition had uses
    if current_def:
        if uses_for_current_def:
            for use in uses_for_current_def:
                def_use_pairs.append((current_def, use))
        else:
            def_use_pairs.append((current_def, '0'))

    # Deduplicate pairs and sort them
    def_use_pairs = sorted(set(def_use_pairs), key=lambda x: (x[0], x[1]))

    # Print the def-use pairs
    # for pair in def_use_pairs:
    #     print(f"Def-Use Pair: {pair}")

    return def_use_pairs




def process_tb(filename):
    blocks = []

    with open(filename, 'r') as file:
        data = file.readlines()

    for i, line in enumerate(data):
        parts = line.split(', ')
        tb = parts[0].split(':')[1].strip()
        pc = parts[1].split(':')[1].strip()
        tb_code = parts[2].split(':')[1].strip()
        # Calculate strip for each block except the last one
        if i < len(data) - 1:
            next_tb = data[i + 1].split(', ')[0].split(':')[1].strip()
            strip = hex(int(next_tb, 16) - int(tb, 16))
        else:  # Assign a default strip for the last block
            strip = "0x200"  # Example placeholder strip for the last block
        blocks.append({'tb': tb, 'pc': pc, 'tb_code': tb_code, 'strip': strip})

    # Sort the blocks based on pc values
    sorted_blocks = sorted(blocks, key=lambda x: int(x['pc'], 16))

    return sorted_blocks

# Specify the path to the uploaded file

# Call the function with the updated filename
sorted_blocks = process_tb(tbfilename)



data = process_blocks(filename)
tb_data = process_tb(tbfilename)
print(">>>>>>>>>>>>>>>>>>>>")


for block in tb_data:
    block['num_def'] = 0
    block['num_use'] = 0
    block['def_use_chain'] = []

for info in data:
    # for def_addr in info[0]:
        for block in tb_data:
            pc_start = block['pc']
            pc_end = hex(int(pc_start, 16) + int(block['strip'], 16))
            # print (f"Block {pc_start} - {pc_end}:")
            # print(def_addr)
            if info[0] >= pc_start and info[0] <= pc_end:
                block['num_def'] += 1
                block['def_use_chain'].append(info)
                
    # for use_addr in info[1]:
        for block in tb_data:
            pc_start = block['pc']
            pc_end = hex(int(pc_start, 16) + int(block['strip'], 16))
            # print (f"Block {pc_start} - {pc_end}:")
            # print(use_addr)
            if info[1] >= pc_start and info[1] <= pc_end:
                # print(f"Block {pc_start} - {pc_end}:")
                # print(use_addr)
                block['num_use'] += 1
                block['def_use_chain'].append(info)
print(">>>>>>>>>>>>>>>>>>>>")
# print(tb_data)
with open('strip_def_use_chain.json', 'w') as outfile:
    json.dump(tb_data, outfile)
print(">>>>>>>>>>>>>>>>>>>>")