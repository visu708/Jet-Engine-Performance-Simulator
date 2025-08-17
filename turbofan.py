# turbofan engine

# engines/turbofan.py

from .turbojet import Turbojet
from Components.nozzle import Nozzle
from Physics.performance import thrust as compute_thrust, overall_efficiency

class Turbofan(Turbojet):
    def __init__(self, bypass_ratio, fan=None, **kwargs):
        super().__init__(**kwargs)
        self.bypass_ratio = float(bypass_ratio)
        self.fan = fan
        self.name = f"Turbofan (BPR={self.bypass_ratio})"

    def simulate(self, flight: dict, mdot_air: float, Tt4_target: float, verbose=False):
        # 1. Separate mass flows
        mdot_core = mdot_air / (1 + self.bypass_ratio)
        mdot_bypass = mdot_air - mdot_core

        # 2. Process core stream (same as Turbojet)
        core_state = {
            'mdot_air': mdot_core,
            'flight': flight,
            'p_ambient': flight['p0'],
        }
        
        inlet_state = self.inlet.process(flight, self.gas)
        core_state.update(inlet_state)

        # Fan
        fan_state = self.fan.process(core_state, self.gas)
        core_state.update(fan_state)
        
        # Core components
        core_state.update(self.inlet.process(flight, self.gas))
        core_state.update(self.compressor.process(core_state, self.gas))
        core_state.update(self.combustor.process(core_state, self.gas, mdot_air=mdot_core, Tt4_target=Tt4_target))
        w_comp = core_state['w_comp']
        mdot_fuel = core_state['mdot_f']
        
        mdot_total_core = mdot_core + mdot_fuel
        # The specific work required by the fan and core compressor must be provided by the turbine
        w_fan = fan_state['w_comp'] # We can reuse w_comp key from fan process
        specific_turb_work = (w_comp * mdot_core + w_fan * mdot_air) / mdot_total_core
        
        turbine_state = self.turbine.process(core_state, self.gas, specific_work_required=specific_turb_work)
        core_state.update(turbine_state)

        # 3. Core Nozzle
        core_nozzle = Nozzle(Ae=self.nozzle.Ae)
        
        V0 = flight['M0'] * (self.gas.gamma * self.gas.R * flight['T0'])**0.5
        core_state['V0'] = V0



        core_state['mdot'] = mdot_total_core
        core_state['Pt'] = core_state['pt']
        core_state['Tt'] = core_state['Tt']
        core_state['p0'] = flight['p0']
        
        core_nozzle_res = core_nozzle.process(core_state, self.gas)
        
        # 4. Bypass Nozzle
        bypass_nozzle = Nozzle(Ae=self.nozzle.Ae * self.bypass_ratio)
        bypass_state = {
            'Pt': fan_state['pt'],
            'Tt': fan_state['Tt'],
            'p0': flight['p0'],
            'mdot': mdot_bypass,
        }
        bypass_state['V0'] = core_state['V0']
        
        bypass_nozzle_res = bypass_nozzle.process(bypass_state, self.gas)

        # 5. Combine thrusts
        V0 = flight['M0'] * (self.gas.gamma * self.gas.R * flight['T0'])**0.5

        Fnet_core = compute_thrust(mdot_total_core, core_nozzle_res['Ve'], V0, 
                                   core_nozzle_res['Pe'], flight['p0'], core_nozzle.Ae)
        Fnet_bypass = compute_thrust(mdot_bypass, bypass_nozzle_res['Ve'], V0,
                                     bypass_nozzle_res['Pe'], flight['p0'], bypass_nozzle.Ae)
        
        Fnet_total = Fnet_core + Fnet_bypass
        tsfc = mdot_fuel / Fnet_total if Fnet_total != 0 else float('inf')
        eta_o = overall_efficiency(Fnet_total, V0, mdot_fuel, self.combustor.LHV)

        results = {
            'F_net_N': Fnet_total,
            'TSFC': tsfc,
            'mdot_fuel': mdot_fuel,
            'mdot_air': mdot_air,
            'eta_overall': eta_o,
        }
        
        if verbose:
            print(f"\nSimulation Results:")
            print(f"Net Thrust (Total): {Fnet_total:.2f} N")
            print(f"Core Thrust: {Fnet_core:.2f} N, Bypass Thrust: {Fnet_bypass:.2f} N")
            print(f"TSFC: {tsfc:.6f} kg/(N·s)")
            print(f"Overall Efficiency: {eta_o:.2%}")
        
        return results