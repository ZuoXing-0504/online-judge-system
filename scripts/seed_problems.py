"""Seed 100 classic competitive programming problems into the online judge."""

import itertools
import json
import time
import urllib.request

BASE = "http://localhost:8000/api/v1"
PROBLEMS = []


def api(method, path, data=None, token=""):
    url = f"{BASE}{path}"
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read()) if resp.status != 204 else {}
    except urllib.error.HTTPError as e:
        print(f"  API error {e.code}: {e.read().decode()[:200]}")
        return None


def login():
    data = api("POST", "/auth/login", {"username": "admin", "password": "admin123456"})
    if not data:
        print("Login failed, registering...")
        api("POST", "/auth/register", {"username": "admin", "email": "admin@oj.com", "password": "admin123456"})
        data = api("POST", "/auth/login", {"username": "admin", "password": "admin123456"})
    return data.get("access_token", "")


def create_problem(token, p):
    existing = api("GET", f"/problems/{p['slug']}")
    if existing and "slug" in existing:
        return existing
    result = api("POST", "/problems", p, token)
    return result


def add_test_case(token, slug, tc):
    return api("POST", f"/problems/{slug}/test-cases", tc, token)


# ── Problem definitions ──────────────────────────────────────────────
# Format: (slug, title, description, difficulty, input_desc, output_desc,
#          sample_input, sample_output, test_cases)
# test_cases: list of (input, expected_output, is_sample)

