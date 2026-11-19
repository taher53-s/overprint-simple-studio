package studio;

import java.nio.file.*;
import java.util.*;

/** Small reproducible microbenchmark, not a replacement for JMH. */
public final class Benchmark {
    private static volatile double sink;
    private static double medianMillis(Runnable task) {
        for(int i=0;i<15;i++) task.run();
        double[] samples=new double[21];
        for(int i=0;i<samples.length;i++) { long t=System.nanoTime(); task.run(); samples[i]=(System.nanoTime()-t)/1e6; }
        Arrays.sort(samples); return samples[samples.length/2];
    }
    public static void main(String[] args) throws Exception {
        List<Map<String,Object>> rows=new ArrayList<>();
        for(int n:new int[]{100,1000,10000}) {
            Random rng=new Random(2409540); int m=32;
            double[][] bank=new double[m][]; double[] costs=new double[m]; int[][] rgb=new int[m][3];
            for(int j=0;j<m;j++) {
                for(int k=0;k<3;k++) rgb[j][k]=30+rng.nextInt(196);
                bank[j]=ColorMath.lab(String.format("#%02X%02X%02X",rgb[j][0],rgb[j][1],rgb[j][2]));
                costs[j]=1+rng.nextInt(9)/2.0;
            }
            boolean[][] c=new boolean[m][n]; double[] errors=new double[n];
            for(int i=0;i<n;i++) {
                int j=i%m; int[] v=new int[3];
                for(int k=0;k<3;k++) v[k]=Math.max(0,Math.min(255,rgb[j][k]+rng.nextInt(31)-15));
                double[] lab=ColorMath.lab(String.format("#%02X%02X%02X",v[0],v[1],v[2]));
                errors[i]=ColorMath.distance(lab,bank[j]);
                for(int k=0;k<m;k++) c[k][i]=ColorMath.distance(lab,bank[k])<=18;
            }
            int rank=(int)Math.ceil(.9*n)-1;
            var greedy=WeightedSetCover.solve(n,c,costs); var base=WeightedSetCover.perColorBaseline(n,c,costs);
            Map<String,Object> row=new LinkedHashMap<>();
            row.put("n",n); row.put("m",m);
            row.put("greedyMs",medianMillis(() -> sink=WeightedSetCover.solve(n,c,costs).cost()));
            row.put("baselineMs",medianMillis(() -> sink=WeightedSetCover.perColorBaseline(n,c,costs).cost()));
            row.put("quickselectMs",medianMillis(() -> sink=RandomizedSelect.select(errors,rank,2409540).value()));
            row.put("sortMs",medianMillis(() -> {double[] a=errors.clone(); Arrays.sort(a); sink=a[rank];}));
            row.put("greedyCost",greedy.cost()); row.put("baselineCost",base.cost());
            row.put("greedyInks",greedy.selected().size()); row.put("covered",n-greedy.uncovered().size());
            rows.add(row); System.out.println(Json.encode(row));
        }
        Map<String,Object> result=new LinkedHashMap<>();
        result.put("seed",2409540); result.put("warmups",15); result.put("repetitions",21);
        result.put("java",System.getProperty("java.version")); result.put("os",System.getProperty("os.name")+" "+System.getProperty("os.arch"));
        result.put("processors",Runtime.getRuntime().availableProcessors()); result.put("rows",rows);
        result.put("method","Median of 21 runs after 15 warmups per method; coverage construction, HTTP and rendering excluded. Quickselect and sort both include input cloning. Generated clustered sRGB colors; 32 candidate inks, tolerance 18. Costs are relative setup units. Shared VM timings are indicative.");
        if (!Double.isFinite(sink)) throw new AssertionError("Non-finite benchmark result");
        Files.createDirectories(Path.of("results"));
        Files.writeString(Path.of("results/benchmarks.json"),Json.encode(result));
        StringBuilder csv=new StringBuilder("colors,candidates,greedy_ms,baseline_ms,quickselect_ms,sort_ms,greedy_cost,baseline_cost,covered\n");
        for(var r:rows) csv.append(String.join(",",List.of(r.get("n").toString(),r.get("m").toString(),r.get("greedyMs").toString(),r.get("baselineMs").toString(),r.get("quickselectMs").toString(),r.get("sortMs").toString(),r.get("greedyCost").toString(),r.get("baselineCost").toString(),r.get("covered").toString()))).append('\n');
        Files.writeString(Path.of("results/benchmarks.csv"),csv);
    }
}
