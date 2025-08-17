#inlet of engine
# components/inlet.py
from Physics.isentropic import Pt_P_ratio, Tt_T_ratio
from Physics.shocks import oblique_shock, normal_shock
class Inlet:
    """
    Simple inlet model:
    - mode: 'auto' | 'subsonic' | 'supersonic'
    - eta_sub: total-pressure recovery for subsonic inlet
    - ramps: list of ramp deflections (radians) for supersonic inlet (optional)
    """
    def __init__(self, mode='auto', eta_sub=0.99, ramps=None):
        self.mode = mode
        self.eta_sub = float(eta_sub)
        self.ramps = ramps or []

    def process(self, flight: dict, gas):
        M0 = float(flight['M0'])
        p0 = float(flight['p0'])
        T0 = float(flight['T0'])
        gamma = gas.gamma

        # stagnation upstream
        pt0 = p0 * Pt_P_ratio(M0, gamma)
        Tt0 = T0 * Tt_T_ratio(M0, gamma)

        mode = self.mode
        if mode == 'auto':
            mode = 'supersonic' if M0 > 1.0 else 'subsonic'

        if mode == 'subsonic':
            pt_after = pt0 * self.eta_sub
            # choose a design diffuser exit Mach (user could vary)
            M_exit = 0.5
            T_exit = Tt0 / Tt_T_ratio(M_exit, gamma)
            p_exit = pt_after / Pt_P_ratio(M_exit, gamma)
            return {'M': M_exit, 'p': p_exit, 'T': T_exit, 'pt': pt_after, 'Tt': Tt0}

        # SUPRSONIC simple model: apply oblique ramps (if any) then terminal normal shock
        M = M0
        pt = pt0
        p = p0
        T = T0

        # apply oblique ramps if provided
        for theta in self.ramps:
            try:
                res = oblique_shock(M, theta, gamma=gamma, weak=True)
            except Exception:
                # if detaches or failure -> fallback to terminal normal shock at upstream
                res = None
            if res:
                pt *= res['pt2_pt1']
                p *= res['p2_p1']
                T *= res['T2_T1']
                M = res['M2']
            else:
                break

        # terminal normal shock to get subsonic flow
        if M > 1.0:
            ns = normal_shock(M, gamma)
            pt *= ns['pt2_pt1']
            p *= ns['p2_p1']
            T *= ns['T2_T1']
            M = ns['M2']

        # diffuse to subsonic exit Mach (design)
        pt *= 0.99  # diffuser loss
        M_exit = 0.5
        T_exit = Tt0 / Tt_T_ratio(M_exit, gamma)
        p_exit = pt / Pt_P_ratio(M_exit, gamma)
        return {'M': M_exit, 'p': p_exit, 'T': T_exit, 'pt': pt, 'Tt': Tt0}
