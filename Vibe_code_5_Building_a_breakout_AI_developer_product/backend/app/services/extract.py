import re
from typing import List


import re
from typing import List


def extract_action_items(text: str) -> list[str]:
    lines = [line.strip("- ") for line in text.splitlines() if line.strip()]
    return [line for line in lines if line.endswith("!") or line.lower().startswith("todo:")]


def extract_tags(text: str) -> List[str]:
    """
    Extract hashtags from text.
    
    Args:
        text: Input text containing hashtags
        
    Returns:
        List of unique tag names (without # symbol)
        
    Examples:
        extract_tags("学习 #Python #AI #Python") → ['Python', 'AI']
        extract_tags("没有标签") → []
        extract_tags(None) → []
    """
    # Handle None and empty string cases
    if not text:
        return []
    
    # Match hashtags: # followed by Chinese/English/numbers/underscores
    pattern = r'#([a-zA-Z0-9\u4e00-\u9fa5_]+)'
    matches = re.findall(pattern, text)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_tags = []
    for tag in matches:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)
    
    return unique_tags


def extract_tags(text: str) -> List[str]:
    """
    从文本中提取#标签
    
    Args:
        text: 输入文本
        
    Returns:
        去重后的标签列表（不包含#符号）
        
    Examples:
        >>> extract_tags("学习 #Python #AI #Python")
        ['Python', 'AI']
        >>> extract_tags("没有标签")
        []
        >>> extract_tags(None)
        []
    """
    # 处理边界情况
    if text is None or not isinstance(text, str):
        return []
    
    if not text.strip():
        return []
    
    # 使用正则表达式匹配标签：#后跟中英文、数字、下划线
    pattern = r'#([a-zA-Z0-9\u4e00-\u9fa5_]+)'
    matches = re.findall(pattern, text)
    
    # 去重并保持顺序
    seen = set()
    result = []
    for tag in matches:
        if tag not in seen:
            seen.add(tag)
            result.append(tag)
    
    return result
