import re
import sqlparse
def re_tochar(input_string):
    # 定义正则表达式模式
    result = re.sub(r'TO_CHAR\(([^,]*?),\s*([^)]*?)\)',r'DATE_FORMAT(\1,\2)',input_string,re.IGNORECASE)
    #
    return result

def re_unpivot(input_string):
    """
    unpviot格式：
    unpivot(新列名 for 聚合列名 in (对应的列名1…列名n ))
    多列转行
    :param input_string:
    :return:
    """
    pattern = re.compile(r'\bUNPIVOT\s*\(.*?\)\)',re.IGNORECASE | re.DOTALL) # 全匹配
    temp_str = re.findall(pattern,input_string)[0]
    # 一般来说只会有一个结果""
    col1 = re.findall(r'\bUNPIVOT\((.*)for',temp_str,re.IGNORECASE | re.DOTALL)[0]
    col2 = re.findall(r'for\s*(.*)\sin',temp_str,re.IGNORECASE | re.DOTALL)[0]
    cols = re.findall(r'IN\((.*?)\)',temp_str,re.IGNORECASE | re.DOTALL)[0]  # 如果是中文别名可能还是换引号
    cols = is_Chinese(cols)
    cols_tmp = cols.split(',')
    cols = ""
    for i in cols_tmp:
        cols = cols + i + ',' + i + ','
    cols = cols[:-1] # 去除多余逗号
    result = 'LATERAL VIEW EXPLODE(MAP(' + cols +')) t AS ' + col1 + ' , ' + col2
    input_string = re.sub(pattern,result,input_string)

    return input_string
def re_nvl(input_string):
    # 定义正则表达式模式
    result = re.sub(r'NVL\(([^,]*?),\s*([^)]*?)\)', r'COALESCE(\1,\2)', input_string,re.IGNORECASE)
    #
    return result

def is_Chinese(input_string):
    # 判断是否为中文
    if re.search(r'[\u4e00-\u9fa5]',input_string,re.IGNORECASE):
        input_string = re.sub(r'\"|\'','`',input_string)
    return input_string
def decode_digui(input_string):
    """
    input_parse = sqlparse.parse(input_string)
    for stmt in input_parse:
        for token in stmt.tokens:
            if token.value.upper() == 'DECODE':
                for identifer in token.get_identifier():
                    print(identifer.value)"""
    input_string = sqlparse.format(input_string, reindent=True)
    # 必须要进过sqlparse.format才能正确获取数据。通过\n来限制decode位置
    if re.search(r'DECODE\s*(?=\()(.*)(?<=\)).*',input_string,re.IGNORECASE):
        result_first = re.finditer(r'DECODE\s*(?=\()(.*)(?<=\)).*',input_string,re.IGNORECASE)
        # 获取DECODE内容
        decode_result = next(result_first) #每次只改第一个
        decode_result_start = decode_result.start() # 开始位置
        decode_result_end = decode_result.end()  # 结束位置
        pattern = re.compile(r"DECODE\s*\((.*)\).*",re.IGNORECASE)
        # 获取别名 ？如果不存在怎么办  直接连带逗号一起获取
        pattern2 = re.compile(r"DECODE\s*(?=\().*(?<=\))(.*)",re.IGNORECASE)
        # 匹配
        result = re.findall(pattern, decode_result.group())
        result2 = re.findall(pattern2, decode_result.group())
        alias = is_Chinese(result2[0])
        split_temp = re.split(',(?![^()]*\))', result[0])
        # 获取case项
        result = 'CASE '
        condition = split_temp.pop(0)
        # 挨个获取对应的WHEN...THEN...
        while len(split_temp):
            if len(split_temp) == 1:
                result = result + ' ELSE ' + split_temp.pop(0)
            else:
                # 输入对应的键对
                result = result + ' WHEN ' + condition + ' = ' + split_temp.pop(0) + ' THEN ' + split_temp.pop(0)
        # 别名直接连带逗号一起获取
        if re.search(r'AS',result2[0]):
            result = result + ' END ' + alias
        else:
            result = result + ' END AS ' + alias
        input_string = input_string.replace(input_string[decode_result_start:decode_result_end], result)
        input_string = decode_digui(input_string)

    return input_string

