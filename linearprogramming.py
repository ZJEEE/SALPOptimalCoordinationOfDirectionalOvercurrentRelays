# coding: utf-8
from cvxopt.modeling import variable, op


class LinearProgramming(object):

    def __init__(self, Ai, Ni, CTI, TDS_min, TDS_max, PS_min):

        # General Article Data
        self.mu = 0.01
        self.phi = 0.05
        self.alpha = 0.6
        self.ksi = 20

        # CTI is the coordination time interval (in seconds)
        self.CTI = CTI

        # Bounds on relay settings
        self.TDS_min = TDS_min
        self.TDS_max = TDS_max

        self.PS_min = PS_min

        self.Ai = Ai
        self.Ni = Ni

    def solve_lp(self, General_Data, Specific_Data, ps):

        # Number of relays
        number_relays = int(max(Specific_Data['Rp']))

        # Decision variables (linear modeling)
        self.tds = variable(number_relays, 'TDS')

        # Set of restrictions
        self.constraints = []

        for ir in range(number_relays):
            self.constraints.append(self.tds[ir] >= self.TDS_min)
            self.constraints.append(self.tds[ir] <= self.TDS_max)

        # Selectivity criteria
        for ir, relay in enumerate(Specific_Data['Rbp']):
            if Specific_Data['Icc_remote'][ir] < self.PS_min * Specific_Data['CTRbp'][ir]:
                pass
            else:
                eq = 0
                eq += self.tds[relay - 1] * self.Ai / ((Specific_Data['Icc_remote'][ir] /
                                                        (Specific_Data['CTRbp'][ir] * ps[relay - 1])) ** self.Ni - 1)

                eq -= self.tds[Specific_Data['Rp'][ir] - 1] * self.Ai / ((Specific_Data['Icc_local'][ir] /
                                                                          (Specific_Data['CTRp'][ir] *
                                                                           ps[Specific_Data['Rp'][ir] - 1])) ** self.Ni - 1)

                self.constraints.append(eq >= self.CTI)

        # Objective function
        self.of = 0
        for ir, relay in enumerate(General_Data['Rp']):

            self.of += self.tds[relay - 1] * self.Ai / ((General_Data['Icc_local'][ir]
                                                         / (General_Data['CTRp'][ir] * ps[relay - 1])) ** self.Ni - 1)

        # Solves linear optimization problem:
        problem = op(self.of, self.constraints)

        # Enables GLPK solver and disables status messages:
        problem.solve('dense', 'glpk', options={'glpk': {'msg_lev': 'GLP_MSG_OFF'}})
        self.status = 'optimal!'

        # Checks for errors in optimizing the problem:
        if problem.status != 'optimal':
            self.status = 'error!'
            # print('ERRO NA OTIMIZAÇÃO DO PROBLEMA!')

        return problem
