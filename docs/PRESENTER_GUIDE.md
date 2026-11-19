# OVERPRINT — understand it, then present it

## Your opening (30 seconds)

“OVERPRINT helps a designer reduce an artwork palette to available print inks. Instead of selecting inks by eye alone, it compares colours, chooses an approximate low-cost ink cover, and shows which colour changes need a closer look. The sample starts with eight colours and reaches four inks.”

## Explain the flow in plain language

1. **Input:** Eight hex colours, available inks, costs, tolerance and a review count.
2. **Deduplicate:** A hash set keeps repeated colours from counting twice.
3. **Measure:** Convert colours to CIELAB; Delta E measures their difference.
4. **Represent:** A boolean matrix answers “can ink j represent colour i within tolerance?”
5. **Choose:** Weighted set cover buys the most useful coverage per unit cost at each step.
6. **Inspect:** Find the nearest selected ink for each colour and calculate its error.
7. **Select:** Quickselect or Median of Medians finds the boundary for the k largest errors.
8. **Prioritize:** A max-heap orders those k colours, worst first.
9. **Output:** Show the proof, chosen inks, coverage, error queue and exportable result.

## The important distinction

Set cover answers **which inks should we choose?** Selection answers **which colour changes should we review?** The heap answers **in what order should we review them?** These are different jobs.

## Your actual semester connection

The uploaded archive contains two PDFs and a maximum-flow DOCX, rather than standalone Java files. Module 1 Notes.pdf introduces Quickselect on pages 9–11 and Median of Medians on pages 11–13. The implementation follows those concepts, with a seeded random pivot for Quickselect and three-way partition handling for equal values.

The maximum-flow document is not used in this product: its capacity-allocation objective is different. Do not tell sir that maximum flow, tries, KMP or Bloom filters are implemented here.

## Set cover example to say aloud

“Suppose an ink costs 2 units and covers four colours we have not yet covered. Its score is 0.5. Another costs 1.5 and covers two new colours, so its score is 0.75. We choose the first one. After every pick we recalculate new coverage, because a colour already covered should not count again.”

In the real default trace, the scores are 0.55, 0.75, 0.95 and 1.05. Four inks cover eight colours. Greedy is not exact: a cheap local decision can force an expensive later decision. Do not claim minimum possible inks or guaranteed cheapest cost.

## Quickselect example to say aloud

“For errors [2, 9, 4, 7, 1, 6], I want the two largest changes. I need the element at ascending rank 4, which is 7. Quickselect chooses a pivot, partitions into smaller, equal and larger errors, and continues only on the side containing that rank. It does not fully sort the array.”

Expected O(n); worst O(n²). Our method copies the input, so extra space is O(n). The fixed seed makes the demonstration repeatable, not worst-case linear.

## Median of Medians example to say aloud

“The second option changes how the pivot is chosen. Divide the array into groups of five, sort those tiny groups with insertion sort, take each median, then select the median of those medians. That gives a pivot with a provable balance bound. Partition around it and continue on the needed side.”

Worst-case O(n), using O(n) extra space in our allocation-based implementation. It is useful when a worst-case guarantee matters, but can have a larger constant cost on small arrays. Both modes must return the same cutoff. p90 still uses randomized Quickselect, so the randomized component remains meaningful in both modes.

## Max-heap example to say aloud

“Selection produces the review set. I place its entries in an array-backed binary max-heap. The root holds the largest error. Remove it, move the last element to the root and sift down. Repeating gives a worst-first review queue.”

For zero-based position i, children are 2i+1 and 2i+2. Heap construction is O(k); extracting all k entries costs O(k log k). Ties use the original colour index. We rank only the chosen k errors.

## Five-minute live demonstration

- **0:00–0:30:** Explain the design problem and run the default study.
- **0:30–1:15:** Toggle Original / Ink proof and point out 8 colours → 4 inks.
- **1:15–2:15:** Open Algorithms; explain a real cost/new-coverage row.
- **2:15–3:00:** Switch review algorithm, rerun and show that the cutoff remains the same. Explain the different pivot rules.
- **3:00–3:45:** Point to the numbered review queue and explain the heap.
- **3:45–4:30:** Use the impossible-neon preset or set press limit to one. Show honest failure handling.
- **4:30–5:00:** Restore the default, export, and end with the product film.

Use “Take a tour” if you want the screen to highlight each component while explaining it. The popup contains product and algorithm explanations, not private prompts.

## Code walkthrough

- `Planner.java`: validation, matrices, assignments and orchestration.
- `WeightedSetCover.solve`: compute gains, choose best ratio, update coverage.
- `RandomizedSelect.select`: random pivot and three-way partition.
- `MedianOfMedians.select` / `pick`: groups of five and recursive pivot.
- `ReviewHeap.rank` / `down`: heap construction and priority extraction.

## Questions sir might ask

**Why not just sort?** Sorting works as a baseline, but finding one cutoff needs only selection. The heap ranks just the selected review set.

**Why a hash set?** Repeated targets should not inflate the coverage count. The chosen ordered set also preserves source order.

**Is the proof realistic printing?** It is a palette-remapped screen study. Physical print accuracy needs ink, paper and printer calibration.

**What if no ink matches?** Return uncovered colours and null error statistics for an empty plan. Do not invent a valid proof.

**What is really deployed?** The current hosted site uses a JavaScript adapter checked against Java outputs. The downloadable Java backend is the assessment implementation. The prepared Vercel container is intended to run that Java backend directly; deployment still requires successful authentication and verification.

**What did each student contribute?** Describe only the actual work each person reviewed, changed and understands. Use the contribution record separately.
