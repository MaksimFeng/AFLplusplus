# //this may work
import angr.code_location
from angr.knowledge_plugins.key_definitions.atoms import AtomKind, GuardUse, Tmp, Register, MemoryLocation
import angr
import sys
import Process_Angr
import networkx as nx
import angr.analyses.vfg
import angr.analyses.vsa_ddg
import matplotlib.pyplot as plt
import monkeyhex


p = angr.Project('/home/kai/project/fuzz/bin/ld1/ld', auto_load_libs=False)
# p = angr.Project('/home/kai/project/qemu-afl/AFLPLUSSPLUSS_DEV/AFLplusplus/VUN', auto_load_libs=False)

# # , load_options={'main_opts': {'base_addr': 0x4000000000}})
# cfg = p.analyses.CFGEmulated()
# cfg = p.analyses.CFGEmulated(normalize=True)
cfg = p.analyses.CFGFast(normalize=True, data_references=True)
print(p.loader)
rd_results = {}
# output_file_path = 'rd_analysis_output.txt'
# with open(output_file_path, 'w') as output_file:  # Open the file in write mode 

for function_addr, function in cfg.kb.functions.items():
        rd_results[function_addr] = []
        for block_idx, block in enumerate(function.blocks):
            try:
                rd_analysis = p.analyses.ReachingDefinitions(subject=block, track_tmps=True)
                
                print(f"Function {function.name} (0x{function_addr:x}), Block {block_idx}:")
               
                # dep_graph = rd_analysis.dep_graph
                all_defs = rd_analysis.all_definitions
                for _def in rd_analysis.all_definitions:
                    print("def:", _def.codeloc)
                    print("uses:", rd_analysis.all_uses.get_uses(_def))
                
                    

            except Exception as e:
                 
                print(f"Error analyzing block {block_idx} in function {function.name} (0x{function_addr:x}): {e}")


                
              
