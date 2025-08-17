# turbojet engine

# engines/turbojet.py

from Components.inlet import Inlet
from Components.compressor import CompressorBase
from Components.combustor import Combustor
from Components.turbine import Turbine
from Components.nozzle import Nozzle
from Physics.performance import thrust as compute_thrust, overall_efficiency
from Physics.thermodynamics import fuel_LHV, cp_const, R_const, gamma_const

class Turbojet:
    def __init__(self, name="Turbojet", inlet=None, compressor=None, combustor=None, turbine=None, nozzle=None, gas=None):
        self.name = name
        self.inlet = inlet or Inlet()
        self.compressor = compressor
        self.combustor = combustor or Combustor()
        self.turbine = turbine or Turbine()
        self.nozzle = nozzle or Nozzle()
        self.gas = gas or self._create_default_gas()
        

        
        if not isinstance(self.compressor, CompressorBase):
            raise TypeError("compressor must be an instance of a Compressor class.")

    def _create_default_gas(self):
        # A simple class to hold gas properties
        class Gas:
            def __init__(self):
                self.cp = cp_const()
                self.R = R_const()
                self.gamma = gamma_const()
        return Gas()

    def simulate(self, flight: dict, mdot_air: float, Tt4_target: float, verbose=False):
        """
        Simulates the entire turbojet engine cycle.

        Args:
            flight (dict): Dictionary with flight conditions (M0, p0, T0).
            mdot_air (float): Air mass flow rate [kg/s].
            Tt4_target (float): Target total temperature at turbine inlet [K].
            verbose (bool): If True, prints detailed state properties at each stage.
        """
        # Engine state object to pass between stages
        engine_state = {
            'mdot_air': mdot_air,
            'flight': flight,
            'p_ambient': flight['p0'],
        }

        # 1. Inlet
        inlet_state = self.inlet.process(flight, self.gas)
        engine_state.update(inlet_state)
        if verbose: print(f"Stage 1 (Inlet): {engine_state}")

        # 2. Compressor
        comp_state = self.compressor.process(engine_state, self.gas)
        engine_state.update(comp_state)
        w_comp = comp_state['w_comp']
        if verbose: print(f"Stage 2 (Compressor): {engine_state}")

        # 3. Combustor
        combust_state = self.combustor.process(engine_state, self.gas, mdot_air=mdot_air, Tt4_target=Tt4_target)
        engine_state.update(combust_state)
        mdot_fuel = combust_state['mdot_f']
        if verbose: print(f"Stage 3 (Combustor): {engine_state}")

        # 4. Turbine
        mdot_total = mdot_air + mdot_fuel
        specific_turb_work = w_comp * mdot_air / mdot_total
        turbine_state = self.turbine.process(engine_state, self.gas, specific_work_required=specific_turb_work)
        engine_state.update(turbine_state)
        if verbose: print(f"Stage 4 (Turbine): {engine_state}")

        # 5. Nozzle

        # Calculate V0 first to be included in the state dictionary
        V0 = flight['M0'] * (self.gas.gamma * self.gas.R * flight['T0'])**0.5
        engine_state['V0'] = V0  # Add V0 to the dictionary



        engine_state['mdot'] = mdot_total
        engine_state['Pt'] = engine_state['pt'] # Use a consistent key
        engine_state['Tt'] = engine_state['Tt']
        engine_state['p0'] = flight['p0']
        
        nozzle_state = self.nozzle.process(engine_state, self.gas)
        engine_state.update(nozzle_state)
        
        # Calculate gross thrust
        V0 = flight['M0'] * (self.gas.gamma * self.gas.R * flight['T0'])**0.5
        engine_state['V0'] = V0
        Fnet = compute_thrust(mdot=mdot_total, V_exit=nozzle_state['Ve'], V0=V0, 
                              p_exit=nozzle_state['Pe'], p0=flight['p0'], A_exit=self.nozzle.Ae)
        
        tsfc = mdot_fuel / Fnet if Fnet != 0 else float('inf')
        eta_o = overall_efficiency(thrust=Fnet, V0=V0, mdot_fuel=mdot_fuel, LHV=self.combustor.LHV)
        
        results = {
            'F_net_N': Fnet,
            'TSFC': tsfc,
            'mdot_fuel': mdot_fuel,
            'mdot_air': mdot_air,
            'eta_overall': eta_o,
            'states': engine_state
        }
        
        if verbose:
            print(f"\nSimulation Results:")
            print(f"Net Thrust: {Fnet:.2f} N")
            print(f"TSFC: {tsfc:.6f} kg/(N·s)")
            print(f"Overall Efficiency: {eta_o:.2%}")
        
        return results