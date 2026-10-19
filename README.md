# MEC 568 code: Tasks 1-8 + Task 9 / Scenario A

This is a fresh code-only implementation of the supplied project handout.
The scope is the eight common tasks followed by **Scenario A: Apollo 11 lunar orbit insertion**. The handout lists Apollo 13 as Scenario B; that separate scenario is not part of this rebuild.

## Run

Python 3.11 or newer is recommended.

```bash
python -m pip install -r requirements.txt
python main.py
```

The run creates a `results/` folder containing numerical figures, CSV data, and a JSON summary. To choose another output location:

```bash
python main.py --output ./my_results
```

Tested with Python 3.12.14, NumPy 2.3.5, SciPy 1.17.0, and Matplotlib 3.10.8. Measured runtime was about 34 seconds in the development environment; allow roughly 30-90 seconds depending on hardware. Exact versions and measured runtime are written to `results/summary.json`.

The ZIP contains source code and these run instructions only. There are no slides, PDF builders, report generators, or precomputed simulation results. Running the code generates the required numerical outputs.

## Read the code in this order

1. `main.py`: read `main()` at the bottom to see Tasks 1-9 in handout order. Then read each `task_...` function.
2. `config.py`: handout constants and editable assumptions.
3. `dynamics.py`: force equation, initial orbit, impulses, and frame transformations.
4. `numerics.py`: explicit own RK4, independent DOP853 reference, and event location.
5. `plots.py`: required scientific figures.

## Task locations

| Requirement | Main location |
|---|---|
| Task 1: rocket mechanics, exhaust momentum, indirect lunar term | `task_1_theoretical_background()` and `dynamics.py` |
| Task 2: initial position, velocity, mass, lunar phase | `task_2_initial_conditions()`, `config.py`, `parking_state()` |
| Task 3: frame choice and correct transformations | `task_3_reference_frames()`, frame functions in `dynamics.py`, full-coast checks in Task 6 |
| Task 4: own fixed-step RK4 and tight library integrator | `task_4_numerical_method()` and `numerics.py` |
| Task 5: one TLI and unpowered coast to lunar closest approach | `task_5_baseline()` |
| Task 6: required trajectory, distance, speed plots | `task_6_figures_and_history()` and `plots.py` |
| Task 7: V1 ten-orbit analytic test, V2 convergence, V3 <1 km cross-check | `task_7_verification()` |
| Task 8: independent +/-1 m/s and +/-0.5 degree errors | `task_8_sensitivity()` |
| Task 9: Scenario A lunar capture and published-value comparison | `task_9_scenario_a()` |
| Section 5.5 class summary row | `class_summary.csv`, written at the end of `main()` |

## Modeling choices

- Distances are km, time is s, and mass is kg. State order is `[x, y, vx, vy, mass]`.
- The Moon follows the required circular orbit and updates at every derivative evaluation.
- The Earth-relative equation includes both direct lunar gravity and the indirect term.
- Parking altitude is 185 km. TLI and LOI are impulses, as allowed in the handout.
- We choose a 110 km lunar encounter and a 72 hour outbound time. A numerical shooting solve determines TLI magnitude and initial lunar phase from those targets. These are design choices, not historical state reconstruction.
- The common baseline stops immediately before LOI. Tasks 1-8 do not include a capture burn. Task 9 then starts from that baseline arrival state and applies LOI.
- The 45000 kg initial mass and Isp values of 421 s for TLI and 314 s for LOI are explicit illustrative assumptions. They affect fuel bookkeeping, not the coast path. They do not reproduce flown Apollo/Saturn stage masses or performance.
- LOI initially produces a circular lunar two-body *osculating* orbit. Continuing the full Earth-Moon model introduces a small altitude variation through Earth tides.
- No atmosphere, finite burn, solar gravity, lunar harmonics, or oblateness is included. The optional bonus extensions are not implemented.

## Verification and impact handling

V1 disables both lunar terms and propagates the circular parking orbit for ten revolutions. It compares position with the exact circle and specific energy with its exact constant value.

V2 compares RK4 steps of 40, 20, 10, and 5 seconds. Cubic Hermite interpolation locates closest approach between steps, avoiding a sampled-distance minimum error. The CSV reports altitude changes on halving, absolute errors, and measured orders. The default run demonstrated orders about 4.13, 4.06, and 4.01.

V3 compares the 10-second RK4 lunar altitude with DOP853 at rtol=1e-12. The default difference was about 0.60 meters, below the required 1 km. The code checks this and raises an error if verification fails.

The reference trajectory supplies baseline plots; own RK4 independently reproduces its lunar arrival. Frame position/velocity round trips and Jacobi conservation provide additional consistency checks.

Sensitivity cases are never retargeted. A perturbed trajectory that reaches the Moon's surface stops there and reports `moon_impact`, zero minimum physical altitude, and contact time. It does not invent a negative-altitude flyby. Surface termination is disabled only for intermediate numerical targeting trials, and final nominal trajectories must pass the physical event checks.

## Historical comparison for Scenario A

`task_9_scenario_a()` contains the comparison values and their source: NASA's *Apollo 11 Mission Report*, November 1969, Table 7-V:
https://www.nasa.gov/wp-content/uploads/static/apollo50th/pdf/A11_MissionReport.pdf

Apollo 11's first insertion entered an ellipse; a later burn changed that orbit. The code compares the modeled direct circular insertion with the first historical burn and with the sum of both historical burn magnitudes, while explaining the different targets and assumptions. Our time origin is TLI, not launch.

## Outputs

`results/summary.json` records all inputs, initial states, frame checks, verification, sensitivity, LOI, historical comparison, environment, and runtime. The CSV files expose the class summary, baseline trajectory, convergence, sensitivity, and captured-orbit history. PNG figures have task numbers in their filenames.

AI assisted code development and verification. Review and understand the code before submitting; any eventual presentation must include the AI disclosure required by the handout.
