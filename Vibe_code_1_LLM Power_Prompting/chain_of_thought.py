import os
import re
from dotenv import load_dotenv
from ollama import chat

load_dotenv()

NUM_RUNS_TIMES = 5

# 简化后的系统提示词：简短描述 + 清晰示例（匹配字符串翻转的格式）
SYSTEM_PROMPT = """
计算 (底数^指数) mod 模数 的结果，必须按照以下规则输出：
1. 解题要求：先通过模运算循环规律简化计算，再得出最终结果；
2. 输出要求：最后一行仅输出「Answer: 结果数字」，无任何额外内容。

例如：
（1）输入：3^5 mod 100 → 输出：Answer: 43
（2）输入：3^20 mod 100 → 输出：Answer: 1
（3）输入：2^10 mod 100 → 输出：Answer: 24
"""

# python计算
def modular_exponentiation(base: int, exponent: int, mod: int) -> int:
    if mod == 1:
        return 0
    result = 1
    base = base % mod  # 先取模，缩小底数范围
    while exponent > 0:
        # 如果指数是奇数，结果先乘底数再取模
        if exponent % 2 == 1:
            result = (result * base) % mod
        # 指数折半，底数平方后取模
        exponent = exponent >> 1  # 等价于 exponent = exponent // 2
        base = (base * base) % mod
    return result


def get_user_input() -> tuple[int, int, int]:
    # 输入
    while True:
        user_input = input("请输入模运算参数（格式：底数/指数/模数，例如 3/1/4）：").strip()
        # 分割输入并校验格式
        parts = user_input.split("/")
        if len(parts) != 3:
            print("输入格式错误！必须是 底数/指数/模数 的形式，例如 3/1/4")
            continue
        # 尝试转换为整数
        try:
            base = int(parts[0])
            exponent = int(parts[1])
            mod = int(parts[2])
            # 校验模数合法性
            if mod <= 0:
                print("模数必须是正整数！")
                continue
            # 校验指数非负
            if exponent < 0:
                print("指数暂不支持负数，请输入非负整数！")
                continue
            return base, exponent, mod
        except ValueError:
            print("所有参数必须是整数！请重新输入")


def extract_final_answer(text: str) -> str:
    # 提取最后一行的Answer并标准化格式
    matches = re.findall(r"(?mi)^\s*answer\s*:\s*(.+)\s*$", text)
    if matches:
        value = matches[-1].strip()
        # 提取数字部分，标准化输出格式
        num_match = re.search(r"-?\d+(?:\.\d+)?", value.replace(",", ""))
        if num_match:
            return f"Answer: {num_match.group(0)}"
        return f"Answer: {value}"
    return text.strip()


def test_prompt(base: int, exponent: int, mod: int) -> bool:
    # 运行多次测试，对比大模型输出和程序计算的预期结果

    # 程序自动计算正确结果
    correct_result = modular_exponentiation(base, exponent, mod)
    expected_output = f"Answer: {correct_result}"

    # 构造动态用户提示词
    user_prompt = f"""
Solve this problem, then give the final answer on the last line as "Answer: <number>".

what is {base}^{exponent} (mod {mod})?
    """

    print(f"\n开始测试，模运算表达式：{base}^{exponent} mod {mod}")
    print(f"预期正确输出：{expected_output}\n")

    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        try:
            response = chat(
                model="llama3.1:8b",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                options={"temperature": 0.3},
            )
            # 提取模型输出并解析最终答案
            raw_output = response.message.content
            final_answer = extract_final_answer(raw_output)

            # 对比结果
            if final_answer.strip() == expected_output.strip():
                print("SUCCESS")
                return True
            else:
                print(f"Expected output: {expected_output}")
                print(f"Actual output: {final_answer}")
                # 可选：打印模型原始输出，方便排查问题
                # print(f"Raw model output:\n{raw_output}\n")
        except Exception as e:
            print(f"测试 {idx + 1} 出错：{str(e)}")

    print("\n所有测试轮次均未匹配到正确结果！")
    return False


if __name__ == "__main__":
    # 输入
    base, exponent, mod = get_user_input()
    # 测试
    test_prompt(base, exponent, mod)