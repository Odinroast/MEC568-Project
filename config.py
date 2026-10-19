"""Task 2: all physical constants, design inputs, and numerical settings.

The Earth/Moon constants come from Section 4.5 of the project handout.
Distances are km, time is s, spacecraft mass is kg, and angles are radians
inside the simulation. Inputs explicitly ending in _m_s or _deg use those units.
"""
from dataclasses import dataclass
import numpy as np

# Required common constants. Compute the mean motion rather than rounding it.
MU_EARTH = 398600.4418       # km^3/s^2
MU_MOON = 4902.800          # km^3/s^2
R_EARTH = 6378.137          # km
R_MOON = 1737.4            # km
MOON_ORBIT_RADIUS = 384400.0  # km
MEAN_MOTION = np.sqrt((MU_EARTH + MU_MOON) / MOON_ORBIT_RADIUS**3)
MASS_RATIO = MU_MOON / (MU_EARTH + MU_MOON)
G0 = 9.80665               # m/s^2, used only in the rocket equation
HOUR = 3600.0
DAY = 86400.0


@dataclass(frozen=True)
class Settings:
    """Editable choices, separated from fixed physical constants.

    The handout permits an impulsive TLI. That is the model used here.
    The 72 h arrival target is our design choice, not a historical Apollo epoch.
    Mass/Isp inputs are illustrative propulsion assumptions. They do not claim
    to reconstruct the masses or performance of a flown Saturn/Apollo stage.
    """
    parking_altitude_km: float = 185.0
    target_lunar_altitude_km: float = 110.0
    target_arrival_time_h: float = 72.0
    mass_before_tli_kg: float = 45000.0
    tli_specific_impulse_s: float = 421.0
    loi_specific_impulse_s: float = 314.0
    captured_orbit_duration_h: float = 24.0

    # Initial guesses for a numerical solve, NOT precomputed final answers.
    tli_guess_m_s: float = 3150.0
    moon_phase_guess_deg: float = 130.0

    reference_rtol: float = 1e-12  # handout requires <= 1e-10
    reference_atol: float = 1e-13
    rk4_step_s: float = 10.0
    convergence_steps_s: tuple = (40.0, 20.0, 10.0, 5.0)
    maximum_coast_days: float = 6.0
