"""Seed official solutions for key problems."""
import json, urllib.request

BASE = "http://localhost:8000/api/v1"
data = json.dumps({"username": "admin", "password": "admin123456"}).encode()
req = urllib.request.Request(f"{BASE}/auth/login", data=data, headers={"Content-Type": "application/json"})
token = json.loads(urllib.request.urlopen(req).read())["access_token"]

SOLUTIONS = {
    "hello-world": (
        'print("Hello, World!")',
        "最简单的程序。直接 print 输出。Python 的 print 函数会自动换行。"
    ),
    "a-plus-b": (
        "import sys\na, b = map(int, sys.stdin.read().split())\nprint(a + b)",
        "用 sys.stdin.read() 读入两个整数，输出它们的和。map(int, ...) 一次性转整数。考察基本输入输出。"
    ),
    "even-odd": (
        'n = int(input())\nprint("EVEN" if n % 2 == 0 else "ODD")',
        "判断奇偶：用取余运算符 %。偶数对 2 取余为 0，奇数为 1。"
    ),
    "leap-year": (
        'y = int(input())\nprint("YES" if (y % 400 == 0) or (y % 4 == 0 and y % 100 != 0) else "NO")',
        "闰年规则：能被 400 整除，或能被 4 整除但不能被 100 整除。"
    ),
    "sum-1-to-n": (
        "n = int(input())\nprint(n * (n + 1) // 2)",
        "高斯公式：1+2+...+n = n(n+1)/2。O(1) 时间，比循环快得多。"
    ),
    "sum-of-digits": (
        "n = input().strip()\nprint(sum(int(ch) for ch in n))",
        "将数字转为字符串，每个字符转 int 后求和。"
    ),
    "reverse-number": (
        "n = input().strip()\nprint(int(n[::-1]))",
        "用切片 [::-1] 反转字符串，int() 自动去掉前导零。"
    ),
    "factorial": (
        "n = int(input())\nresult = 1\nfor i in range(2, n + 1):\n    result *= i\nprint(result)",
        "阶乘 n! = 1x2x3x...xn。循环累乘，n=0 时结果为 1（循环不执行）。"
    ),
    "prime-check": (
        "import math\nn = int(input())\n\ndef is_prime(n):\n    if n < 2:\n        return False\n    for i in range(2, int(math.sqrt(n)) + 1):\n        if n % i == 0:\n            return False\n    return True\n\nprint('YES' if is_prime(n) else 'NO')",
        "质数判断只需检查到 sqrt(n)。如果 n 有大于 sqrt(n) 的因子，一定也有一个小于 sqrt(n) 的因子。O(sqrt(n))。"
    ),
    "gcd": (
        "import math\na, b = map(int, input().split())\nprint(math.gcd(a, b))",
        "最大公约数用 math.gcd。手写用欧几里得算法：gcd(a,b) = gcd(b, a%b)，递归直到 b=0。"
    ),
    "palindrome-number": (
        'n = input().strip()\nprint("YES" if n == n[::-1] else "NO")',
        "字符串反转用切片 [::-1]，比较原串和反转串是否相同。"
    ),
    "fizzbuzz": (
        "n = int(input())\nfor i in range(1, n + 1):\n    if i % 15 == 0:\n        print('FizzBuzz')\n    elif i % 3 == 0:\n        print('Fizz')\n    elif i % 5 == 0:\n        print('Buzz')\n    else:\n        print(i)",
        "经典面试题。注意 15 的检查要放在 3 和 5 之前，否则 15 会输出 Fizz 而不是 FizzBuzz。"
    ),
    "armstrong-number": (
        'n = int(input())\na, b, c = n // 100, (n // 10) % 10, n % 10\nprint("YES" if a**3 + b**3 + c**3 == n else "NO")',
        "水仙花数：各位数字立方和等于自身。如 153 = 1^3 + 5^3 + 3^3。拆出百位、十位、个位后计算。"
    ),
    "fibonacci": (
        "n = int(input())\na, b = 0, 1\nfor _ in range(n):\n    a, b = b, a + b\nprint(a)",
        "斐波那契：F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2)。迭代 O(n)，O(1) 空间。比递归高效得多。"
    ),
    "climbing-stairs": (
        "n = int(input())\na, b = 1, 1\nfor _ in range(n - 1):\n    a, b = b, a + b\nprint(b if n > 0 else 1)",
        "本质是斐波那契。到达第 n 级 = 到 n-1 级 + 到 n-2 级。DP 入门题。"
    ),
    "valid-parentheses": (
        "s = input().strip()\nstack = []\npairs = {')': '(', ']': '[', '}': '{'}\nfor ch in s:\n    if ch in '([{':\n        stack.append(ch)\n    else:\n        if not stack or stack[-1] != pairs[ch]:\n            print('NO')\n            break\n        stack.pop()\nelse:\n    print('YES' if not stack else 'NO')",
        "用栈匹配括号。左括号入栈，右括号检查栈顶。最后栈为空则有效。栈是处理嵌套结构的核心工具。"
    ),
    "binary-search": (
        "n, target = map(int, input().split())\narr = list(map(int, input().split()))\nlo, hi = 0, n - 1\nwhile lo <= hi:\n    mid = (lo + hi) // 2\n    if arr[mid] == target:\n        print(mid)\n        break\n    elif arr[mid] < target:\n        lo = mid + 1\n    else:\n        hi = mid - 1\nelse:\n    print(-1)",
        "二分查找核心思想：每次将搜索范围减半。时间复杂度 O(log n)。前提是数组有序。"
    ),
    "two-sum": (
        "n, target = map(int, input().split())\narr = list(map(int, input().split()))\nseen = {}\nfor i, val in enumerate(arr):\n    need = target - val\n    if need in seen:\n        print(seen[need], i)\n        break\n    seen[val] = i\nelse:\n    print('-1 -1')",
        "哈希表记录已遍历值的下标。O(n) 时间 O(n) 空间。比暴力 O(n^2) 快得多。"
    ),
    "max-subarray-sum": (
        "n = int(input())\narr = list(map(int, input().split()))\nbest = cur = arr[0]\nfor x in arr[1:]:\n    cur = max(x, cur + x)\n    best = max(best, cur)\nprint(best)",
        "Kadane 算法。cur 表示以当前位置结尾的最大子数组和。每步决策：延伸前一子数组或重新开始。O(n) 经典一维 DP。"
    ),
    "josephus": (
        "n, k = map(int, input().split())\npos = 0\nfor i in range(2, n + 1):\n    pos = (pos + k) % i\nprint(pos + 1)",
        "约瑟夫环数学解：递推 f(1)=0, f(i)=(f(i-1)+k)%i。最后 +1 转 1-based。O(n)。"
    ),
}

for slug, (code, expl) in SOLUTIONS.items():
    body = json.dumps({"solution_code": code, "solution_explanation": expl}).encode()
    req = urllib.request.Request(
        f"{BASE}/problems/{slug}",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="PUT",
    )
    try:
        resp = urllib.request.urlopen(req)
        print(f"  [+] {slug} ({resp.code})")
    except Exception as e:
        print(f"  [!] {slug}: {e}")

print(f"Done. {len(SOLUTIONS)} solutions seeded.")
