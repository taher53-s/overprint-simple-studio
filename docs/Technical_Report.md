# OVERPRINT

A design-led ink palette planner.

TECHNICAL REPORT  /  CIA 3  /  ATLAS uGDX  /  SEMESTER V, B.TECH CS AI & ML

TEAM MEMBER | APP ID
--- | ---
Taher Sohagpurwala | 2409540
Harsh Agrawal | Pending confirmation

## 1. Problem and objective

The application helps a designer trade screen-colour fidelity against the setup cost of a limited ink palette. Given target colour swatches, available stock inks and a maximum permitted colour distance, it chooses a weighted greedy cover. It then identifies the largest colour changes for human review. The central design question is whether fewer ink setups can preserve the intended visual character.

The optimisation objective is the sum of selected ink setup weights. It is not an exact minimum-ink-count solver. A separate press limit tells the user when the proposed greedy plan exceeds the available number of ink stations. Since the coverage structure depends on colour tolerance, changing that tolerance can change both feasibility and cost.

## Input, output and assumptions

INPUT | CONSTRAINT / INTERPRETATION
--- | ---
Target palette | 1-256 six-digit sRGB colours; repeated values merge in source order. Each unique colour has equal importance; the cream background represents unprinted paper.
Stock inks | 1-64 distinct colours; finite setup cost in (0,1000]. Costs are synthetic relative units.
Parameters | API tolerance 0-100 Delta E76; studio range 0-60. Press limit 1-64. Review count 1-256, clamped to palette size.
Output | Selected inks, nearest assignments, uncovered indices, setup weight, baseline, error review set, p90 and greedy trace.

## Default case

The supplied poster has eight unique target colours. The executed Java plan selects four inks, covers all eight targets, and has setup weight 6.6; the per-colour baseline also costs 6.6. This example demonstrates a usable reduction, not a measured saving over that baseline. The p90 colour shift is 16.86 Delta E76.

All sample palettes and the specimen artwork are synthetic project studies. No production printer or external dataset is represented. Preparation date: 17 November 2026.

# System & workflow

Java makes the decisions.

## 2. Architecture

LAYER | RESPONSIBILITY
--- | ---
Browser studio | Palette controls, input import, adjustable stock costs, original/proof toggle, warnings, SVG/JSON export and algorithm evidence.
HTTP server | JDK HttpServer, static assets, bounded URL-encoded requests, structured JSON errors and eight request threads.
Planner service | Input validation, duplicate normalisation, colour conversion, coverage construction, ink assignment and review-set assembly.
Algorithm classes | WeightedSetCover and RandomizedSelect contain self-implemented assessed algorithms. Java collections and PRNG are supporting infrastructure.
Evidence tools | Java correctness tests and benchmarks; independent Python HTTP integration suite. No database or external service.

```text
Browser palette / stock inks / parameters
              | POST /api/plan
              v
Java validation -> sRGB/XYZ/Lab -> coverage matrix
              |
Weighted set cover -> nearest selected-ink errors
              |
Randomized Quickselect -> top-k cutoff + p90
              | JSON
SVG proof / ink ticket / trace / export
```

## API contract

GET /api/health identifies the Java backend. POST /api/plan accepts URL-encoded targets, inks, tolerance, maxInks, review and seed. Targets are comma-separated hex values; inks are comma-separated hex:cost pairs. GET /api/benchmarks serves the recorded experiment. The request body is bounded at 64 KiB. Errors use an error string and 400, 404, 405, 413, 415 or 500 status as appropriate.

## Colour model

sRGB channels are linearised, transformed to XYZ using the standard D65 matrix, and normalised against the D65 reference white. CIELAB coordinates follow the piecewise cube-root transform. Euclidean distance in this common Lab space is Delta E 1976. Coverage[j][i] is true exactly when the distance between stock ink j and target i is no greater than the tolerance.

Both compared Lab values retain D65. The model is internally consistent but does not use CSS Lab's D50 adaptation or a printer ICC transform. It is not ink-mixing, optical-overprint or paper-absorption simulation.

