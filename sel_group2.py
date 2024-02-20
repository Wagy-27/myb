import sqlparse
import re
import string
import random

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
    "COUNT_DISTINCT_APPROX":10.0,
    "count": 10.0,
    "sum": 10.0,
    "avg": 10.0,
    "max": 10.0,
    "min": 10.0,
    "std": 10.0,
    "var": 10.0,
    "first": 10.0,
    "last": 10.0,
    "concat": 10.0,
    "count_distinct": 10.0,
    "count_distinct_approx": 10.0
}

# 能进来的都是非空tokens
def Check_From_methon(input_string):
    """
    判定子查询是否自带别名
    :param token:
    :return:
    """
    token = sqlparse.parse(input_string)[0]
    for t in token.tokens:
        pattern = re.compile(r'([^()\s]+)',re.IGNORECASE | re.DOTALL)  # 判定是否存在别名
        if pattern.match(t.value):
            return False
    return True

def generate_random_string(length):
    # 生成包含大小写字母和数字的字符集
    characters = string.ascii_letters
    # 从字符集中随机选择指定长度的字符，并拼接成字符串
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def A(input_string):
    """
    去别名，去聚合函数
    :param input_string:
    :return:
    """
    # 去除SELECT中的别名  额外加了个避免DISTINCT A.INDEX_NO问题，特化构筑————’)VALUE2‘
    # select_str = re.sub(r'(?<!,)(?<!\.)\s+\w+(?!\.)|(?<=\))\w+', r'', select_str):
    pattern = re.compile(r'\b\w+\(', re.IGNORECASE | re.DOTALL)
    if re.search(r'^\s*CASE',input_string):
        input_string = re.sub(r'(?<=END\s)\s*.*', r'', input_string,re.IGNORECASE)
    elif pattern.search(input_string) and re.search(r'\|\|', input_string) == None:
        # if re.search(r'(\'|\")$', input_string) == None:
        input_string = re.sub(r'(?<=\))\s+.*', r'', input_string)
        # 去除SELECT中的聚合函数
        check = re.compile(r'\w+(?=\()', re.IGNORECASE | re.DOTALL)  # 获取所有函数名
        check_result = re.findall(check, input_string)
        if len(check_result) == 0:
            return input_string
        if Check_methon.get(check_result[0]):
            # 假设聚合函数不会出现在排头
            input_string = re.sub(fr'\s*{check_result[0]}\s*\(.*?\)\s*.*', r'', input_string,re.IGNORECASE)
    else:
        #if re.search(r'(\'|\")$', input_string):  # 函数内部直接跳过
        #    input_string = input_string
        # if re.search('\)',input_string):
        #    input_string = re.sub(r'(?<=\))\s*.*$', r'', input_string)  # 专门解决 sjlfewjf) jfkewljf这种
        #else:
        input_string = re.sub(r'\s+\w+$', r'', input_string,re.IGNORECASE)

    return input_string

