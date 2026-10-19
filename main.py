"""MEC 568: common Tasks 1-8, then Task 9 / Scenario A (Apollo 11).

Run: python main.py
Only NumPy, SciPy, and Matplotlib are required. No presentation/PDF code.

Read main() at the bottom first. Each task has one clearly named function.
Shared equations, integrators, and plotting live in small supporting modules.
"""
import argparse
import csv
import json
import platform
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import least_squares

from config import Settings, MU_EARTH, MU_MOON, R_EARTH, R_MOON, HOUR
from dynamics import (
    TASK_1_EXPLANATION, parking_state, departure_state, apply_impulse,
    coast_derivative, to_moon_frame, to_rotating_frame, from_rotating_frame,
    jacobi_constant,
)
from numerics import rk4, reference_coast, integrate_to_encounter, rk4_lunar_minimum
import plots


def write_csv(path, rows):
    """Small output helper: write named columns, not unlabeled numeric arrays."""
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def task_1_theoretical_background():
    """Task 1: explain rocket momentum, every force term, and the indirect term."""
    print(TASK_1_EXPLANATION)


def task_2_initial_conditions(settings):
    """Task 2: define the parking state, mass, departure impulse, and lunar phase.

    A two-variable shooting solve determines delta-v and phase to satisfy our
    chosen 110 km arrival and 72 h coast. Those are design targets, not copied
    mission values. Numerical work here uses the Task 4 functions in numerics.py.
    The physical baseline is subsequently propagated separately in Task 5.
    """
    def residual(parameters):
        delta_v_m_s, phase_deg = parameters
        encounter = integrate_to_encounter(
            settings, delta_v_m_s, np.deg2rad(phase_deg), targeting_trial=True,
        )
        # Scaling gives both residuals comparable influence on the root solve.
        altitude_residual = (encounter.altitude_km-settings.target_lunar_altitude_km)/1000
        time_residual = encounter.time_s/HOUR-settings.target_arrival_time_h
        return np.array([altitude_residual, time_residual])

    fit = least_squares(
        residual, [settings.tli_guess_m_s, settings.moon_phase_guess_deg],
        bounds=([3100.0, 100.0], [3300.0, 170.0]), x_scale=[10.0, 1.0],
        diff_step=1e-5, xtol=1e-11, ftol=1e-11, gtol=1e-10, max_nfev=100,
    )
    errors = residual(fit.x)
    if not fit.success or abs(errors[0])*1000 > 0.01 or abs(errors[1])*HOUR > 0.1:
        raise RuntimeError(f'TLI targeting failed: {fit.message}, residuals={errors}')

    delta_v_m_s, phase_deg = map(float, fit.x)
    phase_rad = float(np.deg2rad(phase_deg))
    before = parking_state(settings)
    after = departure_state(settings, delta_v_m_s)
    result = {
        'parking_altitude_km': settings.parking_altitude_km,
        'parking_state_before_TLI': before.tolist(),
        'state_immediately_after_TLI': after.tolist(),
        'state_columns': ['x_km', 'y_km', 'vx_km_s', 'vy_km_s', 'mass_kg'],
        'TLI_delta_v_m_s': delta_v_m_s,
        'moon_phase_deg': phase_deg,
        'TLI_propellant_kg': float(before[4]-after[4]),
        'propulsion_inputs_are_illustrative_assumptions': True,
    }
    print(f'Task 2: TLI={delta_v_m_s:.6f} m/s, lunar phase={phase_deg:.6f} deg')
    return delta_v_m_s, phase_rad, after, result


def task_3_reference_frames(initial_state, phase_rad):
    """Task 3: justify frames and verify the complete forward/inverse transform.

    ECI: all propagation uses one consistent Earth-relative force model.
    MCI: translate position AND velocity to measure the encounter and design LOI.
    Rotating barycentric: visualize Earth-Moon geometry with fixed primaries.
    We transform data for analysis; we do not switch ODE force models mid-flight.
    """
    position, velocity = to_rotating_frame(0.0, initial_state, phase_rad)
    recovered_position, recovered_velocity = from_rotating_frame(0.0, position, velocity, phase_rad)
    position_error = float(np.linalg.norm(recovered_position-initial_state[:2]))
    velocity_error = float(np.linalg.norm(recovered_velocity-initial_state[2:4]))
    if position_error > 1e-8 or velocity_error > 1e-10:
        raise RuntimeError('Task 3 frame transformation round trip failed')
    print('Task 3: ECI propagation, MCI encounter/LOI, rotating-frame display.')
    return {'initial_position_roundtrip_error_km': position_error,
            'initial_velocity_roundtrip_error_km_s': velocity_error}


