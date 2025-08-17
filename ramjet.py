#ramjet engine

# engines/ramjet.py

from .turbojet import Turbojet
from Components.inlet import Inlet
from Components.combustor import Combustor
from Components.nozzle import Nozzle
from Physics.thermodynamics import fuel_LHV, cp_const, R_const, gamma_const
from Physics.performance import thrust as compute_thrust, overall_efficiency

class Ramjet:
    def __init__(self, name="Ramjet", inlet=None, combustor=None, nozzle=None, gas=None):
        self.name = name
        self.inlet = inlet or Inlet()
        self.combustor = combustor or Combustor()
        self.nozzle = nozzle or Nozzle()
        self.gas = gas or self._create_default_gas()
    
    def _create_default_gas(self):
        # A simple class to hold gas properties
        class Gas:
            def __init__(self):
                self.cp = cp_const()
                self.R = R_const()
                self.gamma = gamma_const()
        return Gas()

    def simulate(self, flight: dict, mdot_air: float, Tt4_target: float, verbose=False):
        engine_state = {
            'mdot_air': mdot_air,
            'flight': flight,
            'p_ambient': flight['p0'],
        }

        # 1. Inlet (compresses air via ram effect)
        inlet_state = self.inlet.process(flight, self.gas)
        engine_state.update(inlet_state)
        
        # 2. Combustor (adds heat)
        combust_state = self.combustor.process(engine_state, self.gas, mdot_air, Tt4_target=Tt4_target)
        engine_state.update(combust_state)
        mdot_fuel = combust_state['mdot_f']

        V0 = flight['M0'] * (self.gas.gamma * self.gas.R * flight['T0'])**0.5
        engine_state['V0'] = V0 

        # 3. Nozzle (expands hot gas)
        mdot_total = mdot_air + mdot_fuel
        engine_state['mdot'] = mdot_total
        engine_state['Pt'] = engine_state['pt']
        engine_state['Tt'] = engine_state['Tt']
        engine_state['p0'] = flight['p0']
        
        nozzle_state = self.nozzle.process(engine_state, self.gas)
        
        # 4. Calculate thrust
        V0 = flight['M0'] * (self.gas.gamma * self.gas.R * flight['T0'])**0.5
        Fnet = compute_thrust(mdot=mdot_total, V_exit=nozzle_state['Ve'], V0=V0, 
                              p_exit=nozzle_state['Pe'], p0=flight['p0'], A_exit=self.nozzle.Ae)
        
        tsfc = mdot_fuel / Fnet if Fnet != 0 else float('inf')
        eta_o = overall_efficiency(Fnet, V0, mdot_fuel, self.combustor.LHV)

        results = {
            'F_net_N': Fnet,
            'TSFC': tsfc,
            'mdot_fuel': mdot_fuel,
            'mdot_air': mdot_air,
            'eta_overall': eta_o,
        }

        if verbose:
            print(f"\nSimulation Results:")
            print(f"Net Thrust: {Fnet:.2f} N")
            print(f"TSFC: {tsfc:.6f} kg/(N·s)")
            print(f"Overall Efficiency: {eta_o:.2%}")
        
        return results