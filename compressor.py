# to code the engine compressor

# components/compressor.py
class CompressorBase:
    def process(self, state: dict, gas):
        raise NotImplementedError

class AxialCompressor(CompressorBase):
    def __init__(self, n_stages=8, pr_stage=1.28, eta_stage=0.88):
        self.n_stages = int(n_stages)
        self.pr_stage = float(pr_stage)
        self.eta_stage = float(eta_stage)

    def process(self, state, gas):
        gamma = gas.gamma
        cp = gas.cp
        pt_in = state['pt']
        Tt_in = state['Tt']

        pr_total = self.pr_stage ** self.n_stages
        # approximate overall efficiency
        eta_overall = 1 - (1 - self.eta_stage) ** self.n_stages
        # isentropic temp rise
        Tt_out = Tt_in * (1.0 + (pr_total ** ((gamma - 1.0) / gamma) - 1.0) / max(eta_overall, 1e-6))
        pt_out = pt_in * pr_total
        w_comp = cp * (Tt_out - Tt_in)  # J/kg_air

        out = dict(state)
        out.update({'pt': pt_out, 'Tt': Tt_out, 'w_comp': w_comp, 'pi_c': pr_total, 'eta_c': eta_overall})
        return out

class CentrifugalCompressor(CompressorBase):
    def __init__(self, n_stages=1, pr_stage=5.0, eta=0.82):
        self.n_stages = int(n_stages)
        self.pr_stage = float(pr_stage)
        self.eta = float(eta)

    def process(self, state, gas):
        gamma = gas.gamma
        cp = gas.cp
        pt_in = state['pt']
        Tt_in = state['Tt']

        pr_total = self.pr_stage ** self.n_stages
        Tt_out = Tt_in * (1.0 + (pr_total ** ((gamma - 1.0) / gamma) - 1.0) / max(self.eta, 1e-6))
        pt_out = pt_in * pr_total
        w_comp = cp * (Tt_out - Tt_in)

        out = dict(state)
        out.update({'pt': pt_out, 'Tt': Tt_out, 'w_comp': w_comp, 'pi_c': pr_total, 'eta_c': self.eta})
        return out
