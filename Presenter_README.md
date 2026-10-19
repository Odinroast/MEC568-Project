# Presenter README: MEC 568 Scenario A

## What to use

Use `MEC568_ScenarioA_Slides.pdf` with this README and the latest verified notebook, `MEC568_Tasks1to8_ScenarioA.ipynb`.
This deck uses the rebuilt 72 h / 110 km design. Its LOI is 899.80 m/s. Earlier slides used a different departure design and different LOI numbers. Keep this deck and this README together.

The talk has 15 main slides and five appendix slides. Main-slide timing totals exactly 10 minutes. Appendix slides are for the two-minute Q&A and do not add speaking time to the main talk.

The final PDF slide contains six editable form fields for names and actual contributions. Open the PDF in a reader that supports forms, fill the fields, save it, and check that the completed slide displays correctly before submitting. The stated contributions must describe actual work, not just the speaking assignments below. The AI disclosure is on the final slide and should remain there.

## Three-presenter split

| Presenter | Main slides | Clock interval | Duration | Speaking responsibility |
|---|---|---|---|---|
| Presenter 1 | 1-6 | 0:00-3:20 | 3:20 | Problem, assumptions, frames, integration method, targeting |
| Presenter 2 | 7-10 | 3:20-6:40 | 3:20 | V1-V3 verification, baseline histories, sensitivity |
| Presenter 3 | 11-15 | 6:40-10:00 | 3:20 | Baseline summary, Scenario A capture, historical comparison, limits |

Replace Presenter 1-3 with your team members' names. All three members must study all sections because anyone may receive a question on any task.

## Required topic allocation

| Topic | Slides | Clock interval | Time |
|---|---|---|---|
| Problem and model | 1-4 | 0:00-2:00 | 2:00 |
| Method and verification | 5-8 | 2:00-5:00 | 3:00 |
| Baseline and sensitivity | 9-11 | 5:00-7:00 | 2:00 |
| Team scenario | 12-15 | 7:00-10:00 | 3:00 |

Presenter 3 gives the 20-second baseline-summary bridge before beginning the scenario section. This keeps the speakers balanced while preserving the requested topic timing.

## Rehearsal instructions

The scripts below are speaking drafts, not extra text to add to the slides. At an unhurried pace, leave time to point to the graph and pause after important numbers. Rehearse with a stopwatch. Change wording to sound natural while preserving the numerical claims and physical assumptions.

Target handoffs at 3:20 and 6:40. Finish the main talk at 10:00. Do not read the appendix during the main talk. During Q&A, keep answers around 20-30 seconds, then stop so the instructor can follow up.

## Slide-by-slide speaking notes

### Slide 1: Earth-to-Moon trajectory and lunar capture

**Presenter 1 · 20 seconds · 0:00-0:20**

Our project calculates an Earth-to-Moon trajectory and then adds Scenario A, an Apollo 11 style lunar orbit insertion. We first complete the common baseline and numerical checks. Then we use one retrograde burn to enter a lunar orbit near 110 kilometers.

**Point to:** The scope line separates common work from Scenario A.

### Slide 2: Initial conditions and design targets

**Presenter 1 · 30 seconds · 0:20-0:50**

We begin in a circular Earth orbit, 185 kilometers above the surface. We choose a lunar arrival altitude of 110 kilometers and a travel time of 72 hours after injection. The solver adjusts the departure velocity change and the Moon’s starting phase to meet those two targets. The Moon moves throughout the calculation.

**Point to:** Point to Earth, the spacecraft coast, and the Moon marker at arrival.

### Slide 3: Physics and the accelerating Earth origin

**Presenter 1 · 40 seconds · 0:50-1:30**

Earth and Moon gravity act during the coast. Because our coordinates follow Earth, we also subtract Earth’s acceleration toward the Moon. That is the indirect term in the equation. For a rocket, thrust accounts for the momentum carried away by exhaust. We model the burns as instantaneous velocity changes, so thrust is zero between burns and coast mass stays constant. The appendix gives the rocket equation and mass assumptions.

**Point to:** Indicate the final lunar term as the indirect term.

### Slide 4: Reference frames

**Presenter 1 · 30 seconds · 1:30-2:00**

We propagate the full flight in Earth-centered coordinates. Moon-centered coordinates describe the encounter and the capture burn. The rotating frame shown here makes Earth and Moon stay fixed. When changing frames, we transform both position and velocity. We checked the transformations by converting back and by checking Jacobi conservation along the unpowered coast.