def task_4_numerical_method(settings):
    """Task 4: own RK4 in numerics.rk4; tight independent DOP853 reference.

    The actual numerical comparison is Task 7 / V2-V3, after a coast exists.
    Using a library interpolator for event refinement does not replace RK4.
    """
    if settings.reference_rtol > 1e-10:
        raise ValueError('Reference relative tolerance violates the handout')
    print(f'Task 4: own RK4 h={settings.rk4_step_s:g} s; DOP853 rtol={settings.reference_rtol:g}.')


def task_5_baseline(settings, delta_v_m_s, phase_rad):
    """Task 5: single impulsive TLI followed by UNPOWERED coast to the Moon.

    This baseline ends immediately before lunar orbit insertion. It satisfies
    Tasks 1-8 independently of the subsequent Scenario A capture maneuver.
    """
    encounter = integrate_to_encounter(settings, delta_v_m_s, phase_rad)
    if encounter.event != 'closest_approach':
        raise RuntimeError(f'Nominal baseline hit a surface: {encounter.event}')
    if not 100.0 <= encounter.altitude_km <= 10000.0:
        raise RuntimeError('Baseline lunar altitude is outside the required 100-10000 km')
    print(f'Task 5: lunar altitude={encounter.altitude_km:.6f} km, TOF={encounter.time_s/HOUR:.6f} h.')
    return encounter


def task_6_figures_and_history(directory, encounter, phase_rad):
    """Task 6 / Section 5.5(a)-(d): generate required baseline plots and CSV.

    No slides are generated. Figures are normal numerical simulation outputs.
    Coast mass is constant because TLI is impulsive, as the handout permits.
    """
    plots.baseline_figures(directory, encounter, phase_rad)
    times = np.linspace(0, encounter.time_s, 4000)
    states = encounter.solution.sol(times).T
    rows = [dict(time_s=float(t), x_km=float(y[0]), y_km=float(y[1]),
                 vx_km_s=float(y[2]), vy_km_s=float(y[3]), mass_kg=float(y[4]))
            for t, y in zip(times, states)]
    write_csv(directory/'task6_baseline_history.csv', rows)

    # Task 3 verification on the FULL coast, not just the initial state.
    position, velocity = to_rotating_frame(times, states, phase_rad)
    recovered_position, recovered_velocity = from_rotating_frame(times, position, velocity, phase_rad)
    frame_position_error = float(np.max(np.linalg.norm(recovered_position-states[:, :2], axis=1)))
    frame_velocity_error = float(np.max(np.linalg.norm(recovered_velocity-states[:, 2:4], axis=1)))
    jacobi = jacobi_constant(times, states, phase_rad)
    jacobi_drift = float(np.max(np.abs(jacobi-jacobi[0])))
    if frame_position_error > 1e-7 or frame_velocity_error > 1e-10 or jacobi_drift > 1e-6:
        raise RuntimeError('Full-coast frame/Jacobi accuracy check failed')
    print('Task 6: ECI, rotating, distance, speed/mass plots and trajectory CSV saved.')
    return {'full_coast_position_roundtrip_error_km': frame_position_error,
            'full_coast_velocity_roundtrip_error_km_s': frame_velocity_error,
            'maximum_absolute_Jacobi_drift': jacobi_drift}


