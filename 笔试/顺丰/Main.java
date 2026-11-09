import java.util.*;
import java.io.*;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int T = sc.nextInt();
        while (T-- > 0) {
            int L = sc.nextInt();
            int startFuel = sc.nextInt();
            int n = sc.nextInt();

            int[][] stations = new int[n][2];
            for (int i = 0; i < n; i++) {
                stations[i][0] = sc.nextInt(); // 位置
                stations[i][1] = sc.nextInt(); // 油量
            }

            // 使用优先队列（最大堆）
            PriorityQueue<Integer> pq = new PriorityQueue<>(Collections.reverseOrder());
            int currentFuel = startFuel;
            int currentPosition = 0;
            int ans = 0;

            // 遍历所有加油站和终点
            for (int i = 0; i <= n; i++) {
                int targetPos = (i == n) ? L : stations[i][0];
                int dist = targetPos - currentPosition;

                // 油不够时，从pq中取最大油量
                while (currentFuel < dist && !pq.isEmpty()) {
                    currentFuel += pq.poll();
                    ans++;
                }

                if (currentFuel < dist) {
                    ans = -1;
                    break;
                }

                currentFuel -= dist;
                currentPosition = targetPos;

                // 如果是加油站，将其油量加入pq
                if (i < n) {
                    pq.add(stations[i][1]);
                }
            }

            System.out.println(ans);
        }
    }
}