**Point to:** Point to the fixed Earth and Moon in the rotating plot.

### Slide 5: Own RK4 and the library reference

**Presenter 1 · 50 seconds · 2:00-2:50**

We wrote the classical fourth-order Runge-Kutta method ourselves. Each step evaluates the acceleration four times, using intermediate estimates to improve the final update. Our comparison step is 10 seconds. We also solve the same equations with SciPy’s DOP853 method at a relative tolerance of ten to the minus twelve. Using the same force equation keeps the physics consistent, while the integration algorithms remain independent. We compare their lunar arrival results after checking an analytic orbit.

**Point to:** Explain the four stage evaluations, without reading every symbol aloud.

### Slide 6: Targeting the lunar encounter

**Presenter 1 · 30 seconds · 2:50-3:20**

The departure design has two unknowns: injection velocity change and the Moon’s initial phase angle. A shooting solve adjusts them until the altitude and time targets match. We locate closest approach using Moon-relative radial velocity, rather than simply taking the smallest plotted distance. That avoids a time-sampling error in the reported altitude. Presenter 2 will now show the verification results.

**Point to:** Point to the unknowns and the matching targets.

**Handoff line:** “Presenter 2 will now show the verification results.”

### Slide 7: V1: ten revolutions against an exact orbit

**Presenter 2 · 40 seconds · 3:20-4:00**

Our first test removes both lunar terms and turns off thrust. We propagate the circular parking orbit for ten revolutions with a 10-second RK4 step. We compare position against the exact circular solution and specific energy against its exact constant value. The maximum position error is about 0.315 meters. Relative energy error stays around four times ten to the minus ten. This checks the integrator, units, and force direction before the lunar problem.

**Point to:** Left: relative energy error. Right: position error.

### Slide 8: V2 and V3: convergence and agreement

**Presenter 2 · 60 seconds · 4:00-5:00**

Next, we repeat the lunar coast with RK4 steps of 40, 20, 10, and 5 seconds. Each time the step halves, the arrival-altitude error falls by about a factor of sixteen. The observed orders are 4.13, 4.06, and 4.01, which supports fourth-order convergence. At our 10-second comparison step, RK4 and DOP853 differ by only 0.596 meters in closest-approach altitude. The project allows one kilometer. We refine the event between RK4 samples using position and velocity, so a sampled minimum does not hide the integration accuracy.

**Point to:** Follow the convergence curve, then indicate the highlighted 10 s row.

### Slide 9: Baseline distance and speed histories

**Presenter 2 · 50 seconds · 5:00-5:50**

The baseline has one departure burn followed by an unpowered coast. As the spacecraft climbs away from Earth, its Earth-relative speed decreases. The distance to the moving Moon then falls toward the encounter. The upper graph distinguishes Earth surface altitude from Moon center distance. The spacecraft reaches 110 kilometers above the lunar surface at 72 hours after injection. Mass remains constant throughout this coast because the departure burn was impulsive. Lunar capture has not happened yet.

**Point to:** Upper panel: the two different distance definitions. Lower: ECI speed.

### Slide 10: Small departure errors change the encounter

**Presenter 2 · 50 seconds · 5:50-6:40**

For sensitivity, we change one departure input at a time and never retarget the disturbed case. We test injection errors of plus or minus one meter per second and lunar phase errors of plus or minus half a degree. The results are strongly asymmetric. Two cases hit the Moon, and the others raise the encounter altitude substantially. Surface-impact cases stop at zero physical altitude. This sensitivity explains why real missions use tracking and midcourse corrections. Presenter 3 will connect the baseline to lunar capture.

**Point to:** Point to the two red IMPACT labels, then the higher-altitude cases.

**Handoff line:** “Presenter 3 will connect the baseline to lunar capture.”

### Slide 11: Baseline summary before lunar capture

**Presenter 3 · 20 seconds · 6:40-7:00**

Before adding the scenario, our baseline uses a 3,156.24 meter-per-second departure impulse and reaches the Moon in 72 hours at 110 kilometers altitude. The fuel estimate depends on explicitly assumed mass and engine inputs. We now add Scenario A to this verified arrival state.

**Point to:** This is the same arrival state used in the capture calculation.

### Slide 12: Scenario A: the lunar capture impulse

**Presenter 3 · 60 seconds · 7:00-8:00**

