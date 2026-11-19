# Algorithm extension evidence

The current release adds deterministic Median of Medians and an array-backed binary max-heap to the original weighted set cover and randomized Quickselect pipeline.

## Correctness

Median of Medians selects a pivot recursively from medians of groups of at most five. All entries are partitioned into less, equal or greater. If the desired rank is within the equal interval, the pivot is the answer. Otherwise only the containing partition remains, with an adjusted rank on the greater side. Group sorting operates on a copy. The standard groups-of-five recurrence T(n) <= T(ceil(n/5)) + T(7n/10 + O(1)) + O(n) yields worst-case linear time.

A max-heap maintains the invariant that each parent has priority at least as high as either child. Bottom-up sift-down establishes the invariant. Each extraction removes the maximum, moves the last entry to the root and restores the invariant. Priority is descending error, then ascending original palette index for ties. Repeated extraction therefore produces the required stable worst-first order.

## Documented fixed cases for both methods

| Input | Selection check | Heap check |
|---|---|---|
| [7] | Only rank is 7 | Only entry remains |
| [3,1,2] | Every rank matches [1,2,3] | Indices [0,2,1] |
| [5,5,5,5] | Every rank is 5 | Stable indices [0,1,2,3] |
| [9,8,7,6,5,4,3,2,1] | Every rank matches ascending order | Original indices already descending |
| [-4,8,-2,0,8,3] | All ranks match a full-sort oracle | Tied 8s ordered by original index |

Additional checks: empty heap, rejected empty selection, 500 seeded generated selection cases, both planner modes, 250 Java/hosted full-output comparisons. The hosted unit suite independently adds 300 deterministic-selection and 100 heap-ordering oracles.

## Benchmarks

`results/extension-benchmarks.csv` records actual Java kernel timings at n=100, 1,000 and 10,000. Each number is the median of 15 repetitions after 8 warmups. The heap benchmark ranks all n entries; actual UI review count k is usually smaller. Timings include input copying/allocation. Shared-machine microbenchmarks do not prove asymptotic bounds or guarantee speed on another machine.

Reproduce after compilation:

```sh
java -cp build/classes studio.ExtendedTests
java -cp build/classes studio.ExtensionBenchmark
```

The original technical report documents the base release; this extension note and the current README document the additional methods. The independent presenter guide is not served by the presentation website.
