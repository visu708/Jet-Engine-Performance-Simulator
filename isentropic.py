# to write the flow conditions for an isentropic flow

import math

def Tt_T_ratio(M, gamma=1.4):
    """ Total-to-static temperature ratio """
    return 1 + (gamma - 1) / 2 * M**2

def Pt_P_ratio(M, gamma=1.4):
    """ Total-to-static pressure ratio """
    return (1 + (gamma - 1) / 2 * M**2) ** (gamma / (gamma - 1))

def M_from_pressure_ratio(Pt_P, gamma=1.4):
    """ Solve Mach from total-to-static pressure ratio (isentropic) """
    return math.sqrt((2 / (gamma - 1)) * ((Pt_P) ** ((gamma - 1) / gamma) - 1))

def a_from_T(T,gamma=1.4 , R=287):
    """ Speed of sound from static temperature [K] """
    return math.sqrt(gamma * R * T)

def stagnation_properties(T, P, M, gamma=1.4):
    """ Returns Tt, Pt for given static T, P, M """
    Tt = T * Tt_T_ratio(M, gamma)
    Pt = P * Pt_P_ratio(M, gamma)
    return Tt, Pt
