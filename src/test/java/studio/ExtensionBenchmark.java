package studio;
import java.util.*;
import java.nio.file.*;
public class ExtensionBenchmark {
 static volatile double sink;
 static double time(Runnable r){for(int i=0;i<8;i++)r.run();double[] t=new double[15];for(int i=0;i<t.length;i++){long start=System.nanoTime();r.run();t[i]=(System.nanoTime()-start)/1e6;}Arrays.sort(t);return t[7];}
 public static void main(String[] args)throws Exception{
  StringBuilder out=new StringBuilder("n,median_of_medians_ms,heap_all_entries_ms\n");
  for(int n:new int[]{100,1000,10000}){Random random=new Random(2409540);double[] a=new double[n];List<Integer> ids=new ArrayList<>();for(int i=0;i<n;i++){a[i]=random.nextDouble()*50;ids.add(i);}double med=time(()->sink=MedianOfMedians.select(a,n/2)),heap=time(()->sink=ReviewHeap.rank(ids,a).get(0));out.append(n+","+med+","+heap+"\n");}
  if(!Double.isFinite(sink))throw new AssertionError();Files.writeString(Path.of("results/extension-benchmarks.csv"),out);System.out.println(out);
 }
}
