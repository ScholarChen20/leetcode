import java.util.Scanner;

public class Main {
    /**
    大小写转换：
    输入一个字符，如果是大写字母，输出小写字母，如果是小写字母，输出大写字母，其他字符不变。
    */
    public static void main(String[] args) {
        Scanner in = new Scanner(System.in);

        // 题目要求多组输入，使用 hasNext() 判断是否还有下一个输入
        while (in.hasNext()) {
            String str = in.next(); // 读取输入的字符串
            char ch = str.charAt(0); // 获取第一个字符

            // 判断是否为空，防止空指针或越界
            if(str.length() > 0){
                char ch = str.charAt(0);

                if (ch >= 'A' && ch <= 'Z') {
                    char lower = (char) (ch + 32);
                    System.out.println(lower);
                } else if (ch >= 'a' && ch <= 'z') {
                    char upper = (char) (ch - 32);
                    System.out.println(upper);
                }
            }
        }
        in.close();
    }
}