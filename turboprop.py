# turboprop engine

# engines/turboprop.py

from .turbojet import Turbojet
from Components.nozzle import Nozzle
from Physics.performance import thrust as compute_thrust, overall_efficiency

class Turboprop(Turbojet):
    def __init__(self, prop_efficiency=0.85, **kwargs):
        super().__init__(**kwargs)
        self.prop_efficiency = prop_efficiency
        self.name = "Turboprop"

    def simulate(self, flight: dict, mdot_air: float, Tt4_target: float, verbose=False):
        # 1. Turbojet cycle (as a baseline)
        turbojet_results = super().simulate(flight, mdot_air, Tt4_target, verbose=False)
        
        # 2. Extract shaft power from turbine
        shaft_power = turbojet_results['states']['w_comp'] * mdot_air / self.turbine.eta_t # Assuming all available turbine work goes to shaft
        
        # 3. Calculate propeller thrust
        prop_thrust = self.prop_efficiency * shaft_power / (flight['M0'] * (self.gas.gamma * self.gas.R * flight['T0'])**0.5)
        
        # 4. Net thrust is sum of prop and jet thrust
        Fnet_jet = turbojet_results['F_net_N']
        Fnet_total = Fnet_jet + prop_thrust

        # 5. Recalculate performance metrics
        mdot_fuel = turbojet_results['mdot_fuel']
        V0 = flight['M0'] * (self.gas.gamma * self.gas.R * flight['T0'])**0.5
        tsfc = mdot_fuel / Fnet_total if Fnet_total > 0 else float('inf')
        eta_o = overall_efficiency(Fnet_total, V0, mdot_fuel, self.combustor.LHV)
        
        results = {
            'F_net_N': Fnet_total,
            'TSFC': tsfc,
            'mdot_fuel': mdot_fuel,
            'mdot_air': mdot_air,
            'eta_overall': eta_o,
            'F_prop_N': prop_thrust,
            'F_jet_N': Fnet_jet
        }
        
        if verbose:
            print(f"\nSimulation Results:")
            print(f"Net Thrust (Total): {Fnet_total:.2f} N")
            print(f"Propeller Thrust: {prop_thrust:.2f} N, Jet Thrust: {Fnet_jet:.2f} N")
            print(f"TSFC: {tsfc:.6f} kg/(N·s)")
            print(f"Overall Efficiency: {eta_o:.2%}")

        return results