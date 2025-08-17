# ui cli file

# ui/cli.py

from Engines.turbojet import Turbojet
from Engines.turbofan import Turbofan
from Engines.turboprop import Turboprop
from Engines.turboshaft import Turboshaft
from Engines.ramjet import Ramjet
from Engines.scramjet import Scramjet

from Components.compressor import AxialCompressor, CentrifugalCompressor
from Physics.performance import standard_atmosphere

def get_engine_choice():
    """Presents a menu and gets the user's choice of engine."""
    print("--- Engine Simulator ---")
    print("Select an engine type to simulate:")
    print("1. Turbojet")
    print("2. Turbofan")
    print("3. Turboprop")
    print("4. Turboshaft")
    print("5. Ramjet")
    print("6. Scramjet")
    
    choice = input("Enter your choice (1-6): ")
    return choice

def _get_compressor_inputs():
    """Helper function to get compressor inputs."""
    comp_type = input("Compressor type (axial/centrifugal): ").lower()
    if comp_type == 'axial':
        n_stages = int(input("Number of stages: "))
        pr_stage = float(input("Pressure ratio per stage: "))
        eta_stage = float(input("Efficiency per stage: "))
        return AxialCompressor(n_stages=n_stages, pr_stage=pr_stage, eta_stage=eta_stage)
    elif comp_type == 'centrifugal':
        pr_stage = float(input("Pressure ratio: "))
        eta = float(input("Efficiency: "))
        return CentrifugalCompressor(pr_stage=pr_stage, eta=eta)
    return None

def get_simulation_inputs(engine_type):
    """
    Prompts the user for key simulation parameters.
    Returns a dictionary of validated inputs.
    """
    inputs = {}
    print("\n--- Enter Simulation Parameters ---")
    
    # Flight conditions (common to all engines)
    try:
        altitude = float(input("Enter flight altitude [m]: "))
        Mach_number = float(input("Enter Mach number: "))
        mdot_air = float(input("Enter air mass flow rate [kg/s]: "))
    except ValueError:
        print("Invalid input. Please enter a numerical value.")
        return None

    T0, p0, rho0 = standard_atmosphere(altitude)
    
    inputs['flight'] = {
        'altitude': altitude,
        'M0': Mach_number,
        'p0': p0,
        'T0': T0,
        'rho0': rho0
    }
    inputs['mdot_air'] = mdot_air

    # Engine-specific parameters
    if engine_type in ['Turbojet', 'Turbofan', 'Turboprop', 'Turboshaft']:
        Tt4_target = float(input("Enter target Tt4 (Turbine Inlet Temperature) [K]: "))
        inputs['Tt4_target'] = Tt4_target
    
    if engine_type in ['Turbojet', 'Turbofan', 'Turboprop', 'Turboshaft']:
        print("\n--- Compressor Parameters ---")
        inputs['compressor'] = _get_compressor_inputs()

    if engine_type == 'Turbofan':
        bypass_ratio = float(input("Enter bypass ratio (BPR): "))
        inputs['bypass_ratio'] = bypass_ratio
        
        print("\n--- Fan Parameters ---")
        fan_pr = float(input("Enter fan pressure ratio: "))
        fan_eta = float(input("Enter fan efficiency: "))
        inputs['fan'] = AxialCompressor(n_stages=1, pr_stage=fan_pr, eta_stage=fan_eta)
        
    if engine_type == 'Ramjet' or engine_type == 'Scramjet':
        Tt4_target = float(input("Enter target Tt4 (Combustor Exit Temperature) [K]: "))
        inputs['Tt4_target'] = Tt4_target

    return inputs

def display_results(results: dict):
    """Formats and prints the simulation results."""
    print("\n--- Simulation Complete! ---")
    print("Engine Performance:")

    if 'F_net_N' in results:
        print(f"Net Thrust: {results.get('F_net_N', 'N/A'):.2f} N")
        print(f"TSFC: {results.get('TSFC', 'N/A'):.6f} kg/(N·s)")
        print(f"Overall Efficiency: {results.get('eta_overall', 'N/A'):.2%}")
    
    if 'shaft_power_W' in results:
        print(f"Shaft Power: {results['shaft_power_W']:.2f} W")
        print(f"Overall Efficiency: {results.get('eta_overall', 'N/A'):.2%}")
    
    print(f"Air Mass Flow: {results.get('mdot_air', 'N/A'):.2f} kg/s")
    print(f"Fuel Mass Flow: {results.get('mdot_fuel', 'N/A'):.6f} kg/s")

    # Optional detailed output for each stage
    if 'states' in results:
        print("\nEngine State at Each Station:")
        for station, state_data in results['states'].items():
            if isinstance(state_data, dict):
                print(f"Station {station}:")
                for key, value in state_data.items():
                    if isinstance(value, (int, float)):
                        print(f"  - {key}: {value:.2f}")
                    else:
                        print(f"  - {key}: {value}")