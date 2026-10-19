"""Tasks 1-3: equations of motion, impulses, initial state, and reference frames.

State = [x, y, vx, vy, mass], with km, km/s, kg units. The Moon moves on the
required circular orbit. Coasts use the complete Earth-centered equation (1).
"""
import numpy as np
from config import (
    MU_EARTH, MU_MOON, R_EARTH, MOON_ORBIT_RADIUS,
    MEAN_MOTION, MASS_RATIO, G0,
)

TASK_1_EXPLANATION = """
TASK 1: Rocket mechanics and the indirect lunar term
r is spacecraft position relative to Earth; v = dr/dt; m is spacecraft mass.
rM is Moon position relative to Earth; rho = r-rM is Moon-relative position.
muE and muM are the Earth/Moon gravitational parameters G*M.

Earth-centered equation:
  dv/dt = -muE*r/|r|^3
          -muM*((r-rM)/|r-rM|^3 + rM/|rM|^3) + (T/m)*u
  dr/dt = v; dm/dt = -mdot; T = mdot*Ve; Ve = Isp*g0.
Here mdot > 0 is outgoing propellant flow, T is thrust magnitude, u is its
unit direction, Ve is effective exhaust speed, and Isp is specific impulse.

(a) A rocket is an open system: exhaust removes momentum. Accounting for this
momentum flux gives m*dv/dt = F_gravity + T*u. Writing d(m*v)/dt = F_gravity
alone omits the exhaust flux and is not the rocket momentum balance.

(b) Earth accelerates toward the Moon by muM*rM/|rM|^3. Subtracting Earth's
acceleration when forming spacecraft position relative to Earth gives the
negative indirect term. Without it, the relative equation is inconsistent.

This project uses instantaneous TLI and LOI impulses. Between impulses T=0
and dm/dt=0. At each impulse, delta-v = Isp*g0*ln(m_before/m_after). A finite
burn time/mass-flow history is therefore not simulated or required here.
"""


def moon_state(time_s, phase_rad):
    """Task 2: Moon position and velocity, updated at every ODE stage.

    Supports a scalar time or a 1-D array. Returned vectors have shape (2,)
    for a scalar and (n_times, 2) for an array.
    """
    angle = MEAN_MOTION * np.asarray(time_s) + phase_rad
    position = MOON_ORBIT_RADIUS * np.stack((np.cos(angle), np.sin(angle)), axis=-1)
    velocity = MEAN_MOTION * np.stack((-position[..., 1], position[..., 0]), axis=-1)
    return position, velocity


def coast_derivative(time_s, state, phase_rad, include_moon=True):
    """Task 1: equation (1) during an unpowered coast.

    Earth's direct gravity, Moon's direct gravity, and the indirect term are
    separate below so their physical meanings remain visible. Spacecraft mass
    cancels from gravitational acceleration. It stays in the state for clarity.
    include_moon=False turns off BOTH lunar terms for verification test V1.
    """
    position = state[:2]
    velocity = state[2:4]
    earth_acceleration = -MU_EARTH * position / np.linalg.norm(position)**3
    acceleration = earth_acceleration

    if include_moon:
        moon_position, _ = moon_state(time_s, phase_rad)
        relative_position = position - moon_position
        lunar_direct = -MU_MOON * relative_position / np.linalg.norm(relative_position)**3
        lunar_indirect = -MU_MOON * moon_position / MOON_ORBIT_RADIUS**3
        acceleration = acceleration + lunar_direct + lunar_indirect

    return np.array([velocity[0], velocity[1], acceleration[0], acceleration[1], 0.0])


def parking_state(settings):
    """Task 2: circular 185 km parking orbit BEFORE the departure impulse."""
    radius = R_EARTH + settings.parking_altitude_km
    circular_speed = np.sqrt(MU_EARTH / radius)
    return np.array([radius, 0.0, 0.0, circular_speed, settings.mass_before_tli_kg])