Scenario A asks us to enter a lunar orbit near 110 kilometers. First, we subtract the Moon’s velocity to obtain the spacecraft’s Moon-relative arrival velocity. At closest approach, the radial component is essentially zero. We then reduce the tangential speed from about 2.529 to 1.629 kilometers per second, the local circular speed. That needs a retrograde velocity change of 899.80 meters per second. We add the Moon’s velocity back before continuing in Earth-centered coordinates. Immediately after the impulse, the lunar orbit has negative specific energy and almost zero osculating eccentricity.

**Point to:** Point to the pre-burn speed, circular speed, and LOI difference.

### Slide 13: The captured orbit stays near 110 km

**Presenter 3 · 45 seconds · 8:00-8:45**

We do more than calculate a burn magnitude. We propagate the post-burn spacecraft for 24 hours with Earth gravity and lunar gravity still active. The plot shows repeated revolutions around the Moon. The altitude stays between about 109.934 and 110.011 kilometers. A circular osculating orbit describes the state immediately after insertion. Earth’s tidal effect then causes the small variation seen during the three-body propagation. The initial orbital period is about 1.98 hours.

**Point to:** Point to the insertion marker and the small range of propagated altitudes.

### Slide 14: Comparison with Apollo 11

**Presenter 3 · 45 seconds · 8:45-9:30**

NASA’s mission report gives about 889.25 meters per second for Apollo 11’s first lunar insertion, followed by a later circularization maneuver. The two maneuver magnitudes sum to about 937.66 meters per second. Our 899.80 meter-per-second result is for a direct circular insertion. These are different orbit targets and burn models, so we should not expect an exact historical match. The comparison shows a similar scale of velocity change, not a claim that our simplified design improves the flown mission.

**Point to:** Distinguish the historical first capture from the two-burn scalar budget.

### Slide 15: What the model establishes

**Presenter 3 · 30 seconds · 9:30-10:00**

The project demonstrates a consistent Earth-to-Moon coast, a verified numerical solution, and a successful idealized lunar capture. Its main limits are the planar circular lunar model, instantaneous burns, and assumed propulsion inputs. Real ephemerides, finite burns, and additional gravity effects would improve mission realism. Our notebook reproduces the calculations and figures. We are ready for questions.

**Point to:** End the main talk at 10:00. Use appendix slides only if asked.

## Appendix map

- Slide 16: full position and velocity transformations for ECI, MCI, and rotating barycentric frames.
- Slide 17: rocket equation, variable definitions, and assumed mass/engine inputs.
- Slide 18: complete class-summary row, integrator step, and tolerance.
- Slide 19: numerical and historical sources.
- Slide 20: editable team contributions and final-slide AI disclosure.

## Q&A preparation for all three presenters

**1. Why is there an indirect lunar term?**
Our coordinates follow Earth, which accelerates toward the Moon. Relative acceleration equals spacecraft acceleration minus Earth's acceleration. That subtraction produces the indirect term.

**2. Why is m dv/dt valid for a rocket while d(mv)/dt = gravity alone is not?**
A rocket is an open system. Exhaust carries momentum away. The thrust term accounts for that flux. Writing the derivative of spacecraft momentum equal to gravity alone omits the exhaust contribution.

**3. Does the code use your own RK4 or only SciPy?**
Both. We explicitly implemented the four RK4 stages. DOP853 supplies a tight reference trajectory. We compare lunar arrival altitude using four RK4 step sizes. At 10 s, the difference is 0.596 m.

**4. What does fourth-order convergence mean?**
For sufficiently small steps, the global error scales approximately with h to the fourth power. Halving h should therefore reduce error by roughly 16. Our observed orders are 4.13, 4.06, and 4.01.

**5. Why locate an event between time steps?**
Closest approach is a radial-velocity zero crossing. Taking the lowest sampled distance can miss the true minimum and add an error unrelated to the ODE solver's intended order. We use a position/velocity Hermite interpolation to refine that event for RK4.

**6. Why is Earth-centered energy not constant with the Moon present?**
The moving Moon exchanges energy with the spacecraft in that frame. The Jacobi constant is conserved for an unpowered coast in the circular restricted three-body model. Our full-coast absolute Jacobi drift is about 1.02e-10.

**7. Why do impact cases have zero altitude?**
Physical trajectories stop when they reach the lunar surface. Zero is surface contact. It is not a prediction of a harmless flyby or of a negative-altitude orbit. Contact times differ from hypothetical subsurface periapsis times.