# The ink-cover method

Cost per new colour.

## 3. Weighted greedy set cover - Unit 5

Let U contain n target colours. There are m available inks; ink j has positive cost c[j] and covers subset S[j]. Choose a family whose union covers U with low total cost. Weighted set cover is NP-hard, so this implementation uses the standard weighted greedy approximation. If the union of all available subsets is smaller than U, the uncovered colours are returned explicitly.

```text
covered = empty; selected = []
while some target is uncovered:
    for every unused ink j:
        gain[j] = |S[j] minus covered|
    choose j with minimum c[j] / gain[j], gain[j] > 0
    if no such j exists: stop
    selected.append(j)
    covered = covered union S[j]
return selected, U minus covered
```

## Correctness and termination

Invariant: covered is exactly the union of the selected ink subsets. Initially both are empty. Each update adds precisely S[j], preserving the invariant. Every successful iteration covers at least one new colour and marks an unused ink, so there are at most min(n,m) iterations. If no positive-gain ink remains, no unselected ink covers any remaining colour. Therefore a feasible union is fully covered, while an infeasible union is reported without fabricated assignments.

## Quality bound and a deliberate counterexample

For feasible instances with positive costs, charge each newly covered element the chosen cost/gain. The standard charging argument bounds total greedy cost by H_n times the optimal weighted cover, where H_n = 1 + 1/2 + ... + 1/n. This bound does not apply to satisfying a separate hard ink-count budget. The app checks that budget after selection.

For three colours, A covers the first two at cost 1.9, B covers only the third at cost 2, and C covers all three at cost 3. Greedy first takes A (0.95 per new colour), then B, costing 3.9. The optimum C costs 3. This case is a passing test precisely because the program does not claim exact optimality.

## Time and space

The colour-distance and coverage matrices cost O(nm) time and space to build. Each of r selected inks requires scanning m candidates and n colours: O(rmn), with r <= min(n,m). The solver adds O(n+m) working space beyond its input matrix. The baseline chooses the cheapest eligible ink independently for each colour and deduplicates the resulting set in O(nm) time.

The implementation uses boolean arrays, not bitsets. Candidate-order tie breaking is deterministic. It minimises weighted cost heuristically; it does not optimise perceptual error among all equally priced covers.

# The review method

Find the boundary, keep the order.

## 4. Randomized Quickselect - Unit 6 / CO5

After selection, each target is mapped to its nearest selected ink. The resulting error array has one distance per unique target. The review count k defines a practical attention budget: the designer will inspect k colours. Quickselect finds ascending zero-based rank n-k, the boundary of the k largest errors. A second call finds nearest-rank p90 at ceil(0.9n)-1.

```text
a = copy(errors); low = 0; high = n - 1
while low < high:
    pivot = a[random index in low..high]
    partition a[low..high] into <, = and > pivot
    if rank is in the equal interval: return pivot
    if rank is left of the equal interval: shrink high
    else: advance low
return a[low]
```

## Partition invariant and correctness

During three-way partitioning, the completed left region contains values below the pivot, the middle region contains equal values, and the completed right region contains greater values. Each iteration classifies an unknown element, so the unknown interval shrinks. When partitioning ends, any requested rank in the equal region has the pivot value. Otherwise removing the opposite region cannot change the requested order statistic. Repeating eventually yields the correct value.

All errors above the cutoff enter the review set. Boundary ties are added in original palette order until exactly k colours are selected. The result is a review set, not a fully sorted ranking. The public selection method clones the error array so original colour-index relationships remain intact.

## Randomisation, complexity and reproducibility

The pivot index comes from Java Random using a supplied seed; the UI fixes it to 2409540. Random-pivot selection has expected O(n) time, while unlucky sequences can require O(n squared). Three-way partitioning handles equal values in one partition. The iterative implementation uses O(1) partition state, but the input-preserving copy makes total extra space O(n). The follow-up review scan is O(n).

A fixed seed supports repeatable demonstrations and test traces; it does not imply a deterministic worst-case linear-time guarantee. The operation counter records element classifications, not the exact number of primitive less-than/greater-than comparisons.

