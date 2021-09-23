"""An Improved Simulated Annealing–Linear Programming Hybrid Algorithm Applied to the Optimal Coordination of
Directional Overcurrent Relays (DOI: https://doi.org/10.1016/j.epsr.2020.106197)"""

"""Electric Power Systems Research - Accepted 3 January 2020"""

"""Authors: Alexandre A. Kida
            Angel E. Labrador Rivas
            Luis A. Gallego"""

"""Reproduction: Amanda Pávila Silva (102100572)"""

import subprocess
import time

system = int(input('Enter the number for the desired system: \n'
                   '3  - IEEE 3-BUS SYSTEM! \n'
                   '6  - IEEE 6-BUS SYSTEM! \n'
                   '8  - IEEE 8-BUS SYSTEM! \n'
                   '15 - IEEE 15-BUS SYSTEM! \n'
                   '30 - IEEE 30-BUS SYSTEM! \n'))

try:
    __import__(f'data_{system}bus')
except ModuleNotFoundError:
    print('Number entered does not refer to one of the test systems!')
    __import__('main')

# run = 0
# num_run = 20
# start = time.time()
# while run < num_run:
#     subprocess.call(f'data_{system}bus.py', shell=True)
#     run += 1
# end = time.time()
# print(f'Tempo Médio de Execução: {(end - start)/num_run}s!\n')
