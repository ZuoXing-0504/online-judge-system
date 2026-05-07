"""Seed solutions for ALL 100 problems."""
import json, urllib.request, time

BASE = "http://localhost:8000/api/v1"
data = json.dumps({"username": "admin", "password": "admin123456"}).encode()
req = urllib.request.Request(f"{BASE}/auth/login", data=data, headers={"Content-Type": "application/json"})
token = json.loads(urllib.request.urlopen(req).read())["access_token"]

def put(slug, code, expl):
    body = json.dumps({"solution_code": code, "solution_explanation": expl}).encode()
    req = urllib.request.Request(
        f"{BASE}/problems/{slug}", data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
        method="PUT")
    try:
        r = urllib.request.urlopen(req)
        return r.code
    except Exception as e:
        return str(e)

S = {}  # slug -> (code, explanation)

# ── 基础输入输出 ──
S["hello-world"] = (
    'print("Hello, World!")',
    "最简单的程序，直接 print 输出字符串即可。"
)
S["a-minus-b"] = (
    "a, b = map(int, input().split())\nprint(a - b)",
    "读入两个整数，输出它们的差。与 A+B 完全对称。"
)
S["multiply"] = (
    "a, b = map(int, input().split())\nprint(a * b)",
    "读入两个整数，输出乘积。注意 Python 整数没有溢出问题。"
)
S["divide-floor"] = (
    "a, b = map(int, input().split())\nprint(a // b)",
    "整数除法用 // 运算符，自动向下取整。"
)
S["modulo"] = (
    "a, b = map(int, input().split())\nprint(a % b)",
    "取余用 % 运算符。注意 Python 中负数取余结果为正。"
)
S["average"] = (
    "n = int(input())\narr = list(map(int, input().split()))\nprint(f'{sum(arr)/n:.2f}')",
    "用 f-string 格式化保留两位小数。f'{val:.2f}'。"
)
S["max-of-two"] = (
    "a, b = map(int, input().split())\nprint(max(a, b))",
    "Python 内置 max() 函数直接返回较大值。"
)
S["min-of-three"] = (
    "a, b, c = map(int, input().split())\nprint(min(a, b, c))",
    "min() 可以接受多个参数，返回最小值。"
)
S["absolute-value"] = (
    "n = int(input())\nprint(abs(n))",
    "abs() 函数返回绝对值。"
)

# ── 条件判断 ──
S["leap-year"] = (
    'y = int(input())\nprint("YES" if (y % 400 == 0) or (y % 4 == 0 and y % 100 != 0) else "NO")',
    "格里高利闰年规则：能被400整除 或 (能被4整除且不能被100整除)。"
)
S["positive-negative"] = (
    'n = int(input())\nif n > 0: print("POSITIVE")\nelif n < 0: print("NEGATIVE")\nelse: print("ZERO")',
    "三种情况分别判断即可。"
)
S["triangle-type"] = (
    'a, b, c = map(int, input().split())\nif a + b <= c or a + c <= b or b + c <= a:\n    print("NOT")\nelif a == b == c:\n    print("EQUILATERAL")\nelif a == b or b == c or a == c:\n    print("ISOSCELES")\nelse:\n    print("SCALENE")',
    "先判断能否构成三角形（两边之和大于第三边），再判断类型。"
)
S["grade-score"] = (
    's = int(input())\nif s >= 90: print("A")\nelif s >= 80: print("B")\nelif s >= 70: print("C")\nelif s >= 60: print("D")\nelse: print("F")',
    "从高到低判断分数区间，用 elif 链。"
)
S["is-vowel"] = (
    'ch = input().strip()\nprint("YES" if ch in "aeiou" else "NO")',
    "用 in 运算符检查字符是否在元音集合中。"
)
S["three-sort"] = (
    "arr = list(map(int, input().split()))\nprint(*sorted(arr))",
    "sorted() 返回排序后的新列表，* 解包输出。"
)
S["valid-date"] = (
    "import calendar\ny, m, d = map(int, input().split())\ntry:\n    print('YES' if 1 <= d <= calendar.monthrange(y, m)[1] else 'NO')\nexcept:\n    print('NO')",
    "calendar.monthrange(y,m) 返回 (weekday, days_in_month)，判断日是否在范围内。"
)
S["century-year"] = (
    'y = int(input())\nprint("LEAP" if y % 400 == 0 or (y % 4 == 0 and y % 100 != 0) else "COMMON")',
    "与普通闰年判断规则相同，只是输出格式不同。"
)
S["weekday"] = (
    'days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]\nn = int(input())\nprint(days[n-1])',
    "用列表存储星期名，下标 n-1 取值。"
)

