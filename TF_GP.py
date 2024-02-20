"""
target：
找到每组相对应的SELECT ... GROUP BY ...
将SELECT的内容填到GROUP BY中
————————————————
用栈来确定分组，同步将对应的内容填到平行栈中
一般来说SELECT之后跟的是FROM,GROUP BY 之后跟的是ORDER BY/HAVING/LIMIT/)
还需要去除SELECT中的别名部分
"""
import re
from queue import LifoQueue

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

def Get_new_input(str_l,str_r,input_string):
    # GROUP.*?(GROUP)
    # 切下来的部分
    str_temp = re.compile(fr"({str_l}.*?){str_r}",re.IGNORECASE | re.DOTALL)
    del_str = re.findall(str_temp,input_string)
    # 替换切下来的部分
    str_temp = re.compile(fr"{str_l}.*?({str_r})", re.IGNORECASE | re.DOTALL)
    str_temp = str_temp.sub(r'\1 ', input_string)  # 替换
    result = list()
    result.append(str_temp)  # 新语句
    result.append(del_str[0])  # 切下来的部分

    return result

def find_sg(input_string):
    """
    用列表拆分原输入SQL语句，最后结果又各部分合并
    :param input_string:
    :return:
    """
    SELECT = ""
    GROUP = ""
    result_list = list()  # 结果
    temp_fields = LifoQueue()  # 字段
    temp_str = LifoQueue()  # SELECT的语句
    input_tmp = input_string  # 原输入语句的切片
    # pattern = re.compile(r'((?:\bSELECT\b\s*))|((?:\bGROUP\b\s*))', re.IGNORECASE)
    pattern = re.compile(r'\b(SELECT|GROUP)\b',re.IGNORECASE | re.DOTALL)  # 获取所有的SELECT,GROUP
    result_pattern = re.findall(pattern, input_string)
    del_l = ""
# ——————————————————————————————————————————————————————————————————————————————————————————————————————————————
    # 为区分GROUP对应的位置，定义如果GROUP前面有右括号，则在将GROUP插入temp_fields时，额外在前面输入一个“N"字段
# ——————————————————————————————————————————————————————————————————————————————————————————————————————————————
    for i in result_pattern:
        if del_l != "":
            tmp_list = Get_new_input(del_l, i,input_tmp)
            input_tmp = tmp_list[0]
            result_list.append(tmp_list[1])
        if i == "SELECT":
            temp_fields.put(i)
            select_pattern = re.compile(r'SELECT(.*?)FROM',re.IGNORECASE | re.DOTALL)
            select_result = re.findall(select_pattern, input_tmp)
            # 去除SELECT中的别名
            select_result[0] = re.sub(r'(\b\w+\([^)]*\))\s*\w+',r'\1',select_result[0])
            # 去除SELECT中的聚合函数
            check = re.compile(r'(?:,)\s*(\w+)\(+',re.IGNORECASE | re.DOTALL)  # 获取所有函数名
            check_result = re.findall(check, select_result[0])
            for j in check_result:
                if Check_methon.get(j):
                    # 假设聚合函数不会出现在排头
                    select_result[0] = re.sub(fr',\s*{j}\s*\(.*?\)', r'', select_result[0])
            # print(check_result)
            temp_str.put(select_result[0])  #
        else:
            temp_fields.put(i)
            '''
            group_pattern = re.compile(r'GROUP BY (.+?)(?:\s(ORDER BY (.+?))|(?:\s+HAVING (.+?)))?(?:\s|$)', re.IGNORECASE)
            group_result = re.findall(group_pattern, input_tmp)
            temp_str.put(group_result[0])  #'''
        del_l = i
    result_list.append(input_tmp)
    group_tmp = LifoQueue()  # 过渡
    try:
        while not temp_fields.empty():
            str_name = temp_fields.get()  # GROUP\SELECT
            if str_name != "SELECT":
                str_line = result_list.pop(len(result_list) - 1)  # 对应的原语句切片
                group_tmp.put(str_name)
                group_tmp.put(str_line)
            else:
                insert_str = group_tmp.get()    # 对应的原语句切片
                group_tmp.get()
                select_str = temp_str.get()
                temp_pattern = re.compile(r'(GROUP\s+BY\s+).+?(?:\s(ORDER BY (.+?))|(?:\s+HAVING (.+?)))?(?:\s|$)', re.DOTALL)
                # print(re.findall(temp_pattern,insert_str))
                insert_str = re.sub(temp_pattern,fr'\1{select_str}', insert_str)
                GROUP = GROUP + insert_str  # 拼后半部分
    except Exception as e:
        print(e)
    else:
        while len(result_list)>0:
            SELECT = SELECT + result_list.pop(0)  # 拼前半部分

    return SELECT + GROUP


"""
excel_sql = "SELECT COL1,COL2 FROM(SELECT COL3,COL4 FROM TABLE GROUP BY COL5) GROUP BY COL6"
excel_sql2 ='''SELECT HOSPITAL_CODE, DEPT_CODE, CLASS1, YEAR_MONTH,SUM(VALUE2) VALUE2
FROM (
SELECT A. HOSPITAL_CODE, DEPT_CODE, A.DATA_TYPE CLASS1,
TO_CHAR(INDEX_TIME,'YYYY-MM') YEAR_MONTH, COUNT(DISTINCT A.INDEX_NO)VALUE2
FROM WAREHOUSE.DW_M_VIEW  A
WHERE A.AGE  >=12 AND A.RESPIRATORY8_MAIN = '有'
--拼接
GROUP BY A.HOSPITAL_CODE,DEPT_CODE,TO_CHAR(A.INDEX_TIME,'YYYY-MM'),A.DATA_TYPE
) 
GROUP BY HOSPITAL_CODE,DEPT_CODE,YEAR_MONTH,CLASS1'''
a = find_sg(excel_sql2)
print("以下是新SQL",a)"""
