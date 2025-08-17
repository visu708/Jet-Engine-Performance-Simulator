# to code the thermodynamic parameters
import math

# ---- constants (defaults for dry air, Jet-A) ----
AIR_GAMMA = 1.4
AIR_R = 287.0          # J/(kg·K)
AIR_CP = AIR_GAMMA * AIR_R / (AIR_GAMMA - 1.0)  # 1004.5 J/(kg·K) approx
JET_A_LHV = 43e6       # J/kg

def cp_const():
    return AIR_CP

def gamma_const():
    return AIR_GAMMA

def R_const():
    return AIR_R

# optional mild T-dependence (safe default: constant). you can refine later.
def cp_of_T(T: float) -> float:
    """Return cp [J/(kg·K)] for air. Start constant; swap to NASA poly later."""
    return AIR_CP

def gamma_of_T(T: float) -> float:
    """Return gamma for air. Start constant; swap to T-dependent later."""
    return AIR_GAMMA

def mixture_cp_gamma(mass_fractions: dict, cp_map: dict, gamma_map: dict):
    """
    Simple mass-fraction mix of cp and gamma (rough, but OK for early stages).
    mass_fractions: {'air':0.97, 'fuel_vapour':0.03}
    cp_map, gamma_map: property dicts for each species.
    """
    cp = sum(mass_fractions[k] * cp_map[k] for k in mass_fractions)
    g  = sum(mass_fractions[k] * gamma_map[k] for k in mass_fractions)
    return cp, g

def fuel_LHV():
    return JET_A_LHV

def heat_addition_Tt(Tt_in: float, mdot_air: float, mdot_fuel: float, LHV: float = JET_A_LHV, cp: float = AIR_CP, eta_b: float = 0.98):
    """
    Compute target Tt_out after adding mdot_fuel to mdot_air at efficiency eta_b.
    """
    mdot_tot = mdot_air + mdot_fuel
    if mdot_tot <= 0:
        raise ValueError("Total mass flow must be > 0")
    dTt = eta_b * mdot_fuel * LHV / (mdot_tot * cp)
    return Tt_in + dTt