def digui(input_string):
    Alias = generate_random_string(3)  # 随机别名
    pattern_select = re.compile(r'SELECT\s',re.IGNORECASE)
    pattern_group = re.compile(r'GROUP\s+BY',re.IGNORECASE)
    add_s = re.compile(r'\s*SELECT\s(.*?)\sFROM',re.IGNORECASE | re.DOTALL)
    input_string = re.sub(r'\n',' ',input_string)
    # input_string = sqlparse.format(input_string, reindent=True, keyword_case='upper')
    add_str = re.finditer(add_s, input_string)
    """
    for i in add_str:
        return_str = ""
        tmp_list = re.split(',(?![^()]*\))',i.group())
        for tmp in tmp_list :
            if re.search(r'.(\s).',tmp):
                return_str = return_str + re.sub(r'(.)\s(.)',r'\1 AS \2',tmp) + ","
            else:
                return_str = return_str + tmp + ","
        return_str = re.sub(r',$',r'',return_str)
    """
    # NULL补齐  测试 假设除了IS NOT NULL 以外就没有其他的NULL在外面了.现在多个case when中的等号判断
    input_string = re.sub(r'(?<!NOT\s)(?<!IS\s)(?<!=\s)NULL(?:\s+AS)?\b', r'NULL AS', input_string)
    # str补齐 避免 'EKFJL' FEKFJK被分开  能用，先用着。如果子查询出现在''之后就不行了
    # input_string = re.sub(r'(?<=,|\s)(\'\w+\')\s*(?!AS|as)(?!THEN)(?!END)(?!WHEN)(?!ELSE)(\w+)(?=,|\s)', r'\1 AS \2', input_string)
    """
    pattern_null = re.compile(r'(SELECT).*?(FROM|from)', re.IGNORECASE | re.DOTALL)
    temp_input = re.findall(pattern_null,input_string)
    for i in temp_input:
        i = re.sub(r'(?<!NOT\s)NULL', 'NULL AS',i)"""
    parse = sqlparse.parse(input_string)
    out_check_select = False
    into_identifier = False
    check_group = False
    check_identifier = False # 同一个select内容会被分成多个identifier
    select_str = ""  # 用于后续GROUP BY的一致
    result = ""  # 重拼input_string
    child_select_str = ""
    No_alias = True
    for token in parse[0].tokens:
        if token.ttype == sqlparse.tokens.Keyword.DML and token.value == "SELECT":
            # result = result + token.value
            out_check_select = True
        if token.ttype == sqlparse.tokens.Keyword or token.ttype == sqlparse.tokens.Keyword.DML:
            result = result + token.value
            check_identifier = False
            # 先放这里 out_check_select 的False判定
            if into_identifier:
                out_check_select = False
            if token.value == "GROUP BY":
                check_group = True
            into_identifier = True
        elif check_group and token.is_group:
            check_identifier = False
            result = result + select_str
            into_identifier = False
        elif token.is_group and (into_identifier or out_check_select):
            if pattern_select.search(token.value):  # 对应关键词的子句
                # inner ' SELECT INDEX_NO,HOSPITAL_CODE,DATA_ID FROM WAREHOUSE.DW_M_BASE WHERE DATA_ID IN(511, 1780, 1468, 1467, 1466, 2781, 2897, 1162) AND DATA_TYPE = 1 ) '

                # 通过遍历token的子tokens来确认是否是多个子查询，如果是多个必有','
                check_child_comma = False
                # temp_value = re.findall(r'\(\s*(.*)\).*$', token.value)[0]
                child_parse = token
                for checkchild in child_parse.tokens:
                    if checkchild.value == ",":
                        check_child_comma = True
                if check_child_comma:
                    for child in token.tokens:# 以下进行FROM下面包含多个子查询
                        if re.search(r'(?:(?<=\))|(?<=AS|as))\s*\w+\b(?!\s|,)',token.value):  # 匹配前面为右括号或者为大小as，后面不为逗号空格的外括号别名
                            No_alias = False
                        if pattern_select.search(child.value):
                            # 判定子查询是否自带别名
                            # temp_value = token.value[1:-1]  # 去掉左右括号

                            temp_value = ''
                            lef_ri = ''
                            try:
                                temp_value = re.findall(r'\(\s*(.*)\).*$',child.value)[0]
                                lef_ri = re.findall(r'(^.*?\().*(\).*$)',child.value)[0]
                                left = lef_ri[0]
                                if left != '(': # 如果没有左括号，说明前面是关键字，所以不需要加别名
                                    No_alias = False
                                right = lef_ri[1]
                            except Exception:
                                print(Exception)
                            # 有问题
                            child_select_str = digui(temp_value)  # 不知道子查询会不会带着括号回来 # 带着括号好像sqlparse就读不了了
                            child_select_str = left + child_select_str + right
                            # No_alias = Check_From_methon(child_select_str)
                            # select_str = select_str + child_select_str
                            if No_alias:
                                result = result + child_select_str + " AS " + Alias + " "
                            else:
                                result = result + child_select_str
                                No_alias = True

                        elif token.is_group:  # 得是数据
                            # select_str = select_str + A(t.value)
                            result = result + child.value
                        else:  # 除开数据的比如标点符号
                            result = result + child.value
                        select_str = select_str

                else:
                    if re.search(r'(?:(?<=\))|(?<=AS|as))\s*\w+\b(?!\s|,)$',token.value):  # 匹配前面为右括号或者为大小as，后面不为逗号空格的外括号别名
                        No_alias = False
                    if pattern_select.search(token.value):
                        # 判定子查询是否自带别名
                        # temp_value = token.value[1:-1]  # 去掉左右括号

                        temp_value = ''
                        lef_ri = ''
                        try:
                            temp_value = re.findall(r'\(\s*(.*)\).*$', token.value)[0]
                            lef_ri = re.findall(r'(^.*?\(\s*).*(\).*$)', token.value)[0]
                            left = lef_ri[0]
                            if left != '(':  # 如果没有左括号，说明前面是关键字，所以不需要加别名
                                No_alias = False
                            right = lef_ri[1]
                        except Exception:
                            print(Exception)
                        # 有问题
                        child_select_str = digui(temp_value)  # 不知道子查询会不会带着括号回来 # 带着括号好像sqlparse就读不了了
                        child_select_str = left + child_select_str + right
                        # No_alias = Check_From_methon(child_select_str)
                        # select_str = select_str + child_select_str
                    elif token.is_group:  # 得是数据
                        # select_str = select_str + A(t.value)
                        result = result + token.value
                    else:  # 除开数据的比如标点符号
                        result = result + token.value
                    select_str = select_str
                    if No_alias:
                        result = result + child_select_str + " AS " + Alias + " "
                    else:
                        result = result + child_select_str
                        No_alias = True
            elif out_check_select:  # 外侧SELECT
                token.value = re.sub(r'(?<!NOT\s)(?<!=\s)NULL(?:\s+AS)?\b', 'CAST(NULL AS STRING) AS', token.value) #?
                tmp_parse = token.value
                tmp_token = sqlparse.parse(tmp_parse)
                # tmp_list = re.split(',(?![^()]*\))',token.value)  # 有问题
                tmp_list = []
                # 注意：check_identifier要成立需要select中没有按as分割
                for select_token in tmp_token[0].tokens[0].tokens:  #  不知道为什么会有两层
                    if select_token.is_group or select_token.is_keyword:  # 暂定该判断，不一定对
                        tmp_list.append(select_token.value)
                for tmp in tmp_list:
                    if re.search(r'^\s+',tmp):
                        tmp = re.sub(r'^\s+',r'',tmp)
                    if check_identifier == False: # 一般来说，如果出现多个identifier,第一个位置的内容都是上一个结束的别名，直接跳过
                        tmp_str = A(tmp)
                        if tmp_str == "":
                            select_str = select_str
                        else:
                            select_str = select_str + tmp_str + ','
                    else:
                        check_identifier = False
                        select_str = select_str + ','

                select_str = re.sub(r',\s*$',r'',select_str)
                result = result + token.value
                check_identifier = True
                # out_check_select = False
            else:  # 其他情况
                result = result + token.value
        else:
            result = result + token.value

    return result