def task_7_verification(settings, directory, delta_v_m_s, phase_rad, encounter):
    """Task 7: complete the three verification tests in Section 5.4."""
    # V1: turn off BOTH lunar acceleration terms and propagate ten Earth orbits.
    circular_initial = parking_state(settings)
    radius = np.linalg.norm(circular_initial[:2])
    angular_speed = np.sqrt(MU_EARTH/radius**3)
    period = 2*np.pi/angular_speed
    derivative = lambda t, y: coast_derivative(t, y, phase_rad, include_moon=False)
    times, states = rk4(derivative, circular_initial, 0.0, 10*period, settings.rk4_step_s)
    analytic_position = radius*np.column_stack((np.cos(angular_speed*times), np.sin(angular_speed*times)))
    position_error = np.linalg.norm(states[:, :2]-analytic_position, axis=1)
    energy = np.sum(states[:, 2:4]**2, axis=1)/2-MU_EARTH/np.linalg.norm(states[:, :2], axis=1)
    exact_energy = -MU_EARTH/(2*radius)
    relative_energy_error = np.abs((energy-exact_energy)/exact_energy)
    plots.two_body_figure(directory, times/period, relative_energy_error, position_error)

    # V2: same departure, four RK4 step sizes. Refine the event between steps.
    derivative = lambda t, y: coast_derivative(t, y, phase_rad)
    initial = departure_state(settings, delta_v_m_s)
    convergence = []
    for step_s in settings.convergence_steps_s:
        times, states = rk4(derivative, initial, 0.0, encounter.time_s+900.0, step_s)
        event_time, altitude = rk4_lunar_minimum(times, states, phase_rad, encounter.time_s)
        convergence.append({
            'step_s': step_s, 'lunar_altitude_km': altitude,
            'time_to_closest_approach_h': event_time/HOUR,
            'error_against_reference_km': abs(altitude-encounter.altitude_km),
            'altitude_change_on_halving_km': None, 'observed_order': None,
        })
    for coarse, fine in zip(convergence[:-1], convergence[1:]):
        coarse['altitude_change_on_halving_km'] = fine['lunar_altitude_km']-coarse['lunar_altitude_km']
        coarse['observed_order'] = float(np.log(coarse['error_against_reference_km']/fine['error_against_reference_km'])
                                         / np.log(coarse['step_s']/fine['step_s']))

    # V3: the production RK4 step must agree with the library result within 1 km.
    production = next(row for row in convergence if row['step_s']==settings.rk4_step_s)
    v3_pass = production['error_against_reference_km'] < 1.0
    orders = [row['observed_order'] for row in convergence[:-1]]
    if not v3_pass:
        raise RuntimeError('V3 failed: RK4 altitude differs from reference by >=1 km')
    if not all(3.5 < order < 4.5 for order in orders):
        raise RuntimeError(f'V2 did not demonstrate approximately fourth order: {orders}')
    plots.convergence_figure(directory, convergence)
    write_csv(directory/'task7_convergence.csv', convergence)
    print('Task 7: V1 complete; V2 orders='+', '.join(f'{p:.3f}' for p in orders))
    print(f'        V3 difference={production["error_against_reference_km"]*1000:.4f} m (<1000 m).')
    return {
        'V1_maximum_position_error_km': float(position_error.max()),
        'V1_maximum_relative_energy_error': float(relative_energy_error.max()),
        'V2_convergence': convergence, 'V3_pass': v3_pass,
    }


def task_8_sensitivity(settings, directory, delta_v_m_s, phase_rad, nominal):
    """Task 8: independent +/-1 m/s TLI and +/-0.5 degree phase perturbations.

    Do NOT rerun the targeting optimizer for these cases: that would remove the
    errors we are trying to measure. Impact cases stop at the lunar surface.
    Their reported zero altitude is physical surface contact, not periapsis.
    """
    cases = [('Nominal', 0.0, 0.0), ('TLI -1 m/s', -1.0, 0.0),
             ('TLI +1 m/s', 1.0, 0.0), ('Phase -0.5 deg', 0.0, -0.5),
             ('Phase +0.5 deg', 0.0, 0.5)]
    rows = []
    for name, delta_error_m_s, phase_error_deg in cases:
        encounter = integrate_to_encounter(settings, delta_v_m_s+delta_error_m_s,
                                           phase_rad+np.deg2rad(phase_error_deg))
        if encounter.event == 'earth_impact':
            raise RuntimeError('Perturbation returned to Earth before lunar encounter')
        rows.append({
            'case': name, 'TLI_error_m_s': delta_error_m_s, 'phase_error_deg': phase_error_deg,
            'event': encounter.event, 'lunar_altitude_km': encounter.altitude_km,
            'altitude_change_km': encounter.altitude_km-nominal.altitude_km,
            'time_to_event_h': encounter.time_s/HOUR,
        })
    write_csv(directory/'task8_sensitivity.csv', rows)
    plots.sensitivity_figure(directory, rows)
    explanation = (
        'Small departure errors accumulate over a multi-day coast and change lunar encounter geometry. '
        'Tracking and midcourse corrections are needed to control arrival altitude and capture conditions. '
        'Impact cases stop at altitude zero; their event time is contact time, not an underground periapsis.'
    )
    print('Task 8: sensitivity complete. '+explanation)
    return {'cases': rows, 'interpretation': explanation}