# ── 循环与累加 ──
S["sum-of-digits"] = (
    "n = input().strip()\nprint(sum(int(ch) for ch in n))",
    "转字符串后每个字符转 int，生成器表达式求和。"
)
S["reverse-number"] = (
    "n = input().strip()\nprint(int(n[::-1]))",
    "字符串切片 [::-1] 反转，int() 自动去前导零。"
)
S["factorial"] = (
    "n = int(input())\nr = 1\nfor i in range(2, n + 1): r *= i\nprint(r)",
    "n! = 1*2*3*...*n。循环累乘，n=0 时结果为 1。"
)
S["prime-factors"] = (
    "n = int(input())\nfactors = []\nd = 2\nwhile d * d <= n:\n    while n % d == 0:\n        factors.append(str(d))\n        n //= d\n    d += 1\nif n > 1:\n    factors.append(str(n))\nprint(*factors)",
    "从 2 开始试除，能整除就输出因子并缩小 n。最后若 n>1 说明是质数。O(sqrt(n))。"
)
S["lcm"] = (
    "import math\na, b = map(int, input().split())\nprint(a * b // math.gcd(a, b))",
    "lcm(a,b) = a * b / gcd(a,b)。注意整数除法用 //。"
)
S["tower-of-hanoi"] = (
    "n = int(input())\nprint(2**n - 1)",
    "汉诺塔最少步数 = 2^n - 1。递推公式：T(n) = 2*T(n-1) + 1。"
)

# ── 字符串 ──
S["str-length"] = (
    "s = input()\nprint(len(s))",
    "len() 返回字符串长度（字符数，含 Unicode）。"
)
S["str-reverse"] = (
    "s = input().strip()\nprint(s[::-1])",
    "切片 [::-1] 反转字符串，步长 -1 表示从右向左。"
)
S["to-uppercase"] = (
    "s = input()\nprint(s.upper())",
    ".upper() 方法将所有字母转大写。"
)
S["to-lowercase"] = (
    "s = input()\nprint(s.lower())",
    ".lower() 方法将所有字母转小写。"
)
S["count-char"] = (
    "s = input()\nch = input().strip()\nprint(s.count(ch))",
    ".count() 方法统计子串（单字符）出现次数。"
)
S["is-substring"] = (
    "S = input().strip()\nT = input().strip()\nprint('YES' if T in S else 'NO')",
    "in 运算符检查子串。注意区分大小写。"
)
S["remove-spaces"] = (
    "s = input()\nprint(s.replace(' ', ''))",
    ".replace() 将空格替换为空字符串。"
)
S["word-count"] = (
    "s = input().strip()\nprint(len(s.split()))",
    ".split() 默认按空白字符分割，返回单词列表。"
)
S["most-frequent-char"] = (
    "s = input().strip()\nfrom collections import Counter\nc = Counter(s)\nbest = max(c, key=lambda x: (c[x], -ord(x)))\nprint(best)",
    "Counter 统计频率。key 函数按 (频率, -ASCII) 排序。"
)
S["is-anagram"] = (
    "a = input().strip()\nb = input().strip()\nprint('YES' if sorted(a) == sorted(b) else 'NO')",
    "变位词判断：排序后比较。sorted() 返回字符列表。"
)