def re_decode(input_string):
    """
    废弃，用新的decode_digui
    :param input_string:
    :return:
    """
    # input_string = input_string.replace('\n', ' ')
    # input_string = input_string.replace('\xa0', '')
    pattern_test = re.compile(r'DECODE\(.*?\).*?\w+,',re.IGNORECASE)
    result_test = re.findall(pattern_test, input_string)

    # 获取DECODE内容
    pattern = re.compile(r"DECODE\(([^)]+)\).*?\w+,",re.IGNORECASE)
    # 获取别名 ？如果不存在怎么办
    pattern2 = re.compile(r"DECODE\([^)]+\).*?(\w+),",re.IGNORECASE)
    # 匹配
    result = re.findall(pattern, result_test[0])

    result2 = re.findall(pattern2,result_test[0])

    split_temp = re.split(',(?![^()]*\))',result[0])
    # 获取case项
    result = 'CASE ' + split_temp.pop(0)
    # 挨个获取对应的WHEN...THEN...
    while len(split_temp):
        if len(split_temp) == 1:
            result = result + ' ELSE ' + split_temp.pop(0)
        else:
            # 输入对应的键对
            result = result + ' WHEN ' + split_temp.pop(0) + ' THEN ' + split_temp.pop(0)
    # 填写别名
    result = result + ' END AS ' + result2[0] + ','
    result = re.sub(r'DECODE\(.*?\).*?\w+,', result, input_string,re.IGNORECASE)
    return result

# 字典匹配
re_type_mapping = {
    "TO_CHAR": re_tochar,  # 提取内容修改格式，不需要区分
    "NVL": re_nvl,  # 提取内容修改格式，不需要区分
    "DECODE": decode_digui,  # 递归修改每一个针对的\
    "UNPIVOT": re_unpivot  # 递归修改每一个针对的\
}


def count_sql_commands(input_string):
    # 使用正则表达式匹配 SQL 指令
    sql_commands = re.findall(r"\b\w+\(", input_string)
    return sql_commands

"""

sql = '''
--分母SJGKDP024
SELECT HOSPITAL_CODE, DEPT_CODE, CLASS1, YEAR_MONTH,SUM(VALUE1) VALUE2 FROM (
SELECT  A.HOSPITAL_CODE,  DEPT_CODE, CLASS1, YEAR_MONTH, COUNT(DISTINCT INDEX_NO)VALUE1 FROM (
SELECT A.HOSPITAL_CODE ,NVL(A.DEPT_CODE,-9999999) DEPT_CODE, A.DATA_TYPE CLASS1,TO_CHAR(A.INDEX_TIME,'YYYY-MM') YEAR_MONTH,INDEX_NO,
DECODE(REGEXP_REPLACE((OPERATION_NAME1||OPERATION_NAME2||OPERATION_NAME3||OPERATION_NAME4||OPERATION_NAME5||OPERATION_NAME6),'-|MS999',''),NULL,'无手术史','有手术史') AS OPERATION_NAME
 FROM WAREHOUSE.DW_M_VIEW A
 INNER JOIN (SELECT OPERATION_NAME1 ,OPERATION_NAME2,OPERATION_NAME3,OPERATION_NAME4,OPERATION_NAME5,OPERATION_NAME6,HOSPITAL_CODE,INPATIENT_NO FROM SOURCEDATA.INP_MR_FRONT_SHEET ) B
 ON  A.HOSPITAL_CODE=B.HOSPITAL_CODE AND A.INPATIENT_NO=B.INPATIENT_NO
  and a.data_type=1
 ) A 
 GROUP BY HOSPITAL_CODE,  DEPT_CODE, CLASS1, YEAR_MONTH
 )
GROUP BY HOSPITAL_CODE, DEPT_CODE, CLASS1, YEAR_MONTH
'''

result = decode_digui(sql)
print(result)
"""
