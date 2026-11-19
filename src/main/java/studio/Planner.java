package studio;

import java.util.*;

public final class Planner {
    public record Ink(String hex, double cost) {}
    public static Map<String,Object> plan(Map<String,String> form) {
        long started = System.nanoTime();
        String method = form.getOrDefault("method", "randomized");
        if (!method.equals("randomized") && !method.equals("deterministic")) throw new IllegalArgumentException("Unknown selection method.");
        String raw = form.getOrDefault("targets", "").trim();
        if (raw.isEmpty()) throw new IllegalArgumentException("Add at least one artwork color.");
        String[] input = raw.split(",", -1);
        if (input.length > 256) throw new IllegalArgumentException("Use at most 256 artwork colors.");
        Set<String> unique = new LinkedHashSet<>();
        for (String s : input) unique.add(ColorMath.hex(s));
        List<String> targets = new ArrayList<>(unique);
        List<Ink> inks = new ArrayList<>();
        Set<String> inkColors = new HashSet<>();
        String inkInput = form.getOrDefault("inks", "").trim();
        if (inkInput.isEmpty()) throw new IllegalArgumentException("Enable at least one available ink.");
        for (String s : inkInput.split(",", -1)) {
            String[] p = s.split(":", -1);
            if (p.length != 2) throw new IllegalArgumentException("Each ink needs hex:cost.");
            String h = ColorMath.hex(p[0]);
            double cost = Double.parseDouble(p[1]);
            if (!Double.isFinite(cost) || cost <= 0 || cost > 1000)
                throw new IllegalArgumentException("Ink costs must be between 0 and 1000, excluding zero.");
            if (!inkColors.add(h)) throw new IllegalArgumentException("Remove duplicate inks from the ink bank.");
            inks.add(new Ink(h, cost));
        }
        if (inks.size() > 64) throw new IllegalArgumentException("Use at most 64 available inks.");
        double tolerance = Double.parseDouble(form.getOrDefault("tolerance", "18"));
        if (!Double.isFinite(tolerance) || tolerance < 0 || tolerance > 100)
            throw new IllegalArgumentException("Color tolerance must be between 0 and 100.");
        int requestedReview = Integer.parseInt(form.getOrDefault("review", "3"));
        int maxInks = Integer.parseInt(form.getOrDefault("maxInks", "4"));
        long seed = Long.parseLong(form.getOrDefault("seed", "2409540"));
        if (requestedReview < 1 || requestedReview > 256 || maxInks < 1 || maxInks > 64)
            throw new IllegalArgumentException("Review count must be 1–256 and press limit 1–64.");
        int n = targets.size(), m = inks.size();
        double[][] labs = new double[n][];
        for (int i = 0; i < n; i++) labs[i] = ColorMath.lab(targets.get(i));
        double[][] distances = new double[m][n];
        boolean[][] coverage = new boolean[m][n];
        double[] costs = new double[m];
        for (int j = 0; j < m; j++) {
            costs[j] = inks.get(j).cost();
            double[] lab = ColorMath.lab(inks.get(j).hex());
            for (int i = 0; i < n; i++) {
                distances[j][i] = ColorMath.distance(labs[i], lab);
                coverage[j][i] = distances[j][i] <= tolerance;
            }
        }
        var cover = WeightedSetCover.solve(n, coverage, costs);
        var baseline = WeightedSetCover.perColorBaseline(n, coverage, costs);
        List<Map<String,Object>> selected = new ArrayList<>();
        for (int j : cover.selected()) selected.add(Map.of("index", j, "hex", inks.get(j).hex(), "cost", costs[j]));
        List<Map<String,Object>> mappings = new ArrayList<>();
        double[] errors = new double[n];
        boolean hasPlan = !cover.selected().isEmpty();
        for (int i = 0; i < n; i++) {
            int best = -1;
            for (int j : cover.selected()) if (best < 0 || distances[j][i] < distances[best][i]) best = j;
            Map<String,Object> map = new LinkedHashMap<>();
            map.put("index", i); map.put("source", targets.get(i));
            map.put("ink", best < 0 ? null : inks.get(best).hex());
            map.put("deltaE", best < 0 ? null : distances[best][i]);
            map.put("covered", best >= 0 && coverage[best][i]);
            errors[i] = best < 0 ? 0 : distances[best][i];
            mappings.add(map);
        }
        int k = Math.min(requestedReview, n);
        List<Integer> review = new ArrayList<>();
        Double threshold = null, p90 = null;
        int partitions = 0;
        long comparisons = 0;
        if (hasPlan) {
            var selection = method.equals("deterministic") ? new RandomizedSelect.Result(MedianOfMedians.select(errors,n-k),0,0) : RandomizedSelect.select(errors, n-k, seed);
            threshold = selection.value(); partitions = selection.partitions(); comparisons = selection.comparisons();
            // Strictly larger errors first; fill boundary ties in original palette order.
            for (int i = 0; i < n; i++) if (errors[i] > threshold) review.add(i);
            for (int i = 0; i < n && review.size() < k; i++) if (errors[i] == threshold) review.add(i);
            p90 = RandomizedSelect.select(errors, (int)Math.ceil(.9*n)-1, seed).value();
        }
        List<Map<String,Object>> trace = new ArrayList<>();
        for (var step : cover.steps()) trace.add(Map.of("hex", inks.get(step.ink()).hex(), "gain", step.newlyCovered(), "ratio", step.costPerNewColor()));
        Map<String,Object> out = new LinkedHashMap<>();
        out.put("targets", targets); out.put("inputCount", input.length); out.put("duplicatesRemoved", input.length-n);
        out.put("selected", selected); out.put("mappings", mappings); out.put("uncovered", cover.uncovered());
        out.put("cost", cover.cost()); out.put("baselineCost", baseline.cost()); out.put("baselineInks", baseline.selected().size());
        out.put("feasible", cover.uncovered().isEmpty()); out.put("withinPressLimit", selected.size() <= maxInks);
        out.put("maxInks", maxInks); out.put("tolerance", tolerance); out.put("review", review);
        out.put("rankedReview", ReviewHeap.rank(review, errors)); out.put("selectionMethod", method);
        out.put("reviewThreshold", threshold); out.put("p90", p90); out.put("partitions", partitions);
        out.put("comparisons", comparisons); out.put("seed", seed); out.put("trace", trace);
        out.put("elapsedMs", (System.nanoTime()-started)/1_000_000.0);
        return out;
    }
}
