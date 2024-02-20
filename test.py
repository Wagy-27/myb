import re

input_string = "apple orange apple banana apple"
pattern = r'\bapple\b'

# 使用 re.finditer 找到所有匹配的位置
matches_iter = re.finditer(pattern, input_string)
list_abc = []
list_abc.append('aafljlejwllfj')
list_abc.append('b ')
list_abc.append('c ')
# 遍历匹配对象迭代器，逐个处理每个匹配
modified_string = input_string
for match in matches_iter:
    # 获取匹配的子字符串
    match_string = match.group()

    # 在这里可以对每个匹配的子字符串进行修改
    # 这里简单地将每个匹配的 "apple" 替换为 "X"
    replacement = list_abc.pop(0)
    modified_string = modified_string[:match.start()] + replacement + modified_string[match.end():]

print(modified_string)