def task_9_scenario_a(settings, directory, nominal, phase_rad):
    """Task 9 / Scenario A: Apollo 11 style insertion into a ~110 km lunar orbit.

    At periapsis, Moon-relative radial velocity is zero. A retrograde impulse
    sets the tangential speed to sqrt(muM/rp), making an initially circular
    osculating lunar orbit. Restore the Moon's velocity before ECI propagation.
    We retain Earth gravity and the indirect term for a 24 h captured coast.
    """
    position, velocity = to_moon_frame(nominal.time_s, nominal.state, phase_rad)
    radius = np.linalg.norm(position)
    radial_unit = position/radius
    tangent = velocity-np.dot(velocity, radial_unit)*radial_unit
    tangent /= np.linalg.norm(tangent)
    circular_velocity = np.sqrt(MU_MOON/radius)*tangent
    impulse = circular_velocity-velocity
    delta_v_m_s = 1000*np.linalg.norm(impulse)
    after = apply_impulse(nominal.state, impulse, settings.loi_specific_impulse_s)

    end_s = nominal.time_s+settings.captured_orbit_duration_h*HOUR
    capture = reference_coast(settings, after, phase_rad, nominal.time_s, end_s)
    times = np.linspace(nominal.time_s, end_s, 5000)
    states = capture.sol(times).T
    relative_position, _ = to_moon_frame(times, states, phase_rad)
    altitudes = np.linalg.norm(relative_position, axis=1)-R_MOON
    specific_energy = np.dot(circular_velocity, circular_velocity)/2-MU_MOON/radius
    eccentricity_vector = ((np.dot(circular_velocity, circular_velocity)-MU_MOON/radius)*position
                           - np.dot(position, circular_velocity)*circular_velocity)/MU_MOON
    eccentricity = float(np.linalg.norm(eccentricity_vector))
    if specific_energy >= 0 or eccentricity > 1e-9 or altitudes.min() <= 0:
        raise RuntimeError('Scenario A did not produce a safe, initially circular bound orbit')

    # Published values: NASA Apollo 11 Mission Report, Nov. 1969, Table 7-V.
    # Source: https://www.nasa.gov/wp-content/uploads/static/apollo50th/pdf/A11_MissionReport.pdf
    # 1 international foot = 0.3048 m. The historical FIRST burn entered an
    # ellipse; a SECOND burn changed the orbit. Our one-burn circular target
    # therefore differs from either individual historical burn.
    historical_first_m_s = 2917.5*0.3048
    historical_second_m_s = 158.8*0.3048
    comparison = {
        'source': 'NASA Apollo 11 Mission Report, November 1969, Table 7-V',
        'source_url': 'https://www.nasa.gov/wp-content/uploads/static/apollo50th/pdf/A11_MissionReport.pdf',
        'first_capture_burn_m_s': historical_first_m_s,
        'later_circularization_burn_m_s': historical_second_m_s,
        'sum_of_historical_burn_magnitudes_m_s': historical_first_m_s+historical_second_m_s,
        'model_minus_historical_first_m_s': float(delta_v_m_s-historical_first_m_s),
        'model_minus_historical_sum_m_s': float(delta_v_m_s-historical_first_m_s-historical_second_m_s),
        'interpretation': 'Different arrival states, target orbits, and impulsive versus finite burns prevent an exact historical match.',
    }
    plots.capture_figures(directory, times, states, phase_rad)
    write_csv(directory/'task9A_capture_history.csv', [
        dict(time_since_TLI_s=float(t), time_since_LOI_s=float(t-times[0]),
             x_km=float(y[0]), y_km=float(y[1]), vx_km_s=float(y[2]),
             vy_km_s=float(y[3]), mass_kg=float(y[4]), lunar_altitude_km=float(alt))
        for t, y, alt in zip(times, states, altitudes)
    ])
    print(f'Task 9 / A: LOI={delta_v_m_s:.6f} m/s, captured altitude '
          f'{altitudes.min():.6f} to {altitudes.max():.6f} km over 24 h.')
    return {
        'scenario': 'A - Apollo 11', 'LOI_delta_v_m_s': float(delta_v_m_s),
        'LOI_vector_ECI_km_s': impulse.tolist(), 'state_after_LOI': after.tolist(),
        'LOI_propellant_kg': float(nominal.state[4]-after[4]),
        'pre_LOI_Moon_relative_speed_km_s': float(np.linalg.norm(velocity)),
        'post_LOI_Moon_relative_speed_km_s': float(np.linalg.norm(circular_velocity)),
        'initial_lunar_eccentricity': eccentricity,
        'initial_lunar_specific_energy_km2_s2': float(specific_energy),
        'initial_lunar_period_h': float(2*np.pi*np.sqrt(radius**3/MU_MOON)/HOUR),
        'capture_duration_h': settings.captured_orbit_duration_h,
        'minimum_captured_altitude_km': float(altitudes.min()),
        'maximum_captured_altitude_km': float(altitudes.max()),
        'historical_comparison': comparison,
    }


