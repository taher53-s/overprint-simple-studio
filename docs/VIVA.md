# OVERPRINT — demonstration and viva notes

## Eight-minute demonstration

**0:00–0:45 — the problem.** A designer has eight screen colours and access to stock inks. Every ink introduces setup cost. We want a useful compromise, then human review of the largest changes.

**0:45–2:00 — workflow.** Run the poster preset. Show eight unique target colours mapping to four inks. Toggle the original and the ink proof; inspect the mapping strip and ink ticket. State that this is a fixed sample artwork with an editable palette.

**2:00–3:00 — constraints.** Tighten tolerance and rerun. Set the press limit to one: distinguish “all colours covered” from “within press limit”. Greedy may exceed the budget even when a different smaller cover exists.

**3:00–4:00 — weighted set cover.** Open Under the ink. Explain the next ink's cost divided by newly covered colours. The selected ink is a local greedy choice. The objective is total setup weight, not a claim of exact minimum count.

**4:00–5:00 — Quickselect.** Show the orange review bars and cutoff. A random pivot partitions errors into less-than, equal-to and greater-than groups. Only the partition containing the target rank is continued. The top-k set is not a complete ranking.

**5:00–6:00 — failures.** Load Impossible neon. No candidate is sufficiently close, so the system reports uncovered colours and disables proof export. Import the duplicate sample; show consolidation. Try the empty sample; show the error.

**6:00–7:00 — evidence.** Show three benchmark sizes. Discuss measured costs as well as timings. Full sorting is a baseline for finding one quantile; the per-colour ink baseline is simpler and faster, but may buy an unnecessarily expensive combination.

**7:00–8:00 — export and scope.** Restore the poster and export SVG and JSON. Explain why a physical ink/paper test is still required. State each student's actual confirmed contribution.

## Questions to be ready for

**What is the universe in set cover?** The unique target colour swatches. Each available ink defines the subset within the selected Delta E tolerance.

**Why weighted?** Ink setups can have different relative costs. The score is cost/newly-covered colours, not only the number of matches.

**Why does the algorithm terminate?** Each successful iteration covers at least one previously uncovered colour and selects a previously unused ink. If there is no positive gain, it stops and reports the remaining colours. At most min(n,m) inks can be selected.

**What can you prove?** Every reported covered colour is covered by at least one selected ink. If a full cover exists, greedy will eventually cover it. The weighted approximation is at most H_n times optimal for positive costs, with no hard cardinality constraint applied during selection. This does not prove exact optimality.

**Show a failure of optimality.** For three colours, ink A covers the first two at cost 1.9; B covers the last at cost 2; C covers all three at cost 3. Greedy chooses A because 0.95 < 1, then B: 3.9 total. The optimum is C: 3.

**Complexity?** The coverage matrix is O(nm) to construct. This simple greedy solver scans m candidates and n colours for each of r selected inks: O(rmn), with r ≤ min(n,m). The matrix uses O(nm) space; the solver itself adds O(n+m). Do not describe it as a bitset implementation.

**Where is randomization?** `RandomizedSelect.select` chooses a uniformly random pivot index in the current interval with a seeded Java PRNG. The seed makes demonstrations reproducible; it does not remove the probabilistic algorithm's expected/worst-case distinction.

**How does Quickselect remain correct with duplicates?** Three-way partitioning groups all values equal to the pivot. If the requested rank lies in that middle interval, the pivot is the answer. Otherwise only the relevant outer interval remains.

**Which rank gives the worst k errors?** Ascending zero-based rank n-k gives the boundary. Take all values strictly above it, then enough boundary ties in source order to reach exactly k. We scan for the review set; we do not sort it.

**What does p90 mean here?** The nearest-rank 90th percentile: ascending index ceil(0.9n)-1. On a small palette it can be the maximum. It is a descriptive error statistic, not a pass/fail print-quality standard.

**Does Quickselect use O(1) space?** The in-place iterative partition engine can, but this implementation clones its input to preserve mapping order. Its additional space is O(n).

**Why not use CIEDE2000 or an ICC profile?** D65 CIELAB with Delta E 1976 keeps the course model small and inspectable. It is less perceptually uniform than newer metrics and does not account for the physical press. Printer-specific calibration is future work.

**What if every colour is outside tolerance?** The ink set is empty, all targets are uncovered, assignments and quantiles are null, and proof export is disabled. The system does not invent a good plan.

**What is actually original here?** The course-project composition of palette planning, algorithm traces, controlled before/after proof and a review queue. We make no claim that ink reduction or set cover itself is new.

## Local browser checklist still to run

- Desktop and narrow-phone widths: no horizontal clipping or inaccessible controls.
- Keyboard focus through navigation, palette controls, details, planning and export.
- Import each JSON sample; verify original/proof toggles and stale-result warnings.
- Change inputs while a request is pending; an old response must not overwrite newer inputs.
- Verify SVG and JSON downloads, and reimport the exported JSON.
- Open the SVG in a browser/vector editor and confirm there are no external resources.

The managed browser failed to initialize during preparation. These checks are explicitly pending, not recorded as passed.