"""
sql = '''

----分子sjgkdp057  class3
select a.HOSPITAL_CODE, NVL(A.DEPT_CODE,-9999999) DEPT_CODE, a.data_type CLASS1,DIAG_CODE CLASS2,REPORT_NAME class3,TO_CHAR(A.INDEX_TIME,'YYYY-MM') YEAR_MONTH,sum(REPORT_VALUE) VALUE1
from warehouse.DW_M_VIEW A
inner join(
select index_no,report_id,report_name,report_value ,HOSPITAL_CODE
from(select index_no,report_id,HOSPITAL_CODE,
    DECODE(L_is_pulmonary,1,1,0) "肺通气功能检查",
    DECODE(L_is_bronchial,1,1,0) "支气管激发试验",
    DECODE(L_is_bronchodil,1,1,0) "支气管舒张试验",
    DECODE(L_is_pulmonary_diff,1,1,0) "肺弥散功能检查",
    DECODE(L_is_residual,1,1,0) "肺容积检查",
    DECODE(L_is_airway,1,1,0) "气道阻力检查",
    DECODE(L_LUNG_COMPRE,1,1,0) "肺功能综合" 
    from warehouse.dw_t_lung_screen where index_rule=1) as jfkef
    unpivot (report_value for report_name in (
    "肺通气功能检查",
    "支气管激发试验",
    "支气管舒张试验",
    "肺弥散功能检查",
    "肺容积检查",
    "气道阻力检查",
    "肺功能综合"))
)b on a.hospital_code=b.hospital_code and a.index_no=b.index_no     
inner join (
SELECT  INDEX_NO, HOSPITAL_CODE,DATA_VALUE,
CASE 
WHEN DATA_ID IN (858,1519) THEN 'COPD-001'
WHEN DATA_ID IN (772793458904666237) THEN 'PUFI-002'
WHEN DATA_ID IN (14860) THEN 'INLD-003'
WHEN DATA_ID IN (15710) THEN 'BRON-007'
WHEN DATA_ID IN (15525) THEN 'ADAS-006'
WHEN DATA_ID IN (3294) THEN 'PLUM-012'
WHEN DATA_ID IN (772793458904666375) THEN 'LC-001'
END AS DIAG_CODE
FROM WAREHOUSE.DW_M_DIAGNOSIS WHERE DATA_ID IN (858,14860,1519,15525,15710,3294,772793458904666237,772793458904666375)
AND (DATA_VALUE='1' OR  DATA_VALUE='有'OR DATA_VALUE='是')
UNION ALL
SELECT INDEX_NO,HOSPITAL_CODE,DATA_VALUE,'ALL-DIAG' DIAG_CODE
FROM WAREHOUSE.DW_M_DIAGNOSIS WHERE DATA_ID IN (858,14860,1519,15525,15710,3294,772793458904666237,772793458904666375)
AND (DATA_VALUE='1' OR  DATA_VALUE='有'OR DATA_VALUE='是') 
)c on a.hospital_code=c.hospital_code and a.INDEX_NO=c.INDEX_NO
group by a.HOSPITAL_CODE, NVL(A.DEPT_CODE,-9999999) , a.data_type ,DIAG_CODE ,REPORT_NAME,TO_CHAR(A.INDEX_TIME,'YYYY-MM')

'''
import Re_replace
def insert_subquery(table_n, result, SUM_SQL):
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
    input_string = re.sub(r'FROM\s+DUAL.*?',' ',input_string) # 防止乱加别名
    return input_string

sql = sqlparse.format(sql, reindent=True, keyword_case='upper')
sql = sqlparse.format(sql,reindex=True, keyword_case='upper', strip_comments=True)
sql = sql.replace('\xa0', ' ').replace('\n', ' ')
sql = re.sub(r'(\w+)\s+(\()', r'\1\2', sql) # 去函数名和括号之间的空格
sql = re.sub(r'\s+',' ', sql)
SUM_SQL = []
# result = sqlparse.parse(sql)
table_n = Re_replace.count_sql_commands(sql)  # 获取可能存在的函数名
result = insert_subquery(table_n,sql, SUM_SQL)
#result = digui(sql)
result = sqlparse.format(result,reindent = True)
print(result)

"""