**8. Why does LOI use Moon-relative velocity?**
The target orbit is around the Moon. We subtract Moon velocity before calculating the burn, then add it back to form the new Earth-relative spacecraft velocity. A pure translation between parallel inertial axes does not change the impulse vector.

**9. Why does altitude vary after a circular insertion?**
“Circular” is the instantaneous lunar two-body osculating orbit. Continued Earth gravity perturbs it in the three-body model. Our 24 h altitude range is about 109.934-110.011 km.

**10. Why is the modeled LOI different from the historical capture burn?**
The historical mission first entered an ellipse and later changed it. Our design enters a 110 km circle directly. The arrival state, orbit targets, and finite versus impulsive burn treatment differ. The scalar sum of historical maneuver magnitudes is a budget comparison, not a single burn vector.

**11. Are the propellant values actual Apollo 11 values?**
No. They use explicitly assumed effective masses and specific impulses. Those inputs affect fuel bookkeeping but do not change the unpowered gravitational coast. We do not claim to reconstruct historical stage mass or engine performance.

**12. Why 72 hours and 110 km? Is the solution optimal?**
We chose them as design targets, with 110 km matching Scenario A. A two-variable shooting solve finds a departure that meets them. We did not optimize total fuel or reproduce historical launch-epoch states.

## Code and notebook map

- Task 1: equation (1), exhaust momentum, and the indirect term.
- Task 2: the 185 km parking orbit, initial mass, TLI magnitude, and lunar phase.
- Task 3: positions AND velocities in the Moon-centered and rotating frames.
- Task 4: own RK4 and DOP853 reference.
- Task 5: one impulsive TLI followed by an unpowered coast.
- Task 6: ECI, rotating, distance, speed, and coast-mass figures.
- Task 7: V1, V2, V3.
- Task 8: independent +/-1 m/s and +/-0.5 degree perturbations.
- Task 9 / A: LOI and propagated lunar capture.

The PDF uses larger chart labels for projection. Data and verification values come from the same default notebook outputs. The V1 figure uses the same own RK4, parking state, and ten-revolution test as the notebook.

## Variable and acronym guide

| Symbol / acronym | Meaning |
|---|---|
| ECI | Earth-centered inertial-style, Earth-relative coordinates |
| MCI | Moon-centered coordinates with axes parallel to ECI |
| TLI | Trans-lunar injection, the departure impulse |
| LOI | Lunar orbit insertion, the capture impulse |
| r, v | Earth-relative spacecraft position and velocity |
| rM, vM | Earth-relative lunar position and velocity |
| rho, vrel | Moon-relative spacecraft position and velocity |
| muE, muM | Earth and Moon gravitational parameters |
| mu | Dimensionless Moon-to-total gravitational mass ratio |
| a, n | Lunar circular-orbit radius and mean motion |
| theta0, alpha | Initial lunar phase and instantaneous rotation angle nt+theta0 |
| R, q, qdot | Rotation matrix, barycentric rotating position, and its derivative |
| y, f, t, h, k1-k4 | State vector, derivative function, time, step size, and RK4 stage slopes |
| m, m0 | Spacecraft mass and assumed pre-TLI mass |
| Fg, T, u-hat | Gravitational force, thrust magnitude, and thrust direction |
| mdot_p, Ve, Isp, g0 | Positive outgoing propellant flow, exhaust speed, specific impulse, and standard gravity |
| vc, rp, t-hat | Local circular lunar speed, arrival radius from Moon center, and tangent direction |
| delta-v | Magnitude of a velocity impulse, except when explicitly written as a vector |

## Sources

1. Supplied MEC 568 Spacecraft Trajectory Calculation handout, Sections 4-7.
2. Verified default run of `MEC568_Tasks1to8_ScenarioA.ipynb` and its exported `summary.json`.
3. NASA, *Apollo 11 Mission Report*, November 1969, Table 7-V: https://www.nasa.gov/wp-content/uploads/static/apollo50th/pdf/A11_MissionReport.pdf

## Before submitting

- Fill the six name/contribution fields on the final PDF slide with actual work.
- Retain the final-slide AI disclosure.
- Rehearse every handoff and stay inside ten minutes.
- Make sure all members can explain the equations, algorithms, and assumptions.
- Submit the requested slide PDF and source-code ZIP. A notebook is useful supporting material, but keep the required runnable code ZIP as well.
