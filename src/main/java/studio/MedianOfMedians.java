package studio;
/** Deterministic selection: groups of five, recursive pivot, three-way partition. */
public final class MedianOfMedians {
 public static double select(double[] input,int rank){
  if(input==null||rank<0||rank>=input.length)throw new IllegalArgumentException("Invalid selection rank.");
  for(double v:input)if(!Double.isFinite(v))throw new IllegalArgumentException("Finite values required.");
  return pick(input.clone(),rank);
 }
 private static void insertion(double[] a,int lo,int hi){for(int i=lo+1;i<hi;i++){double v=a[i];int j=i-1;while(j>=lo&&a[j]>v){a[j+1]=a[j];j--;}a[j+1]=v;}}
 private static double pick(double[] a,int k){
  if(a.length<=5){insertion(a,0,a.length);return a[k];}
  double[] medians=new double[(a.length+4)/5];
  for(int i=0;i<a.length;i+=5){int end=Math.min(i+5,a.length);insertion(a,i,end);medians[i/5]=a[i+(end-i)/2];}
  double pivot=pick(medians,medians.length/2);int less=0,equal=0;
  for(double v:a){if(v<pivot)less++;else if(v==pivot)equal++;}
  if(k>=less&&k<less+equal)return pivot;
  boolean left=k<less;double[] next=new double[left?less:a.length-less-equal];int pos=0;
  for(double v:a)if(left?v<pivot:v>pivot)next[pos++]=v;
  return pick(next,left?k:k-less-equal);
 }
}
