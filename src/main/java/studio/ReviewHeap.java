package studio;
import java.util.*;
/** Array-backed max heap. Higher error wins; equal errors use source order. */
public final class ReviewHeap {
 public static List<Integer> rank(List<Integer> indices,double[] errors){
  int[] heap=indices.stream().mapToInt(Integer::intValue).toArray();
  for(int i:heap)if(i<0||i>=errors.length||!Double.isFinite(errors[i]))throw new IllegalArgumentException("Invalid review error.");
  for(int i=heap.length/2-1;i>=0;i--)down(heap,i,heap.length,errors);
  List<Integer> out=new ArrayList<>();
  for(int size=heap.length;size>0;){out.add(heap[0]);heap[0]=heap[--size];down(heap,0,size,errors);}
  return out;
 }
 private static boolean above(int a,int b,double[] e){return e[a]>e[b]||(e[a]==e[b]&&a<b);}
 private static void down(int[] h,int i,int size,double[] e){while(2*i+1<size){int child=2*i+1;if(child+1<size&&above(h[child+1],h[child],e))child++;if(!above(h[child],h[i],e))return;int t=h[i];h[i]=h[child];h[child]=t;i=child;}}
}