def apply_impulse(state_before, delta_velocity_km_s, specific_impulse_s):
    """Tasks 1-2: instant velocity change and rocket-equation mass decrease.

    Position is continuous. Convert km/s to m/s because G0 is in m/s^2.
    No burn-duration or gravity-loss approximation is hidden in this function.
    """
    delta_velocity = np.asarray(delta_velocity_km_s, dtype=float)
    delta_v_m_s = 1000.0 * np.linalg.norm(delta_velocity)
    state_after = state_before.copy()
    state_after[2:4] += delta_velocity
    state_after[4] *= np.exp(-delta_v_m_s / (specific_impulse_s * G0))
    return state_after


def departure_state(settings, delta_v_m_s):
    """Task 5: single tangential, prograde impulsive TLI from the parking orbit."""
    return apply_impulse(
        parking_state(settings), [0.0, delta_v_m_s / 1000.0],
        settings.tli_specific_impulse_s,
    )


def to_moon_frame(time_s, earth_state, phase_rad):
    """Task 3: parallel-axis MCI translation, rho=r-rM and v_rel=v-vM."""
    moon_position, moon_velocity = moon_state(time_s, phase_rad)
    return earth_state[..., :2] - moon_position, earth_state[..., 2:4] - moon_velocity


def to_rotating_frame(time_s, earth_state, phase_rad):
    """Task 3: ECI to barycentric Earth-Moon rotating POSITION AND VELOCITY.

    alpha = n*t+phase; R(-alpha) rotates inertial axes into rotating axes.
    q = R*r - (mu*a, 0).
    q_dot = R*v - n cross (R*r).
    The time derivative of the rotation is essential for velocity/Jacobi checks.
    """
    angle = MEAN_MOTION * np.asarray(time_s) + phase_rad
    cosine, sine = np.cos(angle), np.sin(angle)
    position, velocity = earth_state[..., :2], earth_state[..., 2:4]
    rotated_position = np.stack((
        cosine * position[..., 0] + sine * position[..., 1],
        -sine * position[..., 0] + cosine * position[..., 1],
    ), axis=-1)
    rotated_velocity = np.stack((
        cosine * velocity[..., 0] + sine * velocity[..., 1],
        -sine * velocity[..., 0] + cosine * velocity[..., 1],
    ), axis=-1)
    spin_velocity = MEAN_MOTION * np.stack(
        (-rotated_position[..., 1], rotated_position[..., 0]), axis=-1,
    )
    return (rotated_position - np.array([MASS_RATIO * MOON_ORBIT_RADIUS, 0.0]),
            rotated_velocity - spin_velocity)


def from_rotating_frame(time_s, position, velocity, phase_rad):
    """Task 3 verification: invert BOTH the origin shift and velocity transform."""
    earth_relative_rotated = position + np.array([MASS_RATIO * MOON_ORBIT_RADIUS, 0.0])
    spin_velocity = MEAN_MOTION * np.stack(
        (-earth_relative_rotated[..., 1], earth_relative_rotated[..., 0]), axis=-1,
    )
    rotated_inertial_velocity = velocity + spin_velocity
    angle = MEAN_MOTION * np.asarray(time_s) + phase_rad
    cosine, sine = np.cos(angle), np.sin(angle)

    def rotate_back(vector):
        return np.stack((cosine * vector[..., 0] - sine * vector[..., 1],
                         sine * vector[..., 0] + cosine * vector[..., 1]), axis=-1)

    return rotate_back(earth_relative_rotated), rotate_back(rotated_inertial_velocity)


def jacobi_constant(time_s, earth_state, phase_rad):
    """Task 3 accuracy check: dimensionless CR3BP Jacobi C, valid on each coast.

    Length unit=a and velocity unit=n*a. C changes across a powered impulse.
    Earth-centered orbital energy is NOT conserved when the moving Moon acts.
    """
    position, velocity = to_rotating_frame(time_s, earth_state, phase_rad)
    position = position / MOON_ORBIT_RADIUS
    velocity = velocity / (MEAN_MOTION * MOON_ORBIT_RADIUS)
    x, y = position[..., 0], position[..., 1]
    earth_distance = np.sqrt((x + MASS_RATIO)**2 + y**2)
    moon_distance = np.sqrt((x - 1.0 + MASS_RATIO)**2 + y**2)
    return (x*x + y*y + 2.0 * (1.0 - MASS_RATIO) / earth_distance
            + 2.0 * MASS_RATIO / moon_distance - np.sum(velocity**2, axis=-1))
