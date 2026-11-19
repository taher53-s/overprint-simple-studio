package studio;

import java.util.*;

/** Dependency-free tests with independent exhaustive/sorting oracles. */
public final class AlgorithmTests {
    private static int passed;
    private static final List<String> lines = new ArrayList<>();
    private static void check(boolean value, String message) {
        if (!value) throw new AssertionError(message);
    }
    private static void test(String name, Runnable body) {
        body.run(); passed++; lines.add("PASS " + name); System.out.println("PASS " + name);
    }
    private static void rejects(Runnable body) {
        try { body.run(); } catch (IllegalArgumentException expected) { return; }
        throw new AssertionError("Expected input rejection");
    }
    private static double exact(int n, boolean[][] sets, double[] costs) {
        double best = Double.POSITIVE_INFINITY;
        for (int mask = 0; mask < (1 << sets.length); mask++) {
            boolean[] covered = new boolean[n]; double cost = 0;
            for (int j = 0; j < sets.length; j++) if ((mask & (1<<j)) != 0) {
                cost += costs[j];
                for (int i = 0; i < n; i++) covered[i] |= sets[j][i];
            }
            boolean full = true; for (boolean v : covered) full &= v;
            if (full) best = Math.min(best,cost);
        }
        return best;
    }
    public static void main(String[] args) throws Exception {
        test("SC01 empty universe costs zero", () -> check(WeightedSetCover.solve(0,new boolean[0][0],new double[0]).cost()==0,"empty"));
        test("SC02 a shared ink is cheaper than two single inks", () -> {
            var r = WeightedSetCover.solve(2,new boolean[][]{{true,false},{false,true},{true,true}},new double[]{2,2,3});
            check(r.selected().equals(List.of(2)) && r.cost()==3,"shared");
        });
        test("SC03 weighted choice uses cost per newly covered color", () -> {
            var r = WeightedSetCover.solve(3,new boolean[][]{{true,true,true},{true,true,false},{false,false,true}},new double[]{10,1,1});
            check(r.selected().equals(List.of(1,2)) && r.cost()==2,"weighted");
        });
        test("SC04 infeasible colors are explicitly returned", () -> {
            var r = WeightedSetCover.solve(2,new boolean[][]{{true,false}},new double[]{1});
            check(r.uncovered().equals(List.of(1)),"infeasible");
        });
        test("SC05 equal ratios follow candidate order", () -> check(WeightedSetCover.solve(1,new boolean[][]{{true},{true}},new double[]{1,1}).selected().equals(List.of(0)),"ties"));
        test("SC06 empty candidate bank leaves all colors uncovered", () -> check(WeightedSetCover.solve(2,new boolean[0][2],new double[0]).uncovered().size()==2,"empty bank"));
        test("SC07 invalid costs and dimensions rejected", () -> {
            rejects(() -> WeightedSetCover.solve(1,new boolean[][]{{true}},new double[]{0}));
            rejects(() -> WeightedSetCover.solve(1,new boolean[][]{{true}},new double[]{Double.NaN}));
            rejects(() -> WeightedSetCover.solve(2,new boolean[][]{{true}},new double[]{1}));
        });
        test("SC08 explicit counterexample prevents an optimality claim", () -> {
            boolean[][] c = {{true,true,false},{false,false,true},{true,true,true}}; double[] w = {1.9,2,3};
            check(Math.abs(WeightedSetCover.solve(3,c,w).cost()-3.9)<1e-9 && exact(3,c,w)==3,"not optimal");
        });
        test("SC09 200 seeded instances checked against exhaustive optimum and harmonic bound", () -> {
            Random rng = new Random(2409540);
            for (int trial = 0; trial < 200; trial++) {
                int n = 1+rng.nextInt(8), m = 1+rng.nextInt(8);
                boolean[][] c = new boolean[m][n]; double[] w = new double[m];
                for (int j=0;j<m;j++) { w[j]=1+rng.nextInt(9); for(int i=0;i<n;i++) c[j][i]=rng.nextBoolean(); }
                Arrays.fill(c[0],true);
                var r = WeightedSetCover.solve(n,c,w); double optimum=exact(n,c,w), harmonic=0;
                for(int i=1;i<=n;i++) harmonic+=1.0/i;
                check(r.uncovered().isEmpty() && r.cost()+1e-9>=optimum && r.cost()<=harmonic*optimum+1e-9,"oracle");
                for(int i=0;i<n;i++) { boolean hit=false; for(int j:r.selected()) hit|=c[j][i]; check(hit,"coverage"); }
            }
        });
        test("QS01 singleton boundary", () -> check(RandomizedSelect.select(new double[]{7},0,1).value()==7,"singleton"));
        test("QS02 minimum and maximum ranks", () -> {
            double[] a={9,-2,4,0}; check(RandomizedSelect.select(a,0,1).value()==-2 && RandomizedSelect.select(a,3,1).value()==9,"extremes");
        });
        test("QS03 duplicate values preserve rank semantics", () -> check(RandomizedSelect.select(new double[]{2,8,2,2,9},2,1).value()==2,"duplicates"));
        test("QS04 all equal values terminate in one partition", () -> check(RandomizedSelect.select(new double[]{4,4,4,4,4},2,9).partitions()==1,"equal"));
        test("QS05 sorted and reversed arrays", () -> {
            check(RandomizedSelect.select(new double[]{1,2,3,4,5},2,12).value()==3,"sorted");
            check(RandomizedSelect.select(new double[]{5,4,3,2,1},2,12).value()==3,"reversed");
        });
        test("QS06 input preserved and seed reproducible", () -> {
            double[] a={4,1,8,2,6}; double[] copy=a.clone();
            check(RandomizedSelect.select(a,2,44).equals(RandomizedSelect.select(a,2,44)) && Arrays.equals(a,copy),"preserve");
        });
        test("QS07 empty, out-of-range and non-finite input rejected", () -> {
            rejects(() -> RandomizedSelect.select(new double[0],0,1));
            rejects(() -> RandomizedSelect.select(new double[]{2},1,1));
            rejects(() -> RandomizedSelect.select(new double[]{Double.NaN},0,1));
        });
        test("QS08 1000 random arrays compared with independent full-sort oracle", () -> {
            Random r=new Random(42);
            for(int trial=0;trial<1000;trial++) {
                double[] a=new double[1+r.nextInt(200)]; for(int i=0;i<a.length;i++) a[i]=r.nextInt(35)-17;
                double[] sorted=a.clone(); Arrays.sort(sorted); int rank=r.nextInt(a.length);
                check(RandomizedSelect.select(a,rank,trial).value()==sorted[rank],"sort oracle");
            }
        });
        test("CM01 black, white and published D65 red reference", () -> {
            double[] black=ColorMath.lab("#000000"), white=ColorMath.lab("#FFFFFF"), red=ColorMath.lab("#FF0000");
            check(Math.abs(black[0])<1e-6 && Math.abs(white[0]-100)<.001,"black/white");
            check(Math.abs(red[0]-53.2408)<.001 && Math.abs(red[1]-80.0925)<.001 && Math.abs(red[2]-67.2032)<.001,"red");
            check(ColorMath.distance(red,red)==0,"identity");
        });
        test("API01 duplicate targets consolidated; exact top-k ties remain deterministic", () -> {
            var p=Planner.plan(Map.of("targets","#000000,#000000,#FFFFFF","inks","#000000:1,#FFFFFF:1","tolerance","0","review","1"));
            check(p.get("duplicatesRemoved").equals(1) && p.get("review").equals(List.of(0)),"duplicates and ties");
        });
        test("API02 no eligible inks gives no fabricated proof or quantile", () -> {
            var p=Planner.plan(Map.of("targets","#FFFFFF","inks","#000000:1","tolerance","0"));
            check(p.get("feasible").equals(false) && p.get("p90")==null && ((List<?>)p.get("review")).isEmpty(),"no plan");
        });
        test("API03 infeasible coverage and press budget are distinct", () -> {
            var p=Planner.plan(Map.of("targets","#000000,#FFFFFF","inks","#000000:1,#FFFFFF:1","tolerance","0","maxInks","1"));
            check(p.get("feasible").equals(true) && p.get("withinPressLimit").equals(false),"budget");
        });
        test("API04 malformed, empty, duplicate and infinite inputs rejected", () -> {
            rejects(() -> Planner.plan(Map.of()));
            rejects(() -> Planner.plan(Map.of("targets","bad","inks","#000000:1")));
            rejects(() -> Planner.plan(Map.of("targets","#000000","inks","#000000:1,#000000:2")));
            rejects(() -> Planner.plan(Map.of("targets","#000000","inks","#000000:1","tolerance","NaN")));
        });
        String summary="\n"+passed+" named checks passed, including 1200 oracle cases.\n";
        System.out.println(summary);
        java.nio.file.Files.createDirectories(java.nio.file.Path.of("results"));
        java.nio.file.Files.writeString(java.nio.file.Path.of("results/tests.txt"),"OVERPRINT verification\nJava "+System.getProperty("java.version")+"\n"+String.join("\n",lines)+summary);
    }
}
