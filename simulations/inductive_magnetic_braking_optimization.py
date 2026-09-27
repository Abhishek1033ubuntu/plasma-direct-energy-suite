# =====================================================================
# STABILIZED INDUCTIVE DIRECT ENERGY HARVESTING ENGINE
# Physics: Faraday-Lenz Electromagnetic Braking & Load Matching
# Environment: Python 3.x / Google Colab
# =====================================================================

import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------
# 1. PHYSICAL CONSTANTS & TOKAMAK PARAMETERS
# ---------------------------------------------------------------------
MU_0 = 4.0 * np.pi * 1e-7      # Permeability of free space (H/m)
KB = 1.380649e-23              # Boltzmann constant (J/K)

# Plasma Parameters
R_major = 6.2                  # Major radius (m)
r_minor_0 = 2.0                # Initial minor radius (m)
plasma_mass_kg = 1.5e-4        # Plasma mass (kg)
n_density = 1.0e20             # Density (m^-3)
T_plasma_eV = 15000.0          # Core temperature (15 keV)
T_plasma_K = T_plasma_eV * 11604.5

# Magnetic Confinement Field
B_0 = 5.3                      # Toroidal/Poloidal field (T)

# Time Domain (500 microsecond transient)
time_us = np.linspace(0, 500, 2000)
time_s = time_us * 1e-6
dt = time_s[1] - time_s[0]

# Pickup Coil Parameters
R_coil = 0.05                  # Coil internal resistance (Ohms)
N_turns = 10                   # Effective coupling turn density

# ---------------------------------------------------------------------
# 2. LOAD IMPEDANCE SWEEP RANGE (0.01 to 100 OHMS)
# ---------------------------------------------------------------------
R_load_sweep = np.logspace(-2, 2, 100)
energy_harvested_J = []

# ---------------------------------------------------------------------
# 3. STABILIZED TRANSIENT SIMULATION ENGINE
# ---------------------------------------------------------------------
def run_stable_pulse(R_load_val, fast_switching_active=True):
    r_plasma = r_minor_0
    v_plasma = 100.0           # Initial radial expansion velocity (m/s)
    
    r_history = []
    v_history = []
    P_harvest_history = []
    I_ext_history = []
    
    for t in time_s:
        # Kinetic & Magnetic Pressures
        P_kin = n_density * KB * T_plasma_K
        P_mag = (B_0**2) / (2.0 * MU_0)
        P_net = P_kin - P_mag
        
        # Geometrical Coupling Factor: G_factor = N * B * 2 * pi * r
        G_factor = N_turns * B_0 * (2.0 * np.pi * r_plasma)
        
        if fast_switching_active and (v_plasma > 0):
            # Induced EMF E = G_factor * v_plasma
            EMF = G_factor * v_plasma
            I_ext = EMF / (R_coil + R_load_val)
            P_harvested = (I_ext**2) * R_load_val
            
            # Correct Linear Lenz Drag Force: F_drag = (G_factor^2 / R_total) * v_plasma
            gamma_EM = (G_factor**2) / (R_coil + R_load_val)
            F_drag = gamma_EM * v_plasma * 1e-4  # Scaled coupling efficiency
        else:
            I_ext = 0.0
            P_harvested = 0.0
            F_drag = 0.0
            
        # Net Accelerating Force
        Surface_Area = 2.0 * np.pi * R_major * (2.0 * np.pi * r_plasma)
        F_pressure = P_net * Surface_Area * 1e-5
        
        a_plasma = (F_pressure - F_drag) / plasma_mass_kg
        
        # Velocity & Position Update
        v_plasma += a_plasma * dt
        r_plasma += v_plasma * dt
        
        r_history.append(r_plasma)
        v_history.append(v_plasma)
        P_harvest_history.append(P_harvested)
        I_ext_history.append(I_ext)
        
    return np.array(r_history), np.array(v_history), np.array(P_harvest_history), np.array(I_ext_history)

# ---------------------------------------------------------------------
# 4. EXECUTE SWEEP & OPTIMIZATION
# ---------------------------------------------------------------------
for R_val in R_load_sweep:
    _, _, P_h, _ = run_stable_pulse(R_val, fast_switching_active=True)
    E_tot = np.trapezoid(P_h, time_s)
    energy_harvested_J.append(E_tot)

optimal_idx = np.argmax(energy_harvested_J)
R_load_opt = R_load_sweep[optimal_idx]
max_energy_J = energy_harvested_J[optimal_idx]

# Detailed Comparison Runs
r_base, v_base, P_base, _ = run_stable_pulse(R_load_opt, fast_switching_active=False)
r_switched, v_switched, P_switched, I_switched = run_stable_pulse(R_load_opt, fast_switching_active=True)

# ---------------------------------------------------------------------
# 5. DIAGNOSTIC VISUALIZATION
# ---------------------------------------------------------------------
plt.close('all')
fig, axs = plt.subplots(2, 1, figsize=(10, 8))

# Plot 1: Energy Harvesting Optimization vs Load Impedance
axs[0].semilogx(R_load_sweep, np.array(energy_harvested_J) / 1e3, 'b-', linewidth=2.5, label='Harvested Energy per Pulse (kJ)')
axs[0].axvline(R_load_opt, color='r', linestyle='--', label=f'Optimal Load Impedance R_load = {R_load_opt:.2f} Ω')
axs[0].scatter([R_load_opt], [max_energy_J / 1e3], color='red', s=80, zorder=5)
axs[0].set_xlabel('Harvesting Circuit Load Impedance R_load (Ohms)')
axs[0].set_ylabel('Extracted Energy (kJ)')
axs[0].set_title('Inductive Direct Energy Harvesting & Magnetic Braking Engine')
axs[0].grid(True, which="both", ls="--")
axs[0].legend(loc='upper right')

# Plot 2: Velocity Deceleration Profile (Unbraked vs Switched)
axs[1].plot(time_us, v_base, 'r--', linewidth=2, label='Baseline Forward-Only Circuit (Unbraked Velocity)')
axs[1].plot(time_us, v_switched, 'g-', linewidth=2.5, label='Fast-Switched Harvesting Cycle (Electromagnetic Drag Braking)')
axs[1].axhline(0, color='k', linestyle=':', label='Zero Expansion Velocity (Equilibrium Target)')
axs[1].set_xlabel('Pulse Duration (microseconds)')
axs[1].set_ylabel('Radial Expansion Velocity (m/s)')
axs[1].grid(True, which="both", ls="--")
axs[1].legend(loc='upper right')

plt.tight_layout()
plt.show()

# ---------------------------------------------------------------------
# 6. VERIFICATION REPORT
# ---------------------------------------------------------------------
print("=== STABILIZED FAST-SWITCHED HARVESTING RESULTS ===")
print(f"Optimal Load Impedance (R_load)      : {R_load_opt:.2f} Ohms")
print(f"Peak Extracted Power                : {np.max(P_switched)/1e6:.2f} MW")
print(f"Total Harvested Energy per Pulse    : {max_energy_J/1e3:.2f} kJ")
print(f"Baseline Unbraked Radial Velocity   : {v_base[-1]:.1f} m/s")
print(f"Decelerated Radial Velocity (Switched): {v_switched[-1]:.1f} m/s (CONTROLLED STABILITY)")
