package studio;

import java.util.Random;

/** Random-pivot, three-way Quickselect. Public calls preserve the input array. */
public final class RandomizedSelect {
    public record Result(double value, int partitions, long comparisons) {}
    public static Result select(double[] input, int rank, long seed) {
        if (input == null || rank < 0 || rank >= input.length)
            throw new IllegalArgumentException("Rank must address a nonempty array.");
        double[] a = input.clone();
        for (double v : a) if (!Double.isFinite(v))
            throw new IllegalArgumentException("Quickselect requires finite values.");
        Random random = new Random(seed);
        int low = 0, high = a.length - 1, partitions = 0;
        long comparisons = 0;
        while (low < high) {
            double pivot = a[low + random.nextInt(high - low + 1)];
            int lt = low, i = low, gt = high;
            partitions++;
            while (i <= gt) {
                comparisons++;
                if (a[i] < pivot) swap(a, lt++, i++);
                else if (a[i] > pivot) swap(a, i, gt--);
                else i++;
            }
            if (rank < lt) high = lt - 1;
            else if (rank > gt) low = gt + 1;
            else return new Result(pivot, partitions, comparisons);
        }
        return new Result(a[low], partitions, comparisons);
    }
    private static void swap(double[] a, int i, int j) {
        double t = a[i]; a[i] = a[j]; a[j] = t;
    }
}
