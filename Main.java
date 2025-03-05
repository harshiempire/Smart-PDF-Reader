import java.util.*;

class Solution {
    public int[][] mergeArrays(int[][] nums1, int[][] nums2) {
        HashMap<Integer, Integer> map = new HashMap<>();
        int max = 0;
        for (int i = 0; i < nums1.length; i++) {

            max = Math.max(max, nums1[i][0]);
            if (!map.containsKey(nums1[i][0]))
                map.put(nums1[i][0], 0);
            map.put(nums1[i][0], map.get(nums1[i][0]) + nums1[i][1]);

        }
        for (int i = 0; i < nums2.length; i++) {
 
            max = Math.max(max, nums2[i][0]);
            if (!map.containsKey(nums2[i][0]))
                map.put(nums2[i][0], 0);
            map.put(nums2[i][0], map.get(nums2[i][0]) + nums2[i][1]);
        }
        System.out.println(max + " " + map);
        ArrayList<Integer> sortedKeys
            = new ArrayList<Integer>(map.keySet());
 
        Collections.sort(sortedKeys);

        int[][] newArr = new int[sortedKeys.size()][2]; // Placeholder for now
        int ind = 0;
        for (int i : sortedKeys) {
            newArr[ind++] = new int[]{i,map.get(i)};
        }
        return newArr;
    }
}

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // Read size of nums1
        int m = scanner.nextInt();
        int[][] nums1 = new int[m][2];
        for (int i = 0; i < m; i++) {
            nums1[i][0] = scanner.nextInt();
            nums1[i][1] = scanner.nextInt();
        }

        // Read size of nums2
        int n = scanner.nextInt();
        int[][] nums2 = new int[n][2];
        for (int i = 0; i < n; i++) {
            nums2[i][0] = scanner.nextInt();
            nums2[i][1] = scanner.nextInt();
        }

        Solution solution = new Solution();
        int[][] result = solution.mergeArrays(nums1, nums2);

        // Print the result (currently empty)
        for (int[] arr : result) {
            System.out.println(arr[0] + " " + arr[1]);
        }

        scanner.close();
    }
}
