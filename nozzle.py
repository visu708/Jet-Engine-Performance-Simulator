#to code nozzzle
# components/nozzle.py
from Physics.isentropic import Pt_P_ratio, Tt_T_ratio
from Physics.performance import thrust

class Nozzle:
    """
    Simple nozzle model:
    - Convergent for subsonic exit
    - Convergent-divergent option for supersonic
    """

    def __init__(self, eta=0.98, Ae=1.0, mode="convergent"):
        """
        Parameters:
        eta : nozzle efficiency (0 < eta <= 1)
        Ae : exit area [m^2]
        mode : 'convergent' or 'cd' (convergent-divergent)
        """
        self.eta = float(eta)
        self.Ae = float(Ae)
        self.mode = mode

    def process(self, flow: dict, gas):
        """
        Processes nozzle flow
        Input flow dict requires:
        - 'Pt' : total pressure [Pa]
        - 'Tt' : total temperature [K]
        - 'p0' : ambient pressure [Pa]
        - 'M'  : Mach number at nozzle exit guess (for CD nozzle)

        Returns: dict with
        - Pe : exit static pressure [Pa]
        - Te : exit static temperature [K]
        - Ve : exit velocity [m/s]
        - Fg : gross thrust [N]
        """
        Pt = flow["Pt"]
        Tt = flow["Tt"]
        p0 = flow["p0"]

        gamma = gas.gamma
        R = gas.R

        # Assume isentropic expansion until exit pressure = ambient
        # Exit Mach number (convergent nozzle -> max M=1 at throat)
        if self.mode == "convergent":
            Me = 1.0  # choke condition approx
        else:
            Me = flow.get("M", 2.0)  # allow supersonic exit guess

        # Exit temperature
        Te = Tt / Tt_T_ratio(Me, gamma)
        # Exit pressure
        Pe = Pt / Pt_P_ratio(Me, gamma)
        # Exit velocity
        Ve = (Me * (gamma * R * Te) ** 0.5) * self.eta

        # Thrust (gross only, no nozzle losses yet)
        Fg = thrust(flow["mdot"], Ve, flow["V0"], Pe, p0, self.Ae)

        return {
            "Pe": Pe,
            "Te": Te,
            "Ve": Ve,
            "Fg": Fg,
        }
