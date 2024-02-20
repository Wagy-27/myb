"""
弃用
"""

import sqlparse
import re
import string
import random
import Extend_mod



Check_methon = {
    "COUNT":10.0,
    "SUM":10.0,
    "AVG":10.0,
    "MAX":10.0,
    "MIN":10.0,
    "STD":10.0,
    "VAR":10.0,
    "FIRST":10.0,
    "LAST":10.0,
    "CONCAT":10.0,
    "COUNT_DISTINCT":10.0,
    "COUNT_DISTINCT_APPROX":10.0
}


def Check_From_methon(token):
# 能进来的都是非空tokens
    for t in token.tokens:
        pattern = re.compile(r'([^()\s]+)',re.IGNORECASE | re.DOTALL)  # 判定是否存在别名
        if pattern.match(t.value):
            return False
    return True
def generate_random_string(length):
    # 生成包含大小写字母和数字的字符集
    characters = string.ascii_letters + string.digits
    # 从字符集中随机选择指定长度的字符，并拼接成字符串
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string



def digui(input_string,select_str = ""):
    '''
    如下函数仅能对单个SQL语句进行。
    仅能处理FROM中子查询为一条的SQL语句，多了判断不了
    HIVE中GROUP BY 中的内容要和SELECT中一一对应，且不能使用别名
    :param input_string:
    :return:
    '''
    Alias = generate_random_string(3) # 随机别名
    from_pattern = re.compile(r'\s+FROM\s*\((.*)\)', re.IGNORECASE | re.DOTALL)  # 找到子查询前的FROM
    temp_input_Child = ""
    # 对初始语句进行sqlparse分析，递归找到各个子查询，直到不可分
    parsed = sqlparse.parse(input_string)
    token_select = False
    into_list = False
    if from_pattern.search(input_string):
        # 修改子查询的SELECT GROUP
        temp_input_Child = digui(from_pattern.search(input_string).group(1))  # 子查询的切片
        input_string = re.sub(r'(FROM\s*\().*(\))',fr'\1 \2',input_string) # 保证每一次只需要面对一对SELECT ... GROUP
    # input_string = re.sub(from_pattern,r'\1',input_string)
    # 清理sql语句
    # input_string = sqlparse.format(input_string, reindexed=True, keyword_case='upper', strip_comments=True)
    # input_string = input_string.replace('\xa0', ' ').replace('\n', ' ')

    # print(input_string)

    parsed = sqlparse.parse(input_string)
    select_str = ""
    check_select = False
    check_from = False  # 检查子查询是否有别名
    No_alias = True  # 输入端是否补别名的判断依据
    for token in parsed[0].tokens:
        if token.ttype == sqlparse.tokens.Keyword.DML and token.value == 'SELECT':
            check_select = True
        elif token.ttype == sqlparse.tokens.Keyword and token.value == 'FROM':
            check_from = True
        # 检查是否子查询有别名
        elif check_from and token.is_group and temp_input_Child != "":
            check_from = False  # # 保证后续子查询不会触发
            No_alias = Check_From_methon(token)
        # 假定第一个找到的Identifier就是SELECT的内容
        # 存在问题！
        elif check_select and token.is_group:
            check_select = False # 保证后续子查询不会触发
            temp = token.value
            # 去除SELECT中的别名  额外加了个避免DISTINCT A.INDEX_NO问题，特化构筑————’)VALUE2‘
            # select_str = re.sub(r'(?<!,)(?<!\.)\s+\w+(?!\.)|(?<=\))\w+', r'', select_str)
            temp_list = temp.split(',')
            for index,i in enumerate(temp_list):
                pattern = re.compile(r'\b\w+\(',re.IGNORECASE | re.DOTALL)
                if pattern.search(temp_list[index]):
                    strtemp = i
                    temp_list[index] = re.sub(r'(?<=\))\s+\w+',r'',strtemp)
                else:
                    strtemp = i
                    temp_list[index] = re.sub(r'\s+\w+\b',r'',strtemp)
            select_str = ','.join(temp_list)
            # 去除SELECT中的聚合函数
            check = re.compile(r'(?:,)\s*(\w+)\(+', re.IGNORECASE | re.DOTALL)  # 获取所有函数名
            check_result = re.findall(check, select_str)
            for j in check_result:
                if Check_methon.get(j):
                    # 假设聚合函数不会出现在排头
                    select_str = re.sub(fr',\s*{j}\s*\(.*?\)', r'', select_str)
        else:
            continue
    group_pattern = re.compile(r'(GROUP\s+BY\s+).+?((?:\s(ORDER\s+BY\s+(.+?))|(?:\s+HAVING\s+(.+?)))?(?:\s|$))',re.IGNORECASE | re.DOTALL)
    a = re.findall(group_pattern,input_string)
    if group_pattern.match:
        input_string = re.sub(group_pattern, fr'\1{select_str}\2', input_string)  # 修改GROUP BY
    if No_alias:  # False 有别名；True 没有别名
        input_string = re.sub(r'(\s+FROM\s*\().*?\)(.*)', fr'\1{temp_input_Child}) AS {Alias}\2', input_string)  # 将上一轮修改的子查询放回去
    else:
        input_string = re.sub(r'(\s+FROM\s*\().*?\)(.*)', fr'\1{temp_input_Child}) \2',
                              input_string)  # 将上一轮修改的子查询放回去
    # zzo = zzo + 1  # 子查询递归列别名
    return [input_string,select_str]

excel = '''
--分子xcdp0010    IS_LUNG_EXAM 15938
SELECT A.HOSPITAL_CODE,DEPT_CODE,A.DATA_TYPE class1, NULL CLASS2, TO_CHAR(INDEX_TIME,'YYYY-MM') YEAR_MONTH,SUM(case when B.DATA_VALUE='1' then 1 else 0 end) value1
FROM WAREHOUSE.DW_M_VIEW A
INNER JOIN (
SELECT HOSPITAL_CODE,INDEX_NO,DATA_VALUE FROM WAREHOUSE.DW_M_BASE B
WHERE DATA_ID IN (15938)
)B ON A.HOSPITAL_CODE=B.HOSPITAL_CODE AND A.INDEX_NO=B.INDEX_NO
WHERE A.AGE>=12 AND RESPIRATORY8_MAIN='有'AND A.DATA_TYPE=1
--拼接
GROUP BY A.HOSPITAL_CODE,DEPT_CODE,TO_CHAR(A.INDEX_TIME,'YYYY-MM'),A.DATA_TYPE
'''
# new_input = digui(excel)
excel = re.sub(r'\bNULL\b', 'CAST(NULL AS STRING)', excel)
# new_input = digui(excel)
new_input = sqlparse.parse(excel)
print(new_input)

# parse_str = '''SELECT A.HOSPITAL_CODE,A.DEPT_CODE,A.DATA_TYPE CLASS1,A.AGE CLASS2, A.YEAR_MONTH,COUNT(DISTINCT A.INDEX_NO) VALUE1  FROM TABLE A GROUP BY A.HOSPITAL_CODE,A.DEPT_CODE,A.DATA_TYPE,A.AGE,A.YEAR_MONTH
# '''
