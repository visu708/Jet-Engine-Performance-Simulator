# to code the turbine of the engine
# components/turbine.py
class Turbine:
    """
    Simple turbine model: takes specific work required (J/kg of turbine working mass)
    and reduces Tt accordingly using turbine efficiency eta_t.
    process(state, gas, mdot_working, specific_work_required)
    """
    def __init__(self, eta_t=0.9, pt_loss_frac=0.03):
        self.eta_t = float(eta_t)
        self.pt_loss_frac = float(pt_loss_frac)

    def process(self, state, gas,  specific_work_required):
        # specific_work_required in J/kg_of_flow_through_turbine (W_dot / mdot_working)
        cp = gas.cp
        Tt_in = state['Tt']
        pt_in = state['pt']

        # temperature drop required (ideal)
        dTt_ideal = specific_work_required / cp
        # account for turbine efficiency (actual larger drop)
        dTt_actual = dTt_ideal / max(self.eta_t, 1e-6)
        Tt_out = Tt_in - dTt_actual
        if Tt_out <= 0:
            raise ValueError("Turbine: Tt_out nonphysical (too much work requested)")

        # approximate pressure ratio across turbine via isentropic relation:
        gamma = gas.gamma
        tau = Tt_out / Tt_in
        # approximate pt ratio (approx using isentropic efficiency)
        pt_out = pt_in * (tau ** (gamma / (gamma - 1.0))) * (1.0 - self.pt_loss_frac)

        out = dict(state)
        out.update({'pt': pt_out, 'Tt': Tt_out})
        return out