def build_problems():
    out = []
    seq = itertools.count(1)

    # ── 1-10: 基础输入输出 ──
    out.append(("hello-world", "Hello World", "输出 'Hello, World!'。", "easy",
        "无输入。", "输出一行 Hello, World!。", "", "Hello, World!",
        [("", "Hello, World!", True),
         ("", "Hello, World!", False)]))
    out.append(("a-plus-b", "A + B 问题", "读入两个整数 a 和 b，输出它们的和。", "easy",
        "一行两个空格分隔的整数。", "一个整数 a + b。", "3 5", "8",
        [("3 5", "8", True),
         ("-1 1", "0", False),
         ("1000000 2000000", "3000000", False)]))
    out.append(("a-minus-b", "A - B 问题", "读入两个整数 a 和 b，输出 a - b。", "easy",
        "一行两个空格分隔的整数。", "一个整数 a - b。", "10 3", "7",
        [("10 3", "7", True), ("0 5", "-5", False)]))
    out.append(("multiply", "乘法运算", "读入两个整数，输出它们的乘积。", "easy",
        "一行两个空格分隔的整数。", "乘积。", "6 7", "42",
        [("6 7", "42", True), ("0 100", "0", False)]))
    out.append(("divide-floor", "整数除法", "读入两个整数 a 和 b，输出 a // b（整数除法）。保证 b != 0。", "easy",
        "一行两个空格分隔的整数。", "a // b 的结果。", "10 3", "3",
        [("10 3", "3", True), ("7 2", "3", False)]))
    out.append(("modulo", "取余运算", "读入两个整数 a 和 b，输出 a % b。", "easy",
        "一行两个空格分隔的整数。", "a % b 的结果。", "17 5", "2",
        [("17 5", "2", True), ("10 3", "1", False)]))
    out.append(("average", "求平均值", "读入 n 和 n 个整数，输出它们的平均值（保留两位小数）。", "easy",
        "第一行一个整数 n，第二行 n 个空格分隔的整数。", "平均值，保留两位小数。", "3\n10 20 30", "20.00",
        [("3\n10 20 30", "20.00", True),
         ("4\n1 2 3 4", "2.50", False)]))
    out.append(("max-of-two", "两数较大值", "读入两个整数，输出较大的那个。", "easy",
        "一行两个整数。", "较大的整数。", "3 7", "7",
        [("3 7", "7", True), ("100 50", "100", False)]))
    out.append(("min-of-three", "三数最小值", "读入三个整数，输出最小的那个。", "easy",
        "一行三个空格分隔的整数。", "最小的整数。", "5 2 8", "2",
        [("5 2 8", "2", True), ("-1 -5 0", "-5", False)]))
    out.append(("absolute-value", "绝对值", "读入一个整数，输出它的绝对值。", "easy",
        "一个整数。", "该整数的绝对值。", "-42", "42",
        [("-42", "42", True), ("0", "0", False), ("100", "100", False)]))

    # ── 11-20: 条件判断 ──
    out.append(("even-odd", "判断奇偶", "读入一个整数，如果是偶数输出 EVEN，奇数输出 ODD。", "easy",
        "一个整数。", "EVEN 或 ODD。", "4", "EVEN",
        [("4", "EVEN", True), ("7", "ODD", False), ("0", "EVEN", False)]))
    out.append(("leap-year", "闰年判断", "读入一个年份，判断是否为闰年。是输出 YES，否输出 NO。", "easy",
        "一个整数年份。", "YES 或 NO。", "2000", "YES",
        [("2000", "YES", True), ("1900", "NO", False), ("2024", "YES", False)]))
    out.append(("positive-negative", "正负零判断", "读入一个整数，正数输出 POSITIVE，负数输出 NEGATIVE，零输出 ZERO。", "easy",
        "一个整数。", "POSITIVE / NEGATIVE / ZERO。", "-5", "NEGATIVE",
        [("-5", "NEGATIVE", True), ("0", "ZERO", False), ("10", "POSITIVE", False)]))
    out.append(("triangle-type", "三角形类型", "读入三个正整数 a,b,c，判断能否构成三角形，以及类型：等边 EQUILATERAL、等腰 ISOSCELES、不等边 SCALENE、不能则 NOT。", "medium",
        "一行三个空格分隔的整数。", "三角形类型。", "3 3 3", "EQUILATERAL",
        [("3 3 3", "EQUILATERAL", True), ("3 3 4", "ISOSCELES", False),
         ("3 4 5", "SCALENE", False), ("1 2 5", "NOT", False)]))
    out.append(("grade-score", "成绩等级", "读入分数(0-100)，输出等级：A(90-100)、B(80-89)、C(70-79)、D(60-69)、F(0-59)。", "easy",
        "一个 0-100 的整数。", "等级字母。", "85", "B",
        [("85", "B", True), ("95", "A", False), ("60", "D", False), ("45", "F", False)]))
    out.append(("is-vowel", "元音判断", "读入一个小写字母，判断是否为元音(a,e,i,o,u)。是输出 YES，否输出 NO。", "easy",
        "一个小写字母。", "YES 或 NO。", "a", "YES",
        [("a", "YES", True), ("b", "NO", False), ("u", "YES", False)]))
    out.append(("three-sort", "三数排序", "读入三个整数，按从小到大顺序用空格分隔输出。", "easy",
        "一行三个整数。", "从小到大排序后的三个整数。", "3 1 2", "1 2 3",
        [("3 1 2", "1 2 3", True), ("9 0 5", "0 5 9", False)]))
    out.append(("valid-date", "合法日期", "读入年月日三个整数，判断是否为一个合法的日期。是输出 YES，否输出 NO。", "medium",
        "一行三个整数 y m d。", "YES 或 NO。", "2024 2 29", "YES",
        [("2024 2 29", "YES", True), ("2023 2 29", "NO", False),
         ("2024 4 31", "NO", False), ("2024 7 15", "YES", False)]))
    out.append(("century-year", "世纪闰年判断", "读入一个年份，按格里高利规则判断：能被400整除是闰年，或能被4整除但不能被100整除是闰年。", "easy",
        "一个整数。", "LEAP 或 COMMON。", "1600", "LEAP",
        [("1600", "LEAP", True), ("1700", "COMMON", False), ("2024", "LEAP", False)]))
    out.append(("weekday", "星期几", "读入1-7的整数，1=Monday...7=Sunday，输出对应的英文星期名。", "easy",
        "一个1-7的整数。", "英文星期名。", "1", "Monday",
        [("1", "Monday", True), ("7", "Sunday", False), ("3", "Wednesday", False)]))

    # ── 21-30: 循环与累加 ──
    out.append(("sum-1-to-n", "1到N求和", "读入正整数 n，输出 1+2+...+n。", "easy",
        "一个正整数 n。", "和。", "100", "5050",
        [("100", "5050", True), ("1", "1", False), ("1000", "500500", False)]))
    out.append(("factorial", "阶乘", "读入非负整数 n，输出 n!。", "medium",
        "一个整数 n (0 <= n <= 20)。", "n! 的值。", "5", "120",
        [("5", "120", True), ("0", "1", False), ("10", "3628800", False)]))
    out.append(("sum-of-digits", "各位数字之和", "读入一个正整数，输出各位数字之和。", "easy",
        "一个正整数。", "各位数字之和。", "12345", "15",
        [("12345", "15", True), ("1000", "1", False), ("999", "27", False)]))
    out.append(("reverse-number", "反转数字", "读入一个正整数，输出它的反转形式（去掉前导零）。", "easy",
        "一个正整数。", "反转后的数字。", "12300", "321",
        [("12300", "321", True), ("1000", "1", False), ("54321", "12345", False)]))
    out.append(("palindrome-number", "回文数判断", "读入一个正整数，判断是否为回文数。是输出 YES，否输出 NO。", "easy",
        "一个正整数。", "YES 或 NO。", "12321", "YES",
        [("12321", "YES", True), ("12345", "NO", False), ("1", "YES", False)]))
    out.append(("prime-check", "质数判断", "读入一个正整数 n，判断是否为质数。是输出 YES，否输出 NO。", "medium",
        "一个正整数 n。", "YES 或 NO。", "17", "YES",
        [("17", "YES", True), ("1", "NO", False), ("100", "NO", False),
         ("999983", "YES", False)]))
    out.append(("prime-factors", "质因数分解", "读入一个正整数 n，按升序输出其所有质因数（空格分隔，重复的也输出）。", "medium",
        "一个正整数 n。", "空格分隔的质因数。", "12", "2 2 3",
        [("12", "2 2 3", True), ("17", "17", False), ("100", "2 2 5 5", False)]))
    out.append(("gcd", "最大公约数", "读入两个正整数，输出它们的最大公约数。", "medium",
        "一行两个正整数。", "最大公约数。", "12 18", "6",
        [("12 18", "6", True), ("7 13", "1", False), ("48 64", "16", False)]))
    out.append(("lcm", "最小公倍数", "读入两个正整数，输出它们的最小公倍数。", "medium",
        "一行两个正整数。", "最小公倍数。", "12 18", "36",
        [("12 18", "36", True), ("7 13", "91", False), ("48 64", "192", False)]))
    out.append(("armstrong-number", "水仙花数", "读入一个三位整数，判断是否为水仙花数（各位数字立方和等于自身）。是输出 YES，否输出 NO。", "easy",
        "一个三位整数。", "YES 或 NO。", "153", "YES",
        [("153", "YES", True), ("123", "NO", False), ("371", "YES", False)]))

    # ── 31-40: 字符串 ──
    out.append(("str-length", "字符串长度", "读入一行字符串，输出其长度。", "easy",
        "一行字符串。", "字符串长度。", "hello", "5",
        [("hello", "5", True), ("你好世界", "4", False), ("", "0", False)]))
    out.append(("str-reverse", "反转字符串", "读入一行字符串，输出反转后的字符串。", "easy",
        "一行字符串。", "反转后的字符串。", "abcd", "dcba",
        [("abcd", "dcba", True), ("12345", "54321", False)]))
    out.append(("to-uppercase", "转大写", "读入一行字符串，将其中的小写字母转为大写后输出。", "easy",
        "一行字符串。", "转换后的字符串。", "hello", "HELLO",
        [("hello", "HELLO", True), ("Hello World", "HELLO WORLD", False)]))
    out.append(("to-lowercase", "转小写", "读入一行字符串，将其中的大写字母转为小写后输出。", "easy",
        "一行字符串。", "转换后的字符串。", "HELLO", "hello",
        [("HELLO", "hello", True), ("Hello World", "hello world", False)]))
    out.append(("count-char", "统计字符", "读入一行字符串和一个字符，统计该字符在字符串中出现的次数。", "easy",
        "第一行字符串，第二行一个字符。", "出现次数。", "hello world\nl", "3",
        [("hello world\nl", "3", True), ("aaaa\na", "4", False)]))
    out.append(("is-substring", "子串判断", "读入字符串 S 和 T，判断 T 是否为 S 的子串。是输出 YES，否输出 NO。", "medium",
        "第一行 S，第二行 T。", "YES 或 NO。", "abcdef\ncde", "YES",
        [("abcdef\ncde", "YES", True), ("hello\nworld", "NO", False)]))
    out.append(("remove-spaces", "去除空格", "读入一行字符串，输出去除所有空格后的结果。", "easy",
        "一行字符串。", "去除空格后的字符串。", "a b c", "abc",
        [("a b c", "abc", True), ("hello world", "helloworld", False)]))
    out.append(("word-count", "单词统计", "读入一行字符串（仅由字母和空格组成），统计单词数量。", "easy",
        "一行字符串。", "单词数量。", "hello world from python", "4",
        [("hello world from python", "4", True), ("  a  b  ", "2", False)]))
    out.append(("most-frequent-char", "出现最多的字符", "读入一行字符串，输出出现次数最多的字符（如有多个输出最小的ASCII）。", "medium",
        "一行字符串。", "出现最多的字符。", "abacabad", "a",
        [("abacabad", "a", True), ("zzxy", "z", False)]))
    out.append(("is-anagram", "变位词判断", "读入两个字符串，判断它们是否互为变位词（相同字母不同排列）。是输出 YES，否输出 NO。", "medium",
        "第一行 S，第二行 T。", "YES 或 NO。", "listen\nsilent", "YES",
        [("listen\nsilent", "YES", True), ("hello\nworld", "NO", False),
         ("abc\ncab", "YES", False)]))

    # ── 41-50: 数组/列表 ──
    out.append(("array-sum", "数组求和", "读入 n 和 n 个整数，输出它们的和。", "easy",
        "第一行 n，第二行 n 个整数。", "和。", "5\n1 2 3 4 5", "15",
        [("5\n1 2 3 4 5", "15", True), ("3\n10 20 30", "60", False)]))
    out.append(("array-max", "数组最大值", "读入 n 和 n 个整数，输出最大值。", "easy",
        "第一行 n，第二行 n 个整数。", "最大值。", "5\n3 7 2 9 1", "9",
        [("5\n3 7 2 9 1", "9", True), ("3\n5 5 5", "5", False)]))
    out.append(("array-second-max", "数组第二大值", "读入 n 和 n 个整数，输出第二大的值。保证 n >= 2 且存在不同值。", "medium",
        "第一行 n，第二行 n 个整数。", "第二大的值。", "5\n3 7 2 9 1", "7",
        [("5\n3 7 2 9 1", "7", True), ("4\n10 20 30 40", "30", False)]))
    out.append(("remove-duplicates", "去重", "读入 n 和 n 个整数，输出去重后排序的结果，空格分隔。", "medium",
        "第一行 n，第二行 n 个整数。", "去重排序后的整数。", "6\n3 1 4 1 5 9", "1 3 4 5 9",
        [("6\n3 1 4 1 5 9", "1 3 4 5 9", True),
         ("5\n2 2 2 2 2", "2", False)]))
    out.append(("majority-element", "多数元素", "读入 n 和 n 个整数，输出出现次数 > n/2 的元素。保证存在。", "medium",
        "第一行 n，第二行 n 个整数。", "多数元素。", "5\n2 2 3 2 2", "2",
        [("5\n2 2 3 2 2", "2", True), ("3\n1 1 2", "1", False)]))
    out.append(("missing-number", "缺失的数字", "读入 n 以及 0 到 n 中缺失一个的 n 个整数（乱序），输出缺失的数字。", "medium",
        "第一行 n，第二行 n 个 0..n 中缺失一个的整数。", "缺失的数字。", "3\n3 0 1", "2",
        [("3\n3 0 1", "2", True), ("5\n5 2 3 1 4", "0", False)]))
    out.append(("two-sum", "两数之和", "读入 n、target 和 n 个整数，输出两个不同下标 i j（空格分隔），使 A[i]+A[j]=target。保证有解，输出任意一组。", "medium",
        "第一行 n target，第二行 n 个整数。", "两个空格分隔的下标。", "4 9\n2 7 11 15", "0 1",
        [("4 9\n2 7 11 15", "0 1", True), ("3 6\n3 2 3", "0 2", False)]))
    out.append(("move-zeroes", "移动零", "读入 n 和 n 个整数，将所有零移到末尾，保持非零元素相对顺序，输出结果。", "medium",
        "第一行 n，第二行 n 个整数。", "移动后的数组。", "5\n0 1 0 3 12", "1 3 12 0 0",
        [("5\n0 1 0 3 12", "1 3 12 0 0", True),
         ("4\n1 2 3 4", "1 2 3 4", False)]))
    out.append(("max-subarray-sum", "最大子数组和", "读入 n 和 n 个整数，输出连续子数组的最大和。", "hard",
        "第一行 n，第二行 n 个整数。", "最大子数组和。", "9\n-2 1 -3 4 -1 2 1 -5 4", "6",
        [("9\n-2 1 -3 4 -1 2 1 -5 4", "6", True),
         ("3\n-1 -2 -3", "-1", False)]))
    out.append(("product-except-self", "除自身外的乘积", "读入 n 和 n 个整数，输出每个位置除自身外所有元素的乘积（空格分隔）。", "hard",
        "第一行 n，第二行 n 个整数。", "空格分隔的乘积。", "4\n1 2 3 4", "24 12 8 6",
        [("4\n1 2 3 4", "24 12 8 6", True),
         ("3\n2 3 4", "12 8 6", False)]))

    # ── 51-60: 排序与搜索 ──
    out.append(("bubble-sort", "冒泡排序", "读入 n 和 n 个整数，用冒泡排序从小到大排序后输出。", "easy",
        "第一行 n，第二行 n 个整数。", "排序后的数组。", "5\n5 3 1 4 2", "1 2 3 4 5",
        [("5\n5 3 1 4 2", "1 2 3 4 5", True),
         ("6\n6 5 4 3 2 1", "1 2 3 4 5 6", False)]))
    out.append(("binary-search", "二分查找", "读入升序数组长度 n、target 和 n 个升序整数，输出 target 的下标。找不到输出 -1。", "medium",
        "第一行 n target，第二行 n 个升序整数。", "下标或 -1。", "5 4\n1 2 3 4 5", "3",
        [("5 4\n1 2 3 4 5", "3", True),
         ("5 6\n1 2 3 4 5", "-1", False)]))
    out.append(("kth-largest", "第K大的数", "读入 n、k 和 n 个整数，输出第 k 大的数。", "medium",
        "第一行 n k，第二行 n 个整数。", "第 k 大的数。", "6 2\n3 2 1 5 6 4", "5",
        [("6 2\n3 2 1 5 6 4", "5", True),
         ("4 1\n3 2 3 1", "3", False)]))
    out.append(("merge-sorted-arrays", "合并有序数组", "读入两个升序数组（各一行，格式 n arr），输出合并后的升序数组。", "medium",
        "第一行 n1 和 n1 个升序整数，第二行 n2 和 n2 个升序整数。", "合并后的升序数组。", "3 1 3 5\n3 2 4 6", "1 2 3 4 5 6",
        [("3 1 3 5\n3 2 4 6", "1 2 3 4 5 6", True),
         ("2 1 4\n2 2 3", "1 2 3 4", False)]))
    out.append(("find-peak", "寻找峰值", "读入 n 和 n 个互不相同整数，输出任意一个峰值（大于其左右邻居）的下标。", "medium",
        "第一行 n，第二行 n 个整数（互不相同）。", "峰值下标。", "4\n1 2 3 1", "2",
        [("4\n1 2 3 1", "2", True),
         ("5\n1 5 3 2 1", "1", False)]))
    out.append(("search-rotated", "旋转数组搜索", "读入 n、target 和 n 个旋转过的升序数组，输出 target 下标。找不到输出 -1。", "hard",
        "第一行 n target，第二行 n 个整数。", "下标或 -1。", "6 0\n4 5 6 7 0 1 2", "4",
        [("7 0\n4 5 6 7 0 1 2", "4", True),
         ("7 3\n4 5 6 7 0 1 2", "-1", False)]))
    out.append(("frequency-sort", "按频率排序", "读入 n 和 n 个整数，按出现频率降序输出，同频率按值升序。", "medium",
        "第一行 n，第二行 n 个整数。", "排序后的数组。", "7\n4 5 6 5 4 5 4", "4 4 4 5 5 5 6",
        [("7\n4 5 6 5 4 5 4", "4 4 4 5 5 5 6", True),
         ("3\n1 2 3", "1 2 3", False)]))
    out.append(("first-bad-version", "第一个错误版本", "读入 n，从版本 1 到 n 中查找第一个错误版本（模拟：版本 >= k 为错误，k 在输入第二行给出作为真相，但代码应通过 is_bad 函数判断）。为简化，直接读 n k，输出 k。", "medium",
        "一行两个整数 n k。", "第一个错误版本号。", "10 4", "4",
        [("10 4", "4", True), ("5 1", "1", False)]))
    out.append(("median-two-sorted", "两有序数组中位数", "读入两个升序数组（格式同合并有序数组），输出它们合并后的中位数。", "hard",
        "两行，每行 n 和 n 个升序整数。", "中位数。", "3 1 3 8\n3 7 9 10", "7.0",
        [("3 1 3 8\n3 7 9 10", "7.0", True),
         ("2 1 2\n2 3 4", "2.5", False)]))
    out.append(("custom-sort", "自定义排序", "读入 n 和 n 个整数，偶数在前奇数在后，各组内升序排列。", "medium",
        "第一行 n，第二行 n 个整数。", "排序后的数组。", "6\n5 2 8 1 4 7", "2 4 8 1 5 7",
        [("6\n5 2 8 1 4 7", "2 4 8 1 5 7", True),
         ("4\n3 1 2 4", "2 4 1 3", False)]))

    # ── 61-70: 递归与分治 ──
    out.append(("fibonacci", "斐波那契数列", "读入 n，输出第 n 个斐波那契数（F(0)=0, F(1)=1）。", "medium",
        "一个非负整数 n。", "第 n 个斐波那契数。", "10", "55",
        [("10", "55", True), ("0", "0", False), ("20", "6765", False)]))
    out.append(("tower-of-hanoi", "汉诺塔步数", "读入盘子数 n，输出最少移动步数。", "easy",
        "一个正整数 n。", "最少步数。", "3", "7",
        [("3", "7", True), ("1", "1", False), ("4", "15", False)]))
    out.append(("power-recursive", "快速幂", "读入底数 a 和指数 b，输出 a^b mod 1000000007。", "medium",
        "一行两个整数 a b。", "a^b mod 1000000007。", "2 10", "1024",
        [("2 10", "1024", True), ("3 5", "243", False),
         ("123456 0", "1", False)]))
    out.append(("euclidean-gcd-recursive", "辗转相除法", "用递归实现欧几里得算法，读入两个正整数，输出最大公约数。", "medium",
        "一行两个正整数。", "最大公约数。", "48 18", "6",
        [("48 18", "6", True), ("100 75", "25", False)]))
    out.append(("climbing-stairs", "爬楼梯", "你站在第 0 级，每次可以走 1 级或 2 级。读入 n，输出到达第 n 级的不同走法数。", "medium",
        "一个非负整数 n。", "走法总数。", "5", "8",
        [("5", "8", True), ("1", "1", False), ("10", "89", False)]))
    out.append(("permutations", "全排列", "读入 n，输出 1..n 的所有全排列，每行一个（空格分隔），按字典序。", "hard",
        "一个正整数 n (<= 7)。", "每行一个排列。", "3", "1 2 3\n1 3 2\n2 1 3\n2 3 1\n3 1 2\n3 2 1",
        [("3", "1 2 3\n1 3 2\n2 1 3\n2 3 1\n3 1 2\n3 2 1", True)]))
    out.append(("subset-sum", "子集求和", "读入 n、target 和 n 个正整数，判断是否存在子集和等于 target。输出 YES 或 NO。", "hard",
        "第一行 n target，第二行 n 个正整数。", "YES 或 NO。", "4 9\n3 4 5 2", "YES",
        [("4 9\n3 4 5 2", "YES", True),
         ("3 10\n1 2 3", "NO", False)]))
    out.append(("coin-change", "零钱兑换", "读入 amount 和 n 种硬币面值，输出凑成 amount 的最少硬币数（每种硬币无限）。无法凑出输出 -1。", "hard",
        "第一行 amount n，第二行 n 个硬币面值。", "最少硬币数。", "11 3\n1 5 6", "2",
        [("11 3\n1 5 6", "2", True),
         ("3 2\n2 4", "-1", False)]))
    out.append(("knapsack-01", "01背包", "读入物品数 n 和 capacity，以及每件物品的重量和价值，输出最大总价值。", "hard",
        "第一行 n capacity，接下来 n 行每行 weight value。", "最大总价值。", "3 50\n10 60\n20 100\n30 120", "220",
        [("3 50\n10 60\n20 100\n30 120", "220", True),
         ("2 5\n3 4\n4 5", "5", False)]))
    out.append(("longest-common-subseq", "最长公共子序列", "读入两个字符串 S 和 T，输出最长公共子序列的长度。", "hard",
        "第一行 S，第二行 T。", "LCS 长度。", "abcde\nace", "3",
        [("abcde\nace", "3", True),
         ("abc\nabc", "3", False)]))
    out.append(("edit-distance", "编辑距离", "读入两个字符串 S 和 T，输出将 S 转为 T 的最少操作次数（增删改）。", "hard",
        "第一行 S，第二行 T。", "最少操作次数。", "horse\nros", "3",
        [("horse\nros", "3", True),
         ("intention\nexecution", "5", False)]))

    # ── 81-90: 数据结构模拟 ──
    out.append(("valid-parentheses", "有效括号", "读入一个括号字符串，判断是否有效（括号匹配正确）。输出 YES 或 NO。", "medium",
        "一行括号字符串（仅含 ()[]{}）。", "YES 或 NO。", "()[]{}", "YES",
        [("()[]{}", "YES", True), ("([)]", "NO", False),
         ("({[]})", "YES", False)]))
    out.append(("queue-simulation", "模拟队列", "读入操作序列，每行 PUSH x 或 POP。对 POP 操作输出被弹出的值。", "medium",
        "多行，第一行 n 表示操作数，接下来 n 行操作。", "每次 POP 时输出值。", "5\nPUSH 1\nPUSH 2\nPOP\nPUSH 3\nPOP", "1\n2",
        [("5\nPUSH 1\nPUSH 2\nPOP\nPUSH 3\nPOP", "1\n2", True),
         ("3\nPUSH 5\nPUSH 6\nPOP", "5", False)]))
    out.append(("stack-simulation", "模拟栈", "读入操作序列，每行 PUSH x 或 POP。对 POP 操作输出被弹出的值。", "medium",
        "多行，第一行 n 表示操作数，接下来 n 行操作。", "每次 POP 时输出值。", "5\nPUSH 1\nPUSH 2\nPOP\nPUSH 3\nPOP", "2\n3",
        [("5\nPUSH 1\nPUSH 2\nPOP\nPUSH 3\nPOP", "2\n3", True),
         ("3\nPUSH 5\nPOP\nPOP", "5", False)]))
    out.append(("min-stack", "最小栈", "模拟一个能 O(1) 返回最小值的栈。操作：PUSH x / POP / GETMIN。对 POP 输出值，GETMIN 输出当前最小值。", "hard",
        "第一行 n，接下来 n 行操作。", "POP 和 GETMIN 的结果。", "6\nPUSH 3\nPUSH 5\nGETMIN\nPUSH 2\nGETMIN\nPOP", "3\n2\n2",
        [("6\nPUSH 3\nPUSH 5\nGETMIN\nPUSH 2\nGETMIN\nPOP", "3\n2\n2", True)]))
    out.append(("lru-cache", "LRU缓存", "模拟 LRU 缓存。操作：PUT key value / GET key。容量固定为 capacity。GET 返回 value 或 -1。", "hard",
        "第一行 n capacity，接下来 n 行操作。", "每次 GET 的结果。", "8 2\nPUT 1 10\nPUT 2 20\nGET 1\nPUT 3 30\nGET 2\nGET 3\nPUT 4 40\nGET 1", "10\n-1\n30\n-1",
        [("8 2\nPUT 1 10\nPUT 2 20\nGET 1\nPUT 3 30\nGET 2\nGET 3\nPUT 4 40\nGET 1", "10\n-1\n30\n-1", True)]))
    out.append(("linked-list-cycle", "环形链表检测", "读入 n 及 n 个节点的指向关系，判断链表是否有环。输出 YES 或 NO。输入：每行 node_id next_id（next_id=-1 表示尾节点）。", "medium",
        "第一行 n，接下来 n 行 node_id next_id。", "YES 或 NO。", "4\n0 1\n1 2\n2 3\n3 1", "YES",
        [("4\n0 1\n1 2\n2 3\n3 1", "YES", True),
         ("3\n0 1\n1 2\n2 -1", "NO", False)]))
    out.append(("stack-to-queue", "栈实现队列", "用两个栈实现队列。操作：ENQ x / DEQ。读入 n 和 n 个操作，对 DEQ 输出。", "hard",
        "第一行 n，接下来 n 行操作。", "DEQ 的结果。", "6\nENQ 1\nENQ 2\nDEQ\nENQ 3\nDEQ\nDEQ", "1\n2\n3",
        [("6\nENQ 1\nENQ 2\nDEQ\nENQ 3\nDEQ\nDEQ", "1\n2\n3", True)]))
    out.append(("postfix-eval", "后缀表达式求值", "读入一个后缀表达式（操作数和运算符空格分隔），求值输出结果。运算符：+ - * /。", "medium",
        "一行后缀表达式。", "计算结果。", "3 4 + 5 *", "35",
        [("3 4 + 5 *", "35", True), ("6 2 / 3 4 * +", "15.0", False)]))
    out.append(("top-k-frequent", "Top K 高频词", "读入 n、k 和 n 个单词，输出出现频率最高的 k 个单词，按频率降序、同频按字典序。", "medium",
        "第一行 n k，接下来 n 行每行一个单词。", "k 个单词每行一个。", "5 2\napple\nbanana\napple\napple\nbanana", "apple\nbanana",
        [("5 2\napple\nbanana\napple\napple\nbanana", "apple\nbanana", True),
         ("4 1\nx\ny\nx\nz", "x", False)]))
    out.append(("hash-table-sim", "模拟哈希表", "模拟一个简单哈希表（冲突用开放寻址）。操作：INSERT key / FIND key / DELETE key。FIND 输出 FOUND 或 NOTFOUND。", "hard",
        "第一行 n size，接下来 n 行操作。", "FIND 的结果。", "7 10\nINSERT 5\nINSERT 15\nFIND 5\nFIND 10\nDELETE 5\nFIND 5\nFIND 15", "FOUND\nNOTFOUND\nNOTFOUND\nFOUND",
        [("7 10\nINSERT 5\nINSERT 15\nFIND 5\nFIND 10\nDELETE 5\nFIND 5\nFIND 15", "FOUND\nNOTFOUND\nNOTFOUND\nFOUND", True)]))

    # ── 91-100: 综合题 ──
    out.append(("fizzbuzz", "FizzBuzz", "输出 1 到 n 的整数，但 3 的倍数替换为 Fizz，5 的倍数替换为 Buzz，同时是 3 和 5 的倍数替换为 FizzBuzz。", "easy",
        "一个正整数 n。", "每行一个结果。", "15", "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz",
        [("15", "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz", True)]))
    out.append(("caesar-cipher", "凯撒密码", "读入整数偏移量 k 和一个全大写字符串，输出加密后的字符串（每个字母后移 k 位，Z 后面绕回 A）。", "medium",
        "第一行 k，第二行全大写字符串。", "加密后的字符串。", "3\nHELLO", "KHOOR",
        [("3\nHELLO", "KHOOR", True), ("1\nXYZ", "YZA", False)]))
    out.append(("roman-to-int", "罗马数字转整数", "读入一个罗马数字字符串，输出对应的整数值。", "medium",
        "一行罗马数字(I,V,X,L,C,D,M)。", "整数值。", "MCMXCIV", "1994",
        [("MCMXCIV", "1994", True), ("LVIII", "58", False),
         ("III", "3", False)]))
    out.append(("int-to-roman", "整数转罗马数字", "读入整数(1-3999)，输出对应的罗马数字。", "medium",
        "一个整数。", "罗马数字。", "1994", "MCMXCIV",
        [("1994", "MCMXCIV", True), ("58", "LVIII", False)]))
    out.append(("pascal-triangle", "杨辉三角", "读入 n，输出杨辉三角的前 n 行（每行空格分隔）。", "medium",
        "一个正整数 n。", "每行一个数组。", "5", "1\n1 1\n1 2 1\n1 3 3 1\n1 4 6 4 1",
        [("5", "1\n1 1\n1 2 1\n1 3 3 1\n1 4 6 4 1", True),
         ("1", "1", False)]))
    out.append(("happy-number", "快乐数", "读入一个正整数，判断是否为快乐数（不断用各位数字平方和替换，最终是否变为 1）。输出 YES 或 NO。", "medium",
        "一个正整数。", "YES 或 NO。", "19", "YES",
        [("19", "YES", True), ("2", "NO", False),
         ("7", "YES", False)]))
    out.append(("josephus", "约瑟夫环", "n 个人围成一圈，从 1 开始报数，报到 k 的人出局。输出最后剩下的人的编号。", "hard",
        "一行两个整数 n k。", "最后剩下的编号。", "5 2", "3",
        [("5 2", "3", True), ("7 3", "4", False),
         ("10 3", "4", False)]))
    out.append(("sudoku-validator", "数独验证", "读入 9x9 数独（每行 9 个数字，空格分隔），判断是否有效（每行每列每 3x3 格 1-9 各出现一次）。输出 YES 或 NO。", "hard",
        "9 行，每行 9 个数字。", "YES 或 NO。", "5 3 4 6 7 8 9 1 2\n6 7 2 1 9 5 3 4 8\n1 9 8 3 4 2 5 6 7\n8 5 9 7 6 1 4 2 3\n4 2 6 8 5 3 7 9 1\n7 1 3 9 2 4 8 5 6\n9 6 1 5 3 7 2 8 4\n2 8 7 4 1 9 6 3 5\n3 4 5 2 8 6 1 7 9", "YES",
        [("5 3 4 6 7 8 9 1 2\n6 7 2 1 9 5 3 4 8\n1 9 8 3 4 2 5 6 7\n8 5 9 7 6 1 4 2 3\n4 2 6 8 5 3 7 9 1\n7 1 3 9 2 4 8 5 6\n9 6 1 5 3 7 2 8 4\n2 8 7 4 1 9 6 3 5\n3 4 5 2 8 6 1 7 9", "YES", True)]))
    out.append(("spiral-matrix", "螺旋矩阵", "读入 n，输出 n×n 的螺旋矩阵（从 1 开始，顺时针螺旋填充）。每行空格分隔。", "hard",
        "一个正整数 n。", "n 行每行 n 个数字。", "3", "1 2 3\n8 9 4\n7 6 5",
        [("3", "1 2 3\n8 9 4\n7 6 5", True),
         ("2", "1 2\n4 3", False)]))
    out.append(("n-queens-count", "N皇后计数", "读入 n，输出 n×n 棋盘上 n 皇后问题的解法数量。", "hard",
        "一个整数 n (1 <= n <= 12)。", "解法数量。", "4", "2",
        [("4", "2", True), ("1", "1", False), ("8", "92", False)]))

    return out


def main():
    token = login()
    if not token:
        print("FATAL: Cannot login")
        return

    problems = build_problems()
    print(f"Seeding {len(problems)} problems...\n")

    created = 0
    for slug, title, desc, diff, in_desc, out_desc, sin, sout, cases in problems:
        p = {
            "title": title, "slug": slug, "description": desc,
            "difficulty": diff,
            "input_description": in_desc,
            "output_description": out_desc,
            "sample_input": sin, "sample_output": sout,
            "is_public": True,
        }
        result = create_problem(token, p)
        if result:
            for idx, (tc_in, tc_out, is_sample) in enumerate(cases):
                add_test_case(token, slug, {
                    "input": tc_in, "expected_output": tc_out,
                    "is_sample": is_sample, "order": idx,
                })
            created += 1
            print(f"  [{created:3d}] {slug} ({diff})")
        else:
            print(f"  [FAIL] {slug}")
        time.sleep(0.05)

    print(f"\nDone. Created/verified {created} problems.")


if __name__ == "__main__":
    main()