# ── 数组/列表 ──
S["array-sum"] = (
    "n = int(input())\narr = list(map(int, input().split()))\nprint(sum(arr))",
    "sum() 函数求和。"
)
S["array-max"] = (
    "n = int(input())\narr = list(map(int, input().split()))\nprint(max(arr))",
    "max() 函数求最大值。"
)
S["array-second-max"] = (
    "n = int(input())\narr = list(map(int, input().split()))\nunique = sorted(set(arr), reverse=True)\nprint(unique[1])",
    "set 去重，sorted 降序，取下标 1。"
)
S["remove-duplicates"] = (
    "n = int(input())\narr = list(map(int, input().split()))\nprint(*sorted(set(arr)))",
    "set() 去重，sorted() 排序。"
)
S["majority-element"] = (
    "n = int(input())\narr = list(map(int, input().split()))\ncandidate = count = 0\nfor x in arr:\n    if count == 0:\n        candidate = x\n    count += 1 if x == candidate else -1\nprint(candidate)",
    "Boyer-Moore 投票算法。O(n) 时间 O(1) 空间。多数元素一定存在。"
)
S["missing-number"] = (
    "n = int(input())\narr = list(map(int, input().split()))\ntotal = n * (n + 1) // 2\nprint(total - sum(arr))",
    "0 到 n 的和 = n(n+1)/2，减去数组和得到缺失数字。"
)
S["move-zeroes"] = (
    "n = int(input())\narr = list(map(int, input().split()))\nnon_zero = [x for x in arr if x != 0]\nprint(*(non_zero + [0] * (len(arr) - len(non_zero))))",
    "分离非零元素，补零到末尾。"
)
S["product-except-self"] = (
    "n = int(input())\narr = list(map(int, input().split()))\nprefix = [1] * n\nsuffix = [1] * n\nfor i in range(1, n):\n    prefix[i] = prefix[i-1] * arr[i-1]\nfor i in range(n-2, -1, -1):\n    suffix[i] = suffix[i+1] * arr[i+1]\nprint(*[prefix[i] * suffix[i] for i in range(n)])",
    "前缀积 × 后缀积。prefix[i] = arr[0]*...*arr[i-1], suffix[i] = arr[i+1]*...*arr[n-1]。O(n) 无除法。"
)

# ── 排序与搜索 ──
S["kth-largest"] = (
    "n, k = map(int, input().split())\narr = list(map(int, input().split()))\narr.sort(reverse=True)\nprint(arr[k-1])",
    "降序排序后取第 k-1 个。或用 heapq.nlargest(k, arr)[-1]。"
)
S["merge-sorted-arrays"] = (
    "n1, *a = map(int, input().split())\nn2, *b = map(int, input().split())\nprint(*sorted(a + b))",
    "合并后直接 sorted。O((n+m)log(n+m))。手动归并可达 O(n+m)。"
)
S["find-peak"] = (
    "n = int(input())\narr = list(map(int, input().split()))\nlo, hi = 0, n - 1\nwhile lo < hi:\n    mid = (lo + hi) // 2\n    if arr[mid] < arr[mid + 1]:\n        lo = mid + 1\n    else:\n        hi = mid\nprint(lo)",
    "二分搜索峰值。如果 arr[mid] < arr[mid+1]，峰值在右侧；否则在左侧（含 mid）。O(log n)。"
)
S["search-rotated"] = (
    "n, target = map(int, input().split())\narr = list(map(int, input().split()))\nlo, hi = 0, n - 1\nwhile lo <= hi:\n    mid = (lo + hi) // 2\n    if arr[mid] == target:\n        print(mid)\n        break\n    if arr[lo] <= arr[mid]:\n        if arr[lo] <= target < arr[mid]:\n            hi = mid - 1\n        else:\n            lo = mid + 1\n    else:\n        if arr[mid] < target <= arr[hi]:\n            lo = mid + 1\n        else:\n            hi = mid - 1\nelse:\n    print(-1)",
    "旋转数组二分搜索。先判断哪边有序，再根据 target 是否在有序区间内决定搜索方向。O(log n)。"
)
S["frequency-sort"] = (
    "from collections import Counter\nn = int(input())\narr = list(map(int, input().split()))\nc = Counter(arr)\nresult = sorted(arr, key=lambda x: (-c[x], x))\nprint(*result)",
    "Counter 统计频率，sorted 按 (-频率, 值) 排序。"
)
S["first-bad-version"] = (
    "n, k = map(int, input().split())\n# 模拟：版本 >= k 为错误\nlo, hi = 1, n\nwhile lo < hi:\n    mid = (lo + hi) // 2\n    if mid >= k:\n        hi = mid\n    else:\n        lo = mid + 1\nprint(lo)",
    "二分查找第一个错误版本。每当 mid 为错误时收缩右边界。O(log n)。"
)
S["median-two-sorted"] = (
    "n1, *a = map(int, input().split())\nn2, *b = map(int, input().split())\nc = sorted(a + b)\nmid = (len(c) - 1) / 2\nprint((c[int(mid)] + c[int(mid) + (0 if len(c) % 2 else 1)]) / 2)",
    "合并排序后取中位数。奇数长度取中间，偶数长度取两中间均值。手动二分可达 O(log(min(n,m)))。"
)
S["custom-sort"] = (
    "n = int(input())\narr = list(map(int, input().split()))\neven = sorted([x for x in arr if x % 2 == 0])\nodd = sorted([x for x in arr if x % 2 != 0])\nprint(*(even + odd))",
    "分离奇偶数分别排序后拼接。"
)

