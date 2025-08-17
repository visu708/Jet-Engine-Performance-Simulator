# to calculate all the variables about the engine performance

def thrust(mdot: float, V_exit: float, V0: float, p_exit: float, p0: float, A_exit: float):
    """F = m_dot*(Ve - V0) + (pe - p0)*Ae"""
    return mdot * (V_exit - V0) + (p_exit - p0) * A_exit

def specific_thrust(F: float, mdot_air: float):
    return F / mdot_air

def tsfc(mdot_fuel: float, thrust: float):
    """Thrust specific fuel consumption [kg/(N·s)]"""
    if thrust <= 0:
        return float("inf")
    return mdot_fuel / thrust

def propulsive_efficiency(V0: float, Ve: float):
    if Ve <= 0:
        return 0.0
    return 2 * V0 / (V0 + Ve)

def overall_efficiency(thrust: float, V0: float, mdot_fuel: float, LHV: float):
    """η_o = (thrust * V0) / (mdot_fuel * LHV)"""
    denom = mdot_fuel * LHV
    if denom <= 0:
        return 0.0
    return thrust * V0 / denom


def thermal_efficiency(Tt_in: float, Tt_out: float):
    """η_t = (Tt_out - Tt_in) / Tt_in"""
    if Tt_in <= 0:
        return 0.0
    return (Tt_out - Tt_in) / Tt_in

def isentropic_efficiency(Tt_in: float, Tt_out: float, Pt_in: float, Pt_out: float):
    """η_is = (Tt_out / Tt_in) * (Pt_in / Pt_out)"""
    if Tt_in <= 0 or Pt_out <= 0:
        return 0.0
    return (Tt_out / Tt_in) * (Pt_in / Pt_out)

import numpy as np 
def standard_atmosphere(altitude):
    # Simplified ISA model
    if altitude < 11000:  # Troposphere
        T = 288.15 - 0.0065 * altitude   # K
        P = 101325 * (T / 288.15) ** 5.2561
    else:  # Lower Stratosphere
        T = 216.65
        P = 22632 * np.exp(-9.81 * (altitude - 11000) / (287 * T))
    
    rho = P / (287 * T)
    return T, P, rho
