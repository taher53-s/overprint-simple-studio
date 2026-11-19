package studio;

import java.util.*;

/** Weighted greedy set cover. Costs are positive; ties follow candidate order. */
public final class WeightedSetCover {
    public record Step(int ink, int newlyCovered, double costPerNewColor) {}
    public record Result(List<Integer> selected, List<Integer> uncovered,
                         List<Step> steps, double cost) {}

    public static Result solve(int n, boolean[][] coverage, double[] costs) {
        if (n < 0 || coverage == null || costs == null || coverage.length != costs.length)
            throw new IllegalArgumentException("Invalid set-cover dimensions.");
        for (int j = 0; j < costs.length; j++) {
            if (!Double.isFinite(costs[j]) || costs[j] <= 0 || coverage[j].length != n)
                throw new IllegalArgumentException("Each ink needs positive cost and one entry per color.");
        }
        boolean[] covered = new boolean[n];
        boolean[] used = new boolean[costs.length];
        List<Integer> selected = new ArrayList<>();
        List<Step> steps = new ArrayList<>();
        int remaining = n;
        double cost = 0;
        while (remaining > 0) {
            int best = -1, bestGain = 0;
            double bestRatio = Double.POSITIVE_INFINITY;
            for (int j = 0; j < costs.length; j++) {
                if (used[j]) continue;
                int gain = 0;
                for (int i = 0; i < n; i++) if (!covered[i] && coverage[j][i]) gain++;
                if (gain > 0 && costs[j] / gain < bestRatio) {
                    best = j; bestGain = gain; bestRatio = costs[j] / gain;
                }
            }
            if (best == -1) break; // Some colors cannot be covered by the available inks.
            used[best] = true;
            selected.add(best);
            steps.add(new Step(best, bestGain, bestRatio));
            cost += costs[best];
            for (int i = 0; i < n; i++) if (!covered[i] && coverage[best][i]) {
                covered[i] = true; remaining--;
            }
        }
        List<Integer> uncovered = new ArrayList<>();
        for (int i = 0; i < n; i++) if (!covered[i]) uncovered.add(i);
        return new Result(List.copyOf(selected), List.copyOf(uncovered), List.copyOf(steps), cost);
    }

    /** Baseline: buy the cheapest eligible ink for each color, then deduplicate. */
    public static Result perColorBaseline(int n, boolean[][] coverage, double[] costs) {
        Set<Integer> selected = new LinkedHashSet<>();
        List<Integer> uncovered = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            int best = -1;
            for (int j = 0; j < costs.length; j++)
                if (coverage[j][i] && (best == -1 || costs[j] < costs[best])) best = j;
            if (best == -1) uncovered.add(i); else selected.add(best);
        }
        double cost = 0;
        for (int j : selected) cost += costs[j];
        return new Result(List.copyOf(selected), uncovered, List.of(), cost);
    }
}