# ── 递归与DP ──
S["power-recursive"] = (
    "MOD = 1000000007\na, b = map(int, input().split())\ndef fast_pow(a, b):\n    if b == 0: return 1\n    half = fast_pow(a, b // 2)\n    result = (half * half) % MOD\n    return (result * a) % MOD if b % 2 else result\nprint(fast_pow(a, b))",
    "快速幂（二分幂）。a^b = (a^(b/2))^2，b 为奇数时多乘一个 a。O(log b)。"
)
S["euclidean-gcd-recursive"] = (
    "def gcd(a, b):\n    return a if b == 0 else gcd(b, a % b)\na, b = map(int, input().split())\nprint(gcd(a, b))",
    "递归欧几里得算法：gcd(a,b) = gcd(b, a%b)，直到 b=0。"
)
S["permutations"] = (
    "from itertools import permutations\nn = int(input())\nfor p in permutations(range(1, n + 1)):\n    print(*p)",
    "Python 的 itertools.permutations 直接生成全排列。手写用回溯。"
)
S["subset-sum"] = (
    "n, target = map(int, input().split())\narr = list(map(int, input().split()))\ndp = [False] * (target + 1)\ndp[0] = True\nfor x in arr:\n    for s in range(target, x - 1, -1):\n        dp[s] = dp[s] or dp[s - x]\nprint('YES' if dp[target] else 'NO')",
    "0-1 背包变体。dp[s] 表示是否能凑出和 s。倒序遍历避免重复使用。"
)
S["coin-change"] = (
    "amount, n = map(int, input().split())\ncoins = list(map(int, input().split()))\ndp = [float('inf')] * (amount + 1)\ndp[0] = 0\nfor coin in coins:\n    for x in range(coin, amount + 1):\n        dp[x] = min(dp[x], dp[x - coin] + 1)\nprint(dp[amount] if dp[amount] != float('inf') else -1)",
    "完全背包。dp[x] = 凑出金额 x 的最少硬币数。每种硬币无限使用，正序更新。"
)
S["knapsack-01"] = (
    "n, cap = map(int, input().split())\ndp = [0] * (cap + 1)\nfor _ in range(n):\n    w, v = map(int, input().split())\n    for c in range(cap, w - 1, -1):\n        dp[c] = max(dp[c], dp[c - w] + v)\nprint(dp[cap])",
    "0-1 背包。dp[c] = 容量 c 的最大价值。每种物品只能用一次，倒序更新。"
)
S["longest-common-subseq"] = (
    "S = input().strip()\nT = input().strip()\nn, m = len(S), len(T)\ndp = [[0] * (m + 1) for _ in range(n + 1)]\nfor i in range(n):\n    for j in range(m):\n        if S[i] == T[j]:\n            dp[i+1][j+1] = dp[i][j] + 1\n        else:\n            dp[i+1][j+1] = max(dp[i][j+1], dp[i+1][j])\nprint(dp[n][m])",
    "LCS 经典 DP。dp[i][j] = S[:i] 与 T[:j] 的 LCS 长度。字符相同时对角线+1，否则取 max(上方,左方)。"
)
S["edit-distance"] = (
    "S = input().strip()\nT = input().strip()\nn, m = len(S), len(T)\ndp = [[0]*(m+1) for _ in range(n+1)]\nfor i in range(n+1): dp[i][0] = i\nfor j in range(m+1): dp[0][j] = j\nfor i in range(1, n+1):\n    for j in range(1, m+1):\n        if S[i-1] == T[j-1]:\n            dp[i][j] = dp[i-1][j-1]\n        else:\n            dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])\nprint(dp[n][m])",
    "编辑距离（Levenshtein）。dp[i][j] 表示 S[:i] 转 T[:j] 的最少操作。三种操作：删、插、替换。"
)