## Missing and partial plans

If no ink can be selected, assignments and error quantiles are null and the review set is empty. For a partial plan, errors are measured against the nearest selected ink, including out-of-tolerance targets; uncovered indices remain explicit. The visual proof retains unmatched original colours and disables valid-proof export until full coverage and press-limit compliance are achieved.

# Correctness evidence

Check the claim independently.

## 5. Verification strategy

The Java suite contains 22 named checks, including 1,200 generated oracle cases. Exhaustive subset enumeration is independent of the greedy algorithm; full sorting is independent of Quickselect. Five colour/planner checks and boundary checks supplement the two core-method suites. Detailed names and results are in results/tests.txt.

CORE METHOD | DOCUMENTED CHECKS AND EXPECTED BEHAVIOUR
--- | ---
Set cover SC01-SC03 | Empty universe costs zero; shared ink can beat separate inks; weighted cost/gain can beat choosing the largest raw coverage.
Set cover SC04-SC06 | Unreachable colours remain uncovered; equal ratios use candidate order; empty stock leaves all targets uncovered.
Set cover SC07-SC08 | Invalid cost/dimensions rejected; explicit 3.9 versus 3.0 counterexample confirms non-optimal greedy behaviour.
Set cover SC09 | 200 seeded small feasible instances checked for actual coverage, cost >= exact optimum and cost <= H_n times optimum.
Quickselect QS01-QS03 | Singleton; minimum/maximum rank; duplicate values preserve rank semantics.
Quickselect QS04-QS06 | All-equal input terminates in one partition; sorted/reversed arrays; input preserved and seeded traces repeat.
Quickselect QS07-QS08 | Empty/bad-rank/non-finite input rejected; 1,000 random arrays match an independent full-sort order statistic.

## Integration and numerical checks

Known D65 black, white and red coordinates check colour conversion; identity distance must be zero. Planner tests check duplicate consolidation, exact top-k tie handling, null statistics with no eligible ink and separate press-limit warnings. Six invalid input classes are exercised through the HTTP API.

The separate HTTP suite passes 19 checks: Java health, HTML/CSS/JS delivery, the default four-ink plan, exact assignments, review cardinality, zero tolerance, duplicate targets, infeasible neon, budget warnings, invalid payloads, request size, content type, method handling, repeated keys, missing/path-traversal requests and benchmark delivery.

## Observed default output

The executed default trace chooses Carbon, Marigold, Vermilion and Cobalt in that order. Each covers two new colours. Their cost/new-colour scores are 0.55, 0.75, 0.95 and 1.05. The complete machine-readable output is in results/demo-plan.json.

Verification limit: managed browser and preview relay did not initialise. Browser layout, keyboard traversal, imports and download interactions remain pending local checks. JavaScript syntax and the generated SVG are verified separately; no browser screenshots or passed UI tests are claimed.

# Measured performance

Three sizes. Two comparisons.

## 6. Methodology

The Java benchmark uses nested synthetic colour records of 100, 1,000 and 10,000 elements, 32 fixed stock inks and tolerance 18. A seeded generator (2409540) perturbs RGB samples around stock colours. Some perturbations can remain outside tolerance; coverage is reported. Each method has 15 warmups and 21 measured repetitions; the median is recorded. Environment: Java 21.0.13, Linux amd64, 2 reported processors.

The timed kernels exclude colour conversion, coverage construction, network transport and SVG rendering. Quickselect and full sorting both include input cloning. A volatile sink consumes results. These shared-machine microbenchmarks are indicative, not JMH or production latency measurements. Large arrays call algorithm classes directly; the UI has a separate 256-colour validation limit.

n | GREEDY ms | BASELINE ms | SELECT ms | SORT ms
--- | --- | --- | --- | ---
100 | 0.239 | 0.076 | 0.011 | 0.025
1000 | 1.292 | 0.147 | 0.044 | 0.057
10000 | 8.013 | 0.405 | 0.273 | 1.056

