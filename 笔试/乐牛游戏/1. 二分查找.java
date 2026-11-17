import java.util.*;

public class Solution{
    public int search(int[] nums, int target) {
        int left = 0;
        int right = nums.length - 1;

        while (left <= right) {
            // 防止 left + right 溢出，更安全的写法
            int mid = left + (right - left) / 2;

            if (nums[mid] == target) {
                return mid;
            } else if (nums[mid] < target) {
                left = mid + 1; // 注意这里：必须是 mid + 1
            } else {
                right = mid - 1;
            }
        }
        return -1;
    }
}