def main():
    """Follow the handout: eight common tasks, then ONE assigned scenario task."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parent/'results',
                        help='Directory for generated numerical figures and data')
    args = parser.parse_args()
    directory = args.output.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    settings = Settings()
    started = time.perf_counter()

    # ------------------- COMMON BASELINE: TASKS 1-8 -------------------
    task_1_theoretical_background()
    delta_v, phase, initial, initial_summary = task_2_initial_conditions(settings)
    frames = task_3_reference_frames(initial, phase)
    task_4_numerical_method(settings)
    baseline = task_5_baseline(settings, delta_v, phase)
    frames.update(task_6_figures_and_history(directory, baseline, phase))
    verification = task_7_verification(settings, directory, delta_v, phase, baseline)
    sensitivity = task_8_sensitivity(settings, directory, delta_v, phase, baseline)

    # ------------------- ASSIGNED SCENARIO: TASK 9 --------------------
    scenario = task_9_scenario_a(settings, directory, baseline, phase)

    # Section 5.5: the required ONE-LINE class summary for the outbound baseline.
    # Propellant here is TLI propellant. LOI propellant is reported separately.
    write_csv(directory/'class_summary.csv', [{
        'parking_altitude_km': settings.parking_altitude_km,
        'TLI_delta_v_m_s': delta_v,
        'TLI_propellant_kg_assumed_mass_and_Isp': initial_summary['TLI_propellant_kg'],
        'time_to_lunar_closest_approach_h': baseline.time_s/HOUR,
        'lunar_closest_approach_altitude_km': baseline.altitude_km,
        'integrators': 'DOP853 reference; own RK4 comparison',
        'RK4_step_s': settings.rk4_step_s,
        'DOP853_rtol': settings.reference_rtol,
    }])
    summary = {
        'scope': 'Common Tasks 1-8 plus Task 9 / Scenario A (Apollo 11)',
        'settings': asdict(settings), 'task2_initial_conditions': initial_summary,
        'task3_frame_checks': frames,
        'task5_baseline': {'lunar_altitude_km': baseline.altitude_km, 'time_of_flight_h': baseline.time_s/HOUR},
        'task7_verification': verification, 'task8_sensitivity': sensitivity,
        'task9_scenario_A': scenario,
        'environment': {'python': platform.python_version(), 'numpy': np.__version__, 'scipy': scipy.__version__},
        'runtime_s': time.perf_counter()-started,
    }
    (directory/'summary.json').write_text(json.dumps(summary, indent=2))
    print(f'Finished in {summary["runtime_s"]:.1f} s. Results: {directory}')


if __name__ == '__main__':
    main()
