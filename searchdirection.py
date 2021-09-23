# coding: utf-8

import random
import numpy as np
import pandas as pd
from linearprogramming import LinearProgramming


class SearchDirection(object):

    def __init__(self, Ai, Ni, CTI, TDS_min, TDS_max, PS_min, PS_max, ps_available):

        # General Data
        self.mu = 0.01
        self.phi = 0.05
        self.alpha = 0.6
        self.ksi = 20

        self.Ai = Ai
        self.Ni = Ni

        # CTI is the coordination time interval (in seconds)
        self.CTI = CTI

        # Bounds on relay settings
        self.TDS_min = TDS_min
        self.TDS_max = TDS_max

        # Bounds on relay settings
        self.PS_min = PS_min
        self.PS_max = PS_max
        self.ps_available = ps_available

    def search_direction(self, General_Data, Specific_Data, ps, initial_relay, solution_set, temperature):

        """PASS 4"""
        index = self.ps_available.index(ps[initial_relay - 1])

        # Solution go down
        ps_down = ps
        if ps_down[initial_relay - 1] > self.PS_min:
            ps_down[initial_relay - 1] = self.ps_available[index - 1]
            problem = LinearProgramming(self.Ai, self.Ni, self.CTI, self.TDS_min, self.TDS_max, self.PS_min)
            problem = problem.solve_lp(General_Data, Specific_Data, ps_down)
            if problem.status != 'optimal':
                solution_down = np.inf
            else:
                solution_down = problem.objective.value()[0]
        else:
            solution_down = np.inf

        ps[initial_relay - 1] = self.ps_available[index]
        # Solution go up
        ps_up = ps
        if ps_up[initial_relay - 1] < self.PS_max:
            ps_up[initial_relay - 1] = self.ps_available[index + 1]
            problem = LinearProgramming(self.Ai, self.Ni, self.CTI, self.TDS_min, self.TDS_max, self.PS_min)
            problem = problem.solve_lp(General_Data, Specific_Data, ps_up)
            if problem.status != 'optimal':
                solution_up = np.inf
            else:
                solution_up = problem.objective.value()[0]
        else:
            solution_up = np.inf

        assert isinstance(index, object)
        ps[initial_relay - 1] = self.ps_available[index]

        if (solution_down < solution_set['fs'][-1]) or (solution_down > solution_set['fs'][-1]
                                                        and np.exp((solution_set['fs'][-1] - solution_down)
                                                                   / temperature) > random.random()):
            sense = True
        elif solution_up < solution_set['fs'][-1] or (solution_up > solution_set['fs'][-1]
                                                        and np.exp((solution_set['fs'][-1] - solution_up)
                                                                   / temperature) > random.random()):
            sense = False
        else:
            sense = None

        return sense

    def intensification_procedure(self, General_Data, Specific_Data, ps, solution_set, temperature, count):

        # Number of relays
        number_relays = int(max(Specific_Data['Rp']))

        stop_criterion = solution_set['fs'][-1]

        while count < self.ksi:

            if solution_set['fs'][-1] != stop_criterion:
                stop_criterion = solution_set['fs'][-1]
            else:
                count += 1

            _continue_ = True

            """PASS 3"""
            # List of relays and their respective operating times
            tij = dict(relay=list(), Tij=list())

            for ir, relay in enumerate(General_Data['Rp']):
                tij['relay'].append(relay)
                time_ij = solution_set['tds'][-1][relay - 1] * self.Ai / ((General_Data['Icc_local'][ir] /
                                                                           (General_Data['CTRp'][ir]) * ps[relay - 1])
                                                                          ** self.Ni - 1)
                tij['Tij'].append(time_ij)

            tij = pd.DataFrame(tij)

            tij.sort_values(by=['Tij'], ascending=False, ignore_index=True, inplace=True)

            # Identifies first relay
            ir = 0
            initial_relay = tij['relay'][ir]

            """PASS 4"""
            sense = self.search_direction(General_Data, Specific_Data, ps, initial_relay, solution_set, temperature)

            while _continue_:

                if sense is None:
                    if tij['relay'].iloc[-1] != initial_relay:
                        """PASS 7"""
                        ir += 1
                        initial_relay = tij['relay'][ir]
                        sense = self.search_direction(General_Data, Specific_Data, ps, initial_relay, solution_set,
                                                      temperature)
                        continue
                    else:
                        """PASS 8 TO PASS 3"""
                        _continue_ = False

                else:
                    """PASS 5"""
                    if ps[initial_relay - 1] > self.PS_min and sense:
                        index = self.ps_available.index(ps[initial_relay - 1])
                        ps[initial_relay - 1] = self.ps_available[index - 1]

                    elif ps[initial_relay - 1] < self.PS_max and not sense:
                        index = self.ps_available.index(ps[initial_relay - 1])
                        ps[initial_relay - 1] = self.ps_available[index + 1]

                    problem = LinearProgramming(self.Ai, self.Ni, self.CTI, self.TDS_min, self.TDS_max, self.PS_min)
                    problem.solve_lp(General_Data, Specific_Data, ps)

                    if problem.status == 'error!':
                        sense = None
                        continue

                    # Updates solution set
                    sj = ps
                    fsj = problem.of.value()[0]

                    r = random.random()
                    if fsj < solution_set['fs'][-1] or (
                            fsj > solution_set['fs'][-1] and np.exp((solution_set['fs'][-1] -
                                                                     fsj) / temperature) > r):

                        """PASS 6"""
                        solution_set['s'].extend(sj)
                        solution_set['fs'].append(fsj)
                        solution_set['k'].append(solution_set['k'][-1] + 1)
                        temperature = self.alpha * temperature
                        ps = solution_set['s'][-number_relays:]
                        tds = list()
                        for i in range(number_relays):
                            tds.append(problem.tds[i].value()[0])
                        solution_set['tds'].append(tds)

                        if ps[initial_relay - 1] == self.PS_min or ps[initial_relay - 1] == self.PS_max:

                            if tij['relay'].iloc[-1] != initial_relay:
                                """PASS 7"""
                                ir += 1
                                initial_relay = tij['relay'][ir]
                                sense = self.search_direction(General_Data, Specific_Data, ps, initial_relay,
                                                              solution_set, temperature)
                            else:
                                """PASS 8 TO PASS 3"""
                                _continue_ = False

                    else:
                        ps = solution_set['s'][-number_relays:]

                        if tij['relay'].iloc[-1] != initial_relay:
                            """PASS 7"""
                            ir += 1
                            initial_relay = tij['relay'][ir]
                            sense = self.search_direction(General_Data, Specific_Data, ps, initial_relay, solution_set,
                                                          temperature)
                        else:
                            """PASS 8 TO PASS 3"""
                            _continue_ = False

        return solution_set
