# Combustor 

# components/combustor.py
from Physics.thermodynamics import fuel_LHV

class Combustor:
    """
    Simple combustor  Tt4_target (total temperature after combustion)  f_guess (fuel-air ratio).
    Returns mdot_f (kg/s) stored as 'mdot_f' in state.
    """
    def __init__(self, pt_loss_frac=0.06, eta_b=0.98, LHV=None):
        self.pt_loss_frac = float(pt_loss_frac)
        self.eta_b = float(eta_b)
        self.LHV = fuel_LHV() if LHV is None else float(LHV)

    def process(self, state, gas, mdot_air, Tt4_target=None, f_guess=None):
        cp = gas.cp
        pt_in = state['pt']
        Tt_in = state['Tt']

        if Tt4_target is None and f_guess is None:
            raise ValueError("Provide Tt4_target or f_guess for combustor")

        if Tt4_target is not None:
            Tt4 = float(Tt4_target)
            # solve for fuel mass flow (approx)
            # energy balance: (mdot_air+mdot_f)*cp*Tt4 = mdot_air*cp*Tt_in + eta_b*mdot_f*LHV
            # => mdot_f*(eta_b*LHV - cp*Tt4) = mdot_air*cp*(Tt4 - Tt_in)
            denom = (self.eta_b * self.LHV - cp * Tt4)
            if denom <= 0:
                raise ValueError("Requested Tt4 too high for given LHV/eta_b/cp")
            mdot_f = mdot_air * cp * (Tt4 - Tt_in) / denom
        else:
            f = float(f_guess)
            mdot_f = f * mdot_air
            Tt4 = Tt_in + self.eta_b * mdot_f * self.LHV / ((mdot_air + mdot_f) * cp)

        pt_out = pt_in * (1.0 - self.pt_loss_frac)
        out = dict(state)
        out.update({'pt': pt_out, 'Tt': Tt4, 'mdot_f': mdot_f})
        return out