# ── 数据结构模拟 ──
S["queue-simulation"] = (
    "from collections import deque\nn = int(input())\nq = deque()\nout = []\nfor _ in range(n):\n    op = input().split()\n    if op[0] == 'PUSH':\n        q.append(int(op[1]))\n    else:\n        out.append(str(q.popleft()))\nprint('\\n'.join(out))",
    "队列 FIFO。deque 的 popleft() 实现 O(1) 出队。"
)
S["stack-simulation"] = (
    "n = int(input())\nstack = []\nout = []\nfor _ in range(n):\n    op = input().split()\n    if op[0] == 'PUSH':\n        stack.append(int(op[1]))\n    else:\n        out.append(str(stack.pop()))\nprint('\\n'.join(out))",
    "栈 LIFO。list 的 append/pop 都是 O(1)。"
)
S["min-stack"] = (
    "n = int(input())\nstack = []\nmin_stack = []\nout = []\nfor _ in range(n):\n    op = input().split()\n    if op[0] == 'PUSH':\n        v = int(op[1])\n        stack.append(v)\n        if not min_stack or v <= min_stack[-1]:\n            min_stack.append(v)\n    elif op[0] == 'POP':\n        v = stack.pop()\n        out.append(str(v))\n        if v == min_stack[-1]:\n            min_stack.pop()\n    else:\n        out.append(str(min_stack[-1]))\nprint('\\n'.join(out))",
    "辅助栈存储当前最小值。push 时若新值 <= 最小栈顶，同步入栈；pop 时若值等于最小栈顶，同步出栈。"
)
S["lru-cache"] = (
    "from collections import OrderedDict\n\nn, cap = map(int, input().split())\ncache = OrderedDict()\nout = []\nfor _ in range(n):\n    op = input().split()\n    if op[0] == 'PUT':\n        k, v = int(op[1]), int(op[2])\n        if k in cache:\n            cache.move_to_end(k)\n        cache[k] = v\n        if len(cache) > cap:\n            cache.popitem(last=False)\n    else:\n        k = int(op[1])\n        if k in cache:\n            cache.move_to_end(k)\n            out.append(str(cache[k]))\n        else:\n            out.append('-1')\nprint('\\n'.join(out))",
    "OrderedDict 天然支持 LRU。move_to_end 移到末尾（最近使用），popitem(last=False) 删除最久未用。"
)
S["linked-list-cycle"] = (
    "n = int(input())\nnxt = {}\nfor _ in range(n):\n    node, nid = map(int, input().split())\n    nxt[node] = nid\nslow = fast = 0\nif n > 0:\n    slow = fast = next(iter(nxt))\nwhile fast != -1 and nxt.get(fast, -1) != -1:\n    slow = nxt.get(slow, -1)\n    fast = nxt.get(nxt.get(fast, -1), -1)\n    if slow == fast and slow != -1:\n        print('YES')\n        break\nelse:\n    print('NO')",
    "快慢指针检测环。慢指针走一步，快指针走两步，若相遇则有环。"
)
S["stack-to-queue"] = (
    "n = int(input())\nin_stack = []\nout_stack = []\nres = []\nfor _ in range(n):\n    op = input().split()\n    if op[0] == 'ENQ':\n        in_stack.append(int(op[1]))\n    else:\n        if not out_stack:\n            while in_stack:\n                out_stack.append(in_stack.pop())\n        res.append(str(out_stack.pop()))\nprint('\\n'.join(res))",
    "两个栈模拟队列。入队时 push 到 in_stack，出队时若 out_stack 为空则把 in_stack 全部倒到 out_stack 再 pop。"
)
S["postfix-eval"] = (
    "tokens = input().split()\nstack = []\nfor t in tokens:\n    if t in '+-*/':\n        b, a = stack.pop(), stack.pop()\n        if t == '+': stack.append(a + b)\n        elif t == '-': stack.append(a - b)\n        elif t == '*': stack.append(a * b)\n        else: stack.append(a / b)\n    else:\n        stack.append(float(t))\nprint(stack[0])",
    "后缀表达式求值：遇到数字入栈，遇到运算符弹出两个操作数计算后入栈。"
)
S["top-k-frequent"] = (
    "from collections import Counter\nn, k = map(int, input().split())\nwords = [input().strip() for _ in range(n)]\nc = Counter(words)\nresult = sorted(c, key=lambda w: (-c[w], w))\nprint('\\n'.join(result[:k]))",
    "Counter 统计频率，按 (-频率, 字典序) 排序取前 k。"
)
S["hash-table-sim"] = (
    "n, size = map(int, input().split())\nht = [None] * size\nres = []\nfor _ in range(n):\n    op = input().split()\n    if op[0] == 'INSERT':\n        v = int(op[1])\n        idx = v % size\n        while ht[idx] is not None and ht[idx] != v:\n            idx = (idx + 1) % size\n        ht[idx] = v\n    elif op[0] == 'FIND':\n        v = int(op[1])\n        idx = v % size\n        found = False\n        while ht[idx] is not None:\n            if ht[idx] == v:\n                found = True\n                break\n            idx = (idx + 1) % size\n        res.append('FOUND' if found else 'NOTFOUND')\n    else:\n        v = int(op[1])\n        idx = v % size\n        while ht[idx] is not None:\n            if ht[idx] == v:\n                ht[idx] = None\n                break\n            idx = (idx + 1) % size\nprint('\\n'.join(res))",
    "开放寻址法哈希表。冲突时线性探测 (idx + 1) % size。"
)

