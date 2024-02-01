import re
def re_tochar(input_string):
    # 定义正则表达式模式
    result = re.sub(r'TO_CHAR\(([^,]*?),\s*([^)]*?)\)',r'DATE_FORMAT(\1,\2)',input_string)
    #
    return result
def re_nvl(input_string):
    # 定义正则表达式模式
    result = re.sub(r'NVL\(([^,]*?),\s*([^)]*?)\)', r'COALESCE(\1,\2)', input_string)
    #
    return result

def re_decode(input_string):
    input_string = input_string.replace('\n', '')
    # input_string = input_string.replace('\xa0', '')
    pattern_test = re.compile(r'DECODE\(.*\)+.+,')
    result_test = re.findall(pattern_test, input_string)
    # 获取DECODE内容
    pattern = re.compile(r"DECODE\(([^)]+)\)\s+\w+")
    # 获取别名 ？如果不存在怎么办
    pattern2 = re.compile(r"DECODE\([^)]+\)\s*(\w+),")
    # 匹配
    result = re.findall(pattern, input_string)

    result2 = re.findall(pattern2,input_string)
    # 清理
    # 替换换行符 # 去除/xa0
    # result = [x.replace('\n', '').replace('\xa0', '') for x in result]
    # result2 = [x.replace('\n', '').replace('\xa0', '') for x in result2]

    split_temp = str.split(result[0],',')
    # 获取case项
    result = 'CASE ' + split_temp.pop(0)
    # 挨个获取对应的WHEN...THEN...
    while len(split_temp):
        # 输入对应的键对
        result = result + ' WHEN ' + split_temp.pop(0) + ' THEN ' + split_temp.pop(0)
    # 填写别名
    result = result + ' END AS ' + result2[0]
    result = re.sub(r'DECODE\(.*?\)\S*.*', result, input_string)
    return result

# 字典匹配
re_type_mapping = {
    "TO_CHAR": re_tochar,
    "NVL": re_nvl,
    "DECODE": re_decode
}


def count_sql_commands(input_string):
    # 使用正则表达式匹配 SQL 指令
    sql_commands = re.findall(r"\b\w+\(", input_string)
    return sql_commands
'''
excel_data_2 = "DECODE(B.INDEX_NAME,'ALLERGY_ASTHMA','哮喘','ALLERGY_RHINALLERGO','过敏性鼻炎','ALLERGY_URTICARIA','荨麻疹','ALLERGY_ECZEMA','湿疹','ALLERGY_AT_DERMATIT','特应性皮炎','ALLERGY_CONJ','过敏性结膜炎') CLASS2"
excel_data = "DECODE(b.INDEX_NAME,'ALLERGIC_ASTHMA_MAIN','过敏性哮喘','SEVERE_ASTHMA_MAIN','重症哮喘','EO_ASTHMA_MAIN','早发性哮喘','LO_ASTHMA_MAIN','晚发性哮喘', 'ESP_ASTHMA_MAIN','嗜酸粒细胞型哮喘','NTP_ASTHMA_MAIN','中性粒细胞型哮喘','OLI_ASTHMA_MAIN','寡粒细胞型哮喘','MIXG_ASTHMA_MAIN','混合粒细胞型哮喘') CLASS2"
result = re_decode(excel_data_2)
print(result)'''

