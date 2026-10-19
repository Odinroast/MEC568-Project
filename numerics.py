"""Task 4: our RK4 implementation and the independent SciPy reference solver.

The reference and RK4 share a physical force function, but NOT a stepping
algorithm. Lunar minima are found continuously instead of taking sampled minima.
"""
from dataclasses import dataclass
import numpy as np
from scipy.integrate import solve_ivp
from scipy.interpolate import CubicHermiteSpline
from scipy.optimize import brentq
from config import DAY, R_EARTH, R_MOON
from dynamics import coast_derivative, departure_state, to_moon_frame


@dataclass
class Encounter:
    """Reference solution and the first physical event reached during departure."""
    solution: object
    time_s: float
    state: np.ndarray
    altitude_km: float
    event: str  # 'closest_approach', 'moon_impact', or 'earth_impact'


def rk4(derivative, initial_state, start_s, end_s, step_s):
    """Task 4: classical, fixed-step, fourth-order Runge-Kutta, written explicitly.

    Only the final step can be shorter, so the requested final time is exact.
    The method integrates any state vector, including the constant mass state.
    """
    if step_s <= 0 or end_s <= start_s:
        raise ValueError('RK4 requires positive step and end time after start time')
    count = int(np.ceil((end_s - start_s) / step_s))
    times = start_s + step_s * np.arange(count + 1)
    times[-1] = end_s
    states = np.empty((count + 1, len(initial_state)))
    states[0] = initial_state

    for index in range(count):
        time = times[index]
        state = states[index]
        step = times[index + 1] - time
        k1 = derivative(time, state)
        k2 = derivative(time + step/2, state + step*k1/2)
        k3 = derivative(time + step/2, state + step*k2/2)
        k4 = derivative(time + step, state + step*k3)
        states[index + 1] = state + step * (k1 + 2*k2 + 2*k3 + k4) / 6

    return times, states


def reference_coast(settings, initial_state, phase_rad, start_s, end_s, events=None):
    """Task 4: tight-tolerance DOP853 reference, with dense output for events."""
    solution = solve_ivp(
        lambda time, state: coast_derivative(time, state, phase_rad),
        (start_s, end_s), initial_state, method='DOP853',
        rtol=settings.reference_rtol, atol=settings.reference_atol,
        dense_output=True, events=events, max_step=900.0,
    )
    if not solution.success:
        raise RuntimeError(solution.message)
    return solution


def integrate_to_encounter(settings, delta_v_m_s, phase_rad, targeting_trial=False):
    """Tasks 5,8: departure coast ending at lunar periapsis OR surface impact.

    Physical baseline/sensitivity runs stop at a surface. An impact's minimum
    physical altitude is zero; we do not report a fictitious underground flyby.
    During numerical targeting ONLY, surface termination can be disabled to
    keep the optimization residual smooth. Accepted final runs must be physical.
    """
    def closest_approach(time, state):
        position, velocity = to_moon_frame(time, state, phase_rad)
        return np.dot(position, velocity)

    def moon_surface(time, state):
        position, _ = to_moon_frame(time, state, phase_rad)
        return np.linalg.norm(position) - R_MOON

    def earth_surface(time, state):
        return np.linalg.norm(state[:2]) - R_EARTH

    closest_approach.direction = 1
    closest_approach.terminal = True
    moon_surface.direction = -1
    moon_surface.terminal = True
    earth_surface.direction = -1
    earth_surface.terminal = True
    events = [closest_approach] if targeting_trial else [closest_approach, moon_surface, earth_surface]

    solution = reference_coast(
        settings, departure_state(settings, delta_v_m_s), phase_rad,
        0.0, settings.maximum_coast_days * DAY, events,
    )
    found = [(times[0], index) for index, times in enumerate(solution.t_events) if len(times)]
    if not found:
        raise RuntimeError('No lunar encounter or impact within the coast time limit')
    time, event_index = min(found)
    state = solution.sol(time)
    relative_position, _ = to_moon_frame(time, state, phase_rad)
    altitude = float(np.linalg.norm(relative_position) - R_MOON)
    event_name = ['closest_approach', 'moon_impact', 'earth_impact'][event_index]
    if event_name == 'moon_impact':
        altitude = 0.0  # remove numerical root noise at surface contact
    return Encounter(solution, float(time), state, altitude, event_name)


def rk4_lunar_minimum(times, states, phase_rad, expected_time_s):
    """Task 7: event refinement between RK4 steps, preserving fourth-order accuracy.

    Interpolate POSITION using endpoint positions and velocities. Its derivative
    supplies velocity consistently. A sampled distance minimum would add O(h^2)
    error and can obscure the expected RK4 convergence order.
    """
    position_spline = CubicHermiteSpline(times, states[:, :2], states[:, 2:4])

    def radial_product(time):
        from dynamics import moon_state
        moon_position, moon_velocity = moon_state(time, phase_rad)
        position = position_spline(time) - moon_position
        velocity = position_spline(time, 1) - moon_velocity
        return np.dot(position, velocity)

    index = np.searchsorted(times, expected_time_s)
    lower = times[max(0, index - 8)]
    upper = times[min(len(times) - 1, index + 8)]
    time = brentq(radial_product, lower, upper, xtol=1e-7)
    from dynamics import moon_state
    moon_position, _ = moon_state(time, phase_rad)
    altitude = np.linalg.norm(position_spline(time) - moon_position) - R_MOON
    return float(time), float(altitude)
