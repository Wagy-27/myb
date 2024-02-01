#oracle -> hive:
#ORACLE 函数：to_char;to_date;SYSDATE
#函数后面接的括号来区分部分
#hive中子查询必须用别名命名，即FROM后面必须接括号。
#函数差异如下
'''
oracle:
TO_CHAR,NVL,DECODE
hive:
DATE_FORMAT,COALESCE,CASE...WHEN..
'''
#递归按括号修改————是否有需要？看起来SQL函数是相互独立的，先改外面和先改里面没啥区别
import pandas as pd
import Re_replace



def insert_subquery(table_n, result, SUM_SQL):
    """
    Args:
        table_n (list): 包含函数名和参数的列表
        result (str): 需要处理的字符串
        SUM_SQL (dict): 存储函数名和对应值的字典

    Returns:
        result: 处理后的字符串
    """
    for i in table_n:
        function_name = str.split(table_n[0], '(')[0]
        # 判断是否修改过该函数名   # 判定函数是否需要修改
        if SUM_SQL.get(function_name, None) is None and Re_replace.re_type_mapping.get(function_name, None) is not None:
            SUM_SQL[function_name] = "10"
            str_temp = result
            result = Re_replace.re_type_mapping[function_name](str_temp)
    return result



# 获取excel表位置
excel_path = r"C:\Users\GGZ1\Desktop\纵表-哮喘大屏副本1.xlsx"
# excel_path=r'C:\Users\GGZ1\Documents\数仓学习资料\大数据平台各个原表\纵表-慢阻肺大屏-CLASS3 为空.xlsx'
# 打开excel表并读取其中列名为“&SQL1"和“&SQL2”
df = pd.read_excel(excel_path,dtype=object)
# 获取表行
num_rows = df.shape[0]
df["&SQL1_HIVE"] = None
df["&SQL2_HIVE"] = None
for i in range(num_rows):
    for j in range(len(df.columns)):
        # 对于每一个SQL定义字典类防止重复修改
        SUM_SQL = dict()
        if df.columns[j] == "&SQL1" or df.columns[j] == "&SQL2":
            table_n = Re_replace.count_sql_commands(df.at[i,df.columns[j]])
            temp_list = table_n
            result = insert_subquery(temp_list, df.at[i, df.columns[j]], SUM_SQL)
            if df.columns[j] == "&SQL1":
                df.at[i, "&SQL1_HIVE"] = result
            else:
                df.at[i, "&SQL2_HIVE"] = result

df.to_excel(excel_path,index=False)







