"""An Improved Simulated Annealing–Linear Programming Hybrid Algorithm Applied to the Optimal Coordination of
Directional Overcurrent Relays: CASE IV"""

import random
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time

from linearprogramming import LinearProgramming
from searchdirection import SearchDirection

# General Article Data
mu = 0.01
phi = 0.05
alpha = 0.6
ksi = 20
Ai = 0.14
Ni = 0.02

# Case Data: System 15 Bar IEEE
path_ = '/Users/amand/Google Drive/210113-Tópicos Especiais em Análises de Redes Elétricas-Proteção de Sistemas ' \
        'Elétricos/6. Proposta de Trabalho (Artigo)/Data_System'

General_Data = pd.read_excel(f'{path_}/fifteen_bus_system.xlsx', sheet_name='General_Data')

Specific_Data = pd.read_excel(f'{path_}/fifteen_bus_system.xlsx', sheet_name='Specific_Data')

# Transform dataframe into dictionary
General_Data = General_Data.to_dict('list')
Specific_Data = Specific_Data.to_dict('list')

# Number of relays
number_relays = int(max(Specific_Data['Rp']))

# CTI is the coordination time interval (in seconds)
CTI = 0.2

# Bounds on relay settings
TDS_min = .1
TDS_max = 1.1

# Bounds on relay settings
PS_min = .5
PS_max = 2.5
step = .5

ps_available = [0.5, 1.0, 1.5, 2.0, 2.5]

# ps_available = np.arange(start=PS_min, stop=PS_max + step, step=step, dtype=None)

run = 0
num_run = 1
best_solution = None
start = time.time()

while run < num_run:
    # Initializes empty initial solution
    fs0 = None

    while fs0 is None:
        '''PASS 1'''
        # Create an initial solution
        ps = list()
        for ir in range(number_relays):
            ps.append(random.choice(ps_available))

        '''PASS 2'''
        # Initial solution or S0
        problem = LinearProgramming(Ai, Ni, CTI, TDS_min, TDS_max, PS_min)
        problem = problem.solve_lp(General_Data, Specific_Data, ps)

        # Check if the initial solution is feasible
        if problem.status != 'optimal':
            # If not, a new initial solution must be generated
            fs0 = None
        else:
            # If yes, update the initial solution for the initialized PS
            fs0 = problem.objective.value()[0]
            s0 = ps

    '''PASS 2'''
    # Initial solution or S0
    problem = LinearProgramming(Ai, Ni, CTI, TDS_min, TDS_max, PS_min)
    problem.solve_lp(General_Data, Specific_Data, ps)

    # Initial solution
    fs0 = problem.of.value()[0]
    T0 = (mu / (-np.log(phi))) * problem.of.value()[0]

    # Set the temperature T as initial temperature T0
    temperature = T0

    solution_set = {
        's': list(),
        'fs': list(),
        'tds': list(),
        'k': list()
        }

    solution_set['s'].extend(s0)
    solution_set['fs'].append(fs0)
    tds = list()
    for ir in range(number_relays):
        tds.append(problem.tds[ir].value()[0])
    solution_set['tds'].append(tds)
    solution_set['k'].append(1)

    count = -1

    solution = SearchDirection(Ai, Ni, CTI, TDS_min, TDS_max, PS_min, PS_max, ps_available)
    solution.intensification_procedure(General_Data, Specific_Data, ps, solution_set, temperature, count)
    if best_solution is None:
        best_solution = solution_set
    else:
        if solution_set['fs'][-1] < best_solution['fs'][-1]:
            best_solution = solution_set
        else:
            pass
    run += 1

end = time.time()
print(f'Tempo de Execução: {(end - start) / num_run:.04f}s!\n')

print('|-------------------------------------------------------------------------------------------------------|\n'
      '|--------------------------------------IEEE 15 BUS SYSTEM RESULTS!--------------------------------------|\n'
      '|-------------------------------------------------------------------------------------------------------|')
print('|---------------------------------------OBJECTIVE FUNCTION VALUE:---------------------------------------|')
print(f"|                                               {best_solution['fs'][-1]:.04f}s"
      f"                                                |")
print('|-------------------------------------------------------------------------------------------------------|')
print('|---------------------------------PLUG SETTINGS AND TIME DIAL SETTINGS:---------------------------------|')
print('|-------------------------------------------------------------------------------------------------------|')
for ir in range(number_relays):
    print(f"|    Relay Number: {ir + 1:02.0f}    |",
          f"    Plug Settings (PS): {best_solution['s'][-number_relays:][ir]:.04f}    |",
          f"    Time Dial Settings (TDS): {best_solution['tds'][-1][ir]:.04f}     |")
print('|-------------------------------------------------------------------------------------------------------|')

for ic in range(ksi):
    best_solution['k'].append(best_solution['k'][-1] + 1)
    best_solution['fs'].append(best_solution['fs'][-1])

# Plot a graph of the evolution of the solution
path_ = '/Users/amand/Google Drive/210113-Tópicos Especiais em Análises de Redes Elétricas-Proteção de Sistemas ' \
        'Elétricos/6. Proposta de Trabalho (Artigo)/Figures'
fig, ax = plt.subplots()
ax.plot(best_solution['k'], best_solution['fs'], '-', color='royalblue', lw=2)
ax.plot(best_solution['k'], best_solution['fs'], 'o', color='royalblue')
ax.set_xlim([0, best_solution['k'][-1]])
ax.set_ylim([0.99 * best_solution['fs'][-1], 1.01 * best_solution['fs'][0]])
title = f'IEEE 15 BUS SYSTEM RESULTS'
ax.set_title(title, fontsize=16, weight='bold')
ax.set_xlabel('Iteration', fontsize=12)
ax.set_ylabel('Objective Function Value', fontsize=12)
plt.grid()
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
graphic = plt.gcf()
graphic.savefig(f'{path_}/fig_15bus.png', format='png')
plt.show()
