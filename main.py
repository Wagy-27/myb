# oracle -> hive:
# ORACLE 函数：to_char;to_date;SYSDATE
# 函数后面接的括号来区分部分
#  hive中子查询必须用别名命名，即FROM后面必须接括号。


# oracle sql语句的执行顺序：where中的部分先执行 －> 如果有group by，接着执行group by －> select中的函数计算、别名指定再运行－> 最后order by
# hive ： FROM -- WHERE -- GROUP BY -- HAVING -- SELECT -- ORDER BY

# hive中没有dual表

# hive中使用中文别名，只能用`代替"
'''
oracle:
TO_CHAR,NVL,DECODE,unpivot
hive:
DATE_FORMAT,COALESCE,CASE...WHEN..,later view(explode(map()))

PS:GROUP BY 中的DATE_FORMAT涉及的字段名要和SELECT 中一致。即select中使用A.(),则GROUP BY 中也必须用A.()
'''

import pandas as pd
import re
import Re_replace
import sqlparse
import sel_group2

def insert_subquery(table_n, result, SUM_SQL):
    """
    仅能对单个SQL语句进行。
    仅能处理FROM中子查询为一条的SQL语句，多了判断不了
    Args:
        table_n (list): 包含函数名和参数的列表
        result (str): 需要处理的字符串
        SUM_SQL (dict): 存储函数名和对应值的字典

    Returns:
        result: 处理后的字符串
    """
    for i in table_n:
        function_name = str.split(i, '(')[0]
        # 判断是否修改过该函数名   # 判定函数是否需要修改
        # if SUM_SQL.get(function_name, None) is None and Re_replace.re_type_mapping.get(function_name, None) is not None:
        if Re_replace.re_type_mapping.get(function_name.upper(), None) is not None:
            # SUM_SQL[function_name] = "10"
            str_temp = result
            result = Re_replace.re_type_mapping[function_name.upper()](str_temp)
    return result

def delete_dual(input_string):
    """
    删除dual表
    假设定义的dual表都是如下格式：
    SELECT '治愈' AS CLASS2 FROM DUAL UNION ALL
SELECT '好转' AS CLASS2 FROM DUAL UNION ALL
SELECT '未愈' AS CLASS2 FROM DUAL UNION ALL
SELECT '死亡' AS CLASS2 FROM DUAL UNION ALL
SELECT '其他' AS CLASS2 FROM DUAL UNION ALL
SELECT '空值' AS CLASS2 FROM DUAL
    Args:
        input_string (str): 需要处理的字符串
    """
    # input_string = re.sub(r'FROM\s+DUAL.*?',' ',input_string) # 防止乱加别名
    input_string =re.sub(r'FROM\s+DUAL.*?',' ',input_string)
    return input_string


# 获取excel表位置
# excel_path = r"C:\Users\GGZ1\Desktop\纵表-哮喘大屏副本1.xlsx"
# excel_path=r'C:\Users\GGZ1\Desktop\纵表-慢阻肺大屏-CLASS3 为空副本1.xlsx'
# excel_path = r"C:\Users\GGZ1\Desktop\纵表-支气管扩张大屏副本1.xlsx"
# excel_path = r"C:\Users\GGZ1\Desktop\纵表-数据概况大屏-CLASS3不为空副本1.xlsx"
excel_path = r"C:\Users\GGZ1\Desktop\纵表-数据概况大屏-CLASS3为空副本1.xlsx"
# excel_path = r"C:\Users\GGZ1\Desktop\纵表-肺动脉高压大屏副本1.xlsx"
# excel_path = r"C:\Users\GGZ1\Desktop\纵表-间质肺大屏副本1.xlsx"
# excel_path = r"C:\Users\GGZ1\Desktop\纵表-肺部真菌感染大屏副本1.xlsx"
# excel_path = r"C:\Users\GGZ1\Desktop\纵表-儿童哮喘大屏副本1.xlsx"
# excel_path = r"C:\Users\GGZ1\Desktop\纵表-哮喘-慢阻肺重叠综合大屏副本1.xlsx"
# excel_path = r"C:\Users\GGZ1\Desktop\纵表-肺部感染人群特征分析大屏副本1.xlsx"
# 打开excel表并读取其中列名为“&SQL1"和“&SQL2”
df = pd.read_excel(excel_path,dtype=object)
# 获取表行
num_rows = df.shape[0]
df["&SQL1_HIVE"] = None
df["&SQL2_HIVE"] = None
for i in range(num_rows):
    if i == 5 :
        print(i)
    for j in range(len(df.columns)):
        # 对于每一个SQL定义字典类防止重复修改
        SUM_SQL = dict()
        if df.columns[j] == "&SQL1" or df.columns[j] == "&SQL2":
            # 清理sql语句
            result = df.at[i, df.columns[j]]
            # 将其中的NULL 换成CAST(NULL AS STRING)
            # result = re.sub(r'\bNULL\b','CAST(NULL AS STRING)',result)  # 不太对，好像不是所有的NULL都需要改成CAST
            # 处理sql语句
            if re.findall(r'--(.*?)\n',result) != []:
                add_head = re.findall(r'--(.*?)\n', result)[0]  # 获取注释
            else:
                add_head = ""
            result = sqlparse.format(result, keyword_case='upper', strip_comments=True,reindent = True)
            result = result.replace('\xa0', ' ').replace('\n', ' ')
            result = re.sub(r'(\w+)\s+(\()', r'\1\2', result) # 去函数名和括号之间的空格
            result  = re.sub(r'\s+', ' ', result) # 将所有多于一个空格的换成一个空格。union all != union  all
            # 替换其中hive没有的函数
            table_n = Re_replace.count_sql_commands(result)  # 获取可能存在的函数名
            result = insert_subquery(table_n, result, SUM_SQL)
            # print(result)
            # 修改GROUP BY内容
            result = sel_group2.digui(result)
            # 删除dual表
            result = delete_dual(result)
            # print("df的类型：{}",type(df))
            result = sqlparse.format(result,reindent = True)  # 换成1阳间形式
            result = '--' + add_head + '\n' + result
            if df.columns[j] == "&SQL1":
                df.at[i, "&SQL1_HIVE"] = result
            elif df.columns[j] == "&SQL2":
                df.at[i, "&SQL2_HIVE"] = result
            else:
                continue
    print("已修改第{}行".format(i))
# 返回修改后的excel表
df.to_excel(excel_path,index=False)







