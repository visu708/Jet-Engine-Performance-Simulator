#turboshaft engine

# engines/turboshaft.py

from .turbojet import Turbojet
from Physics.performance import overall_efficiency

class Turboshaft(Turbojet):
    def __init__(self, mech_efficiency=0.9, **kwargs):
        super().__init__(**kwargs)
        self.mech_efficiency = mech_efficiency
        self.name = "Turboshaft"

    def simulate(self, flight: dict, mdot_air: float, Tt4_target: float, verbose=False):
        # 1. Run the core cycle
        turbojet_results = super().simulate(flight, mdot_air, Tt4_target, verbose=False)
        
        # 2. Extract ALL available turbine work as shaft power
        shaft_power = turbojet_results['states']['w_comp'] * mdot_air / self.turbine.eta_t
        shaft_power *= self.mech_efficiency
        
        mdot_fuel = turbojet_results['mdot_fuel']
        
        # 3. Overall efficiency is now power-based, not thrust-based
        eta_o = shaft_power / (mdot_fuel * self.combustor.LHV)
        
        results = {
            'shaft_power_W': shaft_power,
            'mdot_fuel': mdot_fuel,
            'mdot_air': mdot_air,
            'eta_overall': eta_o,
        }
        
        if verbose:
            print(f"\nSimulation Results:")
            print(f"Shaft Power: {shaft_power:.2f} W")
            print(f"Overall Efficiency: {eta_o:.2%}")
        
        return results