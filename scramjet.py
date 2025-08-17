#scramjet engine

# engines/scramjet.py

from .ramjet import Ramjet
from Components.nozzle import Nozzle
from Physics.performance import thrust as compute_thrust, overall_efficiency


class Scramjet(Ramjet):
    def __init__(self, name="Scramjet", **kwargs):
        super().__init__(**kwargs)
        self.name = name
    
    def simulate(self, flight: dict, mdot_air: float, Tt4_target: float, verbose=False):
        # 1. Inlet (compresses to supersonic flow)
        # The inlet must be configured for supersonic flow
        
        inlet_state = self.inlet.process(flight, self.gas)
        
        # 2. Combustor (adds heat at supersonic speed, Tt rises)
        combust_state = self.combustor.process(inlet_state, self.gas, mdot_air, Tt4_target=Tt4_target)

        engine_state = {
            'mdot_air': mdot_air,
            'flight': flight,
            'p_ambient': flight['p0'],
        }

        engine_state.update(inlet_state)
        engine_state.update(combust_state)
        

        V0 = flight['M0'] * (self.gas.gamma * self.gas.R * flight['T0'])**0.5
        engine_state['V0'] = V0
        
        # 3. Nozzle (expands hot supersonic flow)
        nozzle = Nozzle(mode="cd")
        
        
        mdot_fuel = engine_state['mdot_f']
        mdot_total = mdot_air + mdot_fuel
        
        engine_state['mdot'] = mdot_total
        engine_state['Pt'] = engine_state['pt']
        engine_state['Tt'] = engine_state['Tt']
        engine_state['p0'] = flight['p0']
        
        nozzle_state = nozzle.process(engine_state, self.gas)

        # 4. Calculate thrust
        V0 = flight['M0'] * (self.gas.gamma * self.gas.R * flight['T0'])**0.5
        Fnet = nozzle_state['Fg'] - mdot_air * V0
        
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