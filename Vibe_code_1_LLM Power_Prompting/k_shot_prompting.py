import os
from dotenv import load_dotenv
from ollama import chat

load_dotenv()

NUM_RUNS_TIMES = 5

# TODO: Fill this in!
SYSTEM_PROMPT = """
把整个字符串从后向前翻转。
例如：
（1）输入：'abcde' → 输出：'edcba'
（2）输入：'12345' → 输出：'54321'
（3）输入：'hello!' → 输出：'!olleh'
"""


def reverse_string(s: str) -> str:
    # 实现字符串翻转，生成正确的预期输出
    return s[::-1]


def get_user_input() -> str:
    # 自由输入
    while True:
        user_input = input("请输入你要测试翻转的字符串：").strip()
        if user_input:
            return user_input
        print("输入不能为空，请重新输入！")


def test_prompt(test_string: str) -> bool:
    # 运行多次测试，对比大模型输出和预期结果

    # 使用python实现字符串翻转
    expected_output = reverse_string(test_string)
    # 构造用户提示词
    user_prompt = f"""
Reverse the order of letters in the following word. Only output the reversed word, no other text:

{test_string}
    """

    print(f"\n开始测试，待翻转字符串：{test_string}")
    print(f"预期正确输出：{expected_output}\n")

    for idx in range(NUM_RUNS_TIMES):
        print(f"Running test {idx + 1} of {NUM_RUNS_TIMES}")
        try:
            response = chat(
                model="qwen3:8b",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                options={"temperature": 0.5},
            )
            # 提取并清理大模型输出
            actual_output = response.message.content.strip()

            # 对比结果
            if actual_output == expected_output:
                print("SUCCESS")
                return True
            else:
                print(f"Expected output: {expected_output}")
                print(f"Actual output: {actual_output}")
        except Exception as e:
            print(f"测试 {idx + 1} 出错：{str(e)}")

    print("\n所有测试轮次均未匹配到正确结果！")
    return False


if __name__ == "__main__":
    # 输入
    test_str = get_user_input()
    # 测试
    test_prompt(test_str)