# ── 综合题 ──
S["int-to-roman"] = (
    "n = int(input())\nvals = [(1000,'M'),(900,'CM'),(500,'D'),(400,'CD'),(100,'C'),(90,'XC'),(50,'L'),(40,'XL'),(10,'X'),(9,'IX'),(5,'V'),(4,'IV'),(1,'I')]\nresult = []\nfor v, s in vals:\n    while n >= v:\n        result.append(s)\n        n -= v\nprint(''.join(result))",
    "贪心法。从大到小枚举罗马数字符号，每次能减就减并拼接。"
)
S["happy-number"] = (
    "n = int(input())\nseen = set()\nwhile n != 1 and n not in seen:\n    seen.add(n)\n    n = sum(int(d)**2 for d in str(n))\nprint('YES' if n == 1 else 'NO')",
    "用集合记录出现过的数。若重复出现且不为 1 说明进入循环，不是快乐数。"
)
S["sudoku-validator"] = (
    "grid = [list(map(int, input().split())) for _ in range(9)]\ndef valid():\n    for i in range(9):\n        row = set()\n        col = set()\n        for j in range(9):\n            if grid[i][j] < 1 or grid[i][j] > 9: return False\n            row.add(grid[i][j])\n            col.add(grid[j][i])\n        if len(row) != 9 or len(col) != 9: return False\n    for bi in range(0, 9, 3):\n        for bj in range(0, 9, 3):\n            box = set()\n            for i in range(3):\n                for j in range(3):\n                    box.add(grid[bi+i][bj+j])\n            if len(box) != 9: return False\n    return True\nprint('YES' if valid() else 'NO')",
    "数独验证：检查每行、每列、每个 3x3 宫格是否包含 1-9 各一次。用集合判断重复。"
)
S["spiral-matrix"] = (
    "n = int(input())\nmat = [[0]*n for _ in range(n)]\ntop, bot, left, right = 0, n-1, 0, n-1\nnum = 1\nwhile top <= bot and left <= right:\n    for j in range(left, right+1):\n        mat[top][j] = num\n        num += 1\n    top += 1\n    for i in range(top, bot+1):\n        mat[i][right] = num\n        num += 1\n    right -= 1\n    if top <= bot:\n        for j in range(right, left-1, -1):\n            mat[bot][j] = num\n            num += 1\n        bot -= 1\n    if left <= right:\n        for i in range(bot, top-1, -1):\n            mat[i][left] = num\n            num += 1\n        left += 1\nfor row in mat:\n    print(*row)",
    "螺旋填充：定义上下左右四边界，依次向右、下、左、上填充，每填完一边收缩边界。"
)
S["collatz"] = (
    "n = int(input())\nwhile n != 1:\n    print(n)\n    n = n // 2 if n % 2 == 0 else 3 * n + 1\nprint(1)",
    "Collatz 猜想：偶数除 2，奇数乘 3 加 1，最终必定到达 1。"
)
S["power-of-two"] = (
    'n = int(input())\nprint("YES" if n > 0 and (n & (n - 1)) == 0 else "NO")',
    "2 的幂的二进制只有一个 1。n & (n-1) == 0 是经典判断法。"
)
S["rotate-array"] = (
    "n, k = map(int, input().split())\narr = list(map(int, input().split()))\nk %= n\nprint(*(arr[-k:] + arr[:-k]))",
    "右旋 k 位 = 后 k 个元素移到前面。切片 arr[-k:] + arr[:-k]。"
)
S["longest-word"] = (
    "import re\nwords = re.findall(r'[a-zA-Z]+', input())\nprint(max(words, key=len) if words else '')",
    "正则提取所有字母单词，max 按长度取最长。"
)
S["trailing-zeros"] = (
    "n = int(input())\ncount = 0\nwhile n >= 5:\n    n //= 5\n    count += n\nprint(count)",
    "n! 尾部零的个数 = n 中因子 5 的数量。不断除以 5 累加。"
)
S["perfect-square"] = (
    "import math\nn = int(input())\nr = int(math.sqrt(n))\nprint('YES' if r * r == n else 'NO')",
    "开方后取整，平方回比原数。"
)
S["max-profit-stock"] = (
    "n = int(input())\nprices = list(map(int, input().split()))\nmin_price = float('inf')\nmax_profit = 0\nfor p in prices:\n    if p < min_price:\n        min_price = p\n    elif p - min_price > max_profit:\n        max_profit = p - min_price\nprint(max_profit)",
    "遍历时维护历史最低价，当天卖出的利润 = 当前价 - 最低价，取最大。"
)
S["encode-run-length"] = (
    "s = input().strip()\nif not s:\n    print('')\nelse:\n    result = []\n    count = 1\n    for i in range(1, len(s)):\n        if s[i] == s[i-1]:\n            count += 1\n        else:\n            result.append(f'{count if count > 1 else \"\"}{s[i-1]}')\n            count = 1\n    result.append(f'{count if count > 1 else \"\"}{s[-1]}')\n    print(''.join(result))",
    "行程编码：遍历字符串，统计连续相同字符个数，大于 1 时写数字+字符，否则只写字符。"
)
S["decode-run-length"] = (
    "s = input().strip()\nimport re\nresult = []\nfor num, ch in re.findall(r'(\\d*)([A-Z])', s):\n    result.append(ch * (int(num) if num else 1))\nprint(''.join(result))",
    "正则提取 (数字?)(字母) 对，数字为空表示 1，重复字母相应次数。"
)
S["bubble-sort"] = (
    "n = int(input())\narr = list(map(int, input().split()))\nfor i in range(n):\n    swapped = False\n    for j in range(n - i - 1):\n        if arr[j] > arr[j + 1]:\n            arr[j], arr[j + 1] = arr[j + 1], arr[j]\n            swapped = True\n    if not swapped:\n        break\nprint(*arr)",
    "冒泡排序：相邻比较，大的往后移。swapped 标志提前退出优化。平均 O(n^2)，最佳 O(n)。"
)

# ── Write all ──
print(f"Seeding {len(S)} solutions...")
done = 0
for slug, (code, expl) in S.items():
    status = put(slug, code, expl)
    if status == 200:
        done += 1
        print(f"  [{done:3d}] {slug}")
    else:
        print(f"  [ERR] {slug}: {status}")
    time.sleep(0.03)

print(f"\nDone. {done}/{len(S)} solutions added.")