n | COVERED | GREEDY COST | BASELINE COST | INKS
--- | --- | --- | --- | ---
100 | 100/100 | 65.5 | 65.5 | 24
1000 | 1000/1000 | 78.5 | 81.0 | 27
10000 | 9981/10000 | 83.0 | 85.5 | 28

## Interpretation

Quickselect is faster than full sorting at each recorded size. At 10,000 elements the measured full-sort time is 3.87 times the selection time. This is consistent with the expected linear versus n log n distinction, but three timings do not prove an asymptotic bound. Small-input results are sensitive to JVM warmup and measurement overhead.

Greedy spends more time than the per-colour baseline in every recorded row. Its purpose is a coordinated cost choice, not a faster scan. Setup weight ties the baseline at n=100, and is lower by 2.5 units at n=1,000 and n=10,000. Neither result establishes universal superiority. At the largest size, 19 targets remain outside all available ink coverage; cost comparisons apply to the shared reachable universe.

## Reproduce

```text
./run.sh test
./run.sh benchmark
python3 scripts/test_api.py
```

Raw outputs: results/benchmarks.json and results/benchmarks.csv. Source: src/test/java/studio/Benchmark.java. Re-running overwrites recorded results; regenerate this document afterwards with scripts/build_documents.py so tables stay consistent.

# Scope & handoff

What the result can honestly say.

## 7. Limitations and next steps

The model compares individual stock-ink colours to unique target swatches. It ignores image area, ink mixing, overprint transparency, paper, lighting, dot gain and ICC profiles. Delta E76 is not uniformly perceptual across all colours. Setup weights are synthetic. Greedy minimises cost approximately, then checks the press limit; it can exceed that limit even if another valid smaller cover exists. The fixed specimen demonstrates palette changes rather than arbitrary image processing.

A useful next iteration would accept a student-authored SVG with controlled fill extraction, compare Delta E2000 against the current metric, add a small-instance exact solver for quality studies, and collect calibrated stock-ink measurements. A hard cardinality-constrained solver would be a distinct optimisation feature and needs its own correctness and complexity analysis.

## Contribution record

MEMBER | PROPOSED AREA; ACTUAL WORK TO CONFIRM
--- | ---
Taher Sohagpurwala / 2409540 | Visual direction, artwork studies, interaction design and colour-model review.
Harsh Agrawal / ID pending | Algorithm review, tests, benchmark reproduction and API walkthrough.

Initial code, synthetic assets and document drafts were prepared with development assistance. The tests were executed in the managed environment. Proposed roles above are not verified contribution claims. Each student must record actual changes and be able to explain both core methods; see docs/CONTRIBUTIONS.md.

## Reproducibility and submission status

JDK 17 or newer is sufficient. Run ./run.sh on macOS/Linux, or run.cmd on Windows, and open http://127.0.0.1:3000. No runtime dependencies, external accounts, secrets or database are needed. The source package includes samples, tests, raw benchmark results, a demo guide and editable documents. Confirm Harsh's ID, local browser checks, faculty scope approval and individual contributions before submission.

## References

1. Cormen, Leiserson, Rivest and Stein. Introduction to Algorithms, 4th ed., MIT Press, 2022. Randomized selection and approximation algorithms.
2. Chvatal, V. A Greedy Heuristic for the Set-Covering Problem. Mathematics of Operations Research 4(3), 233-235, 1979. DOI: 10.1287/moor.4.3.233.
3. CIE. Colorimetry, 3rd ed., CIE 15:2004.
4. W3C. CSS Color Module Level 4, sample sRGB/XYZ conversion methods. https://www.w3.org/TR/css-color-4/ . Both app Lab values retain D65.
5. Supplied ATLAS uGDX CIA 3 Advanced Algorithm Project Guidelines, 2026-27. Assessment brief.

IDEATION RECORD: 15 initial ideas were rejected in full, followed by a new set of 15. OVERPRINT was selected from the second set for visual authorship, meaningful algorithm integration and a reproducible scope. The complete process is in docs/IDEA_PROCESS.md.
