package studio;
import java.util.*;
public class ExtendedTests {
 public static void main(String[] args){
  double[][] cases={{7},{3,1,2},{5,5,5,5},{9,8,7,6,5,4,3,2,1},{-4,8,-2,0,8,3}};
  for(double[] a:cases){double[] sorted=a.clone();Arrays.sort(sorted);for(int k=0;k<a.length;k++)if(MedianOfMedians.select(a,k)!=sorted[k])throw new AssertionError("Median oracle");
   List<Integer> ids=new ArrayList<>();for(int i=0;i<a.length;i++)ids.add(i);List<Integer> oracle=new ArrayList<>(ids);oracle.sort((i,j)->a[i]==a[j]?Integer.compare(i,j):Double.compare(a[j],a[i]));if(!ReviewHeap.rank(ids,a).equals(oracle))throw new AssertionError("Heap oracle");}
  if(!ReviewHeap.rank(List.of(),new double[0]).isEmpty())throw new AssertionError();
  try{MedianOfMedians.select(new double[0],0);throw new AssertionError();}catch(IllegalArgumentException expected){}
  Random rng=new Random(2409540);
  for(int t=0;t<500;t++){double[] a=new double[1+rng.nextInt(300)];for(int i=0;i<a.length;i++)a[i]=rng.nextInt(100);double[] sorted=a.clone();Arrays.sort(sorted);int k=rng.nextInt(a.length);if(MedianOfMedians.select(a,k)!=sorted[k])throw new AssertionError();}
  for(String method:List.of("randomized","deterministic")){var result=Planner.plan(Map.of("targets","#EC6033,#2D488B,#E9BF44","inks","#EC6033:1,#2D488B:1,#E9BF44:1","method",method));if(!result.get("rankedReview").equals(List.of(0,1,2)))throw new AssertionError();}
  System.out.println("PASS 5 fixed oracle cases per new algorithm, heap empty boundary, selection invalid input, 500 generated selection cases and both planner modes.");
 }
}
