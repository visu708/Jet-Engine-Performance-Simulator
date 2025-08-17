#afterburner

def nozzle_thrust(m_dot, T_t, P_t, P_amb, gamma, R, afterburner=False):
    """
    Nozzle thrust calculation with optional afterburner.
    
    m_dot : mass flow rate (kg/s)
    T_t   : total temperature before nozzle (K)
    P_t   : total pressure before nozzle (Pa)
    P_amb : ambient pressure (Pa)
    gamma : specific heat ratio
    R     : gas constant (J/kgK)
    afterburner : bool, if True adds extra energy
    
    Returns: thrust (N), exit velocity (m/s)
    """
    # Increase temperature if afterburner is ON
    if afterburner:
        T_t *= 1.2  # Example: 20% higher total temperature
        P_t *= 0.95 # Slight pressure loss in AB

    # Nozzle exit velocity (isentropic assumption)
    V_e = (2 * gamma / (gamma - 1) * R * T_t * 
           (1 - (P_amb / P_t)**((gamma - 1)/gamma)))**0.5

    # Thrust
    F = m_dot * V_e + (P_t - P_amb)

    return F, V_e




