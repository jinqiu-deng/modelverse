import requests
import json
from time import sleep
import csv
import os
import re
import pandas as pd

url = "http://52.53.130.54:8080/"

#  input_file_name =  '../data/apple_sku_name.csv'
#  output_file_name = '../data/apple_sku_info.csv'

#  prompt_class = '''
#      public class sku {
#          string 品牌;
#          string 产地;
#          int 个数（个）; // 单位：个
#          int 大小（mm）; // 单位：毫米
#          float 总重量（kg）; // 单位：千克
#          float 单果重量（g）; // 单位：克
#      }
#  '''

input_file_name =  '../data/melon_seed_sku_name.csv'
output_file_name = '../data/melon_seed_sku_info.csv'

sku_batch_count = 5

prompt_class = '''
    public class sku {
        long sku_id;
        float 总重量（g）; // 单位：g, 必须是所有商品的重量总和，是一个以克为单位的浮点型数字
        string 品牌;
        string 产地;
        string 类别; // 只能是如下值，禁止使用其它值：南瓜子,吊瓜子,瓜子仁,葵花瓜子,葵花籽,西瓜子,黑瓜子,其它
        string 口味; // 只能是如下值，禁止使用其它值：五香味,原味,咸味,多味,奶油味,山核桃味,核桃味,椒盐味,椰香味,水煮味,海盐味,混合味,炭烧味,烧烤味,焦糖味,牛肉味,甘草味,甜味,盐焗味,紫薯味,绿茶味,藤椒味,蟹黄味,话梅味,香辣味,麻辣味,黑糖味,其它
        string 包装; // 只能是如下值，禁止使用其它值：盒装, 分享装, 箱装, 罐装, 袋装, 多包, 礼盒装, 其它
        int 件数;
        boolean 是否带皮;
    }
'''

output_file_exists = os.path.isfile(output_file_name)

sku_id_exist = None
if output_file_exists:
    df_sku_exist = pd.read_csv(output_file_name)
    sku_id_exist = set(df_sku_exist['sku_id'].astype(int))

# 读取Excel文件
data = pd.read_csv(input_file_name)

sku_to_process = {}

# 遍历每一行并输出
for index, row in data.iterrows():
    sku_id = row['sku_id']
    sku_name = row['sku_name']

    if (sku_id_exist is not None) and (sku_id in sku_id_exist):
        print('{} exist'.format(sku_name))
        continue

    sku_to_process[sku_id] = sku_name

    if len(sku_to_process) >= sku_batch_count:
        batch_sku_names = ''
        for key, value in sku_to_process.items(): batch_sku_names += '{}: {}\n'.format(key, value)

        message = batch_sku_names + '''
        基于class sku的定义生成对象，表示上面每个sku

        转化要求：
        1. 不要使用上面sku描述之外的信息
        3. 没有值填null

        计量单位关系：
        1斤=0.5千克

        ''' + prompt_class + '''
        你要回答的结果：json array包含上面每个对象的json表示。只返回json array！！！不要返回任何java代码！！！
        '''

        print(message)

        # Make a request to the API to generate the JSON for the SKU
        request_data = {'model': "gpt-3.5-turbo", 'temperature': 0, 'messages': [{'role': "user", 'content': message}]}
        response = requests.post(url=url, json=request_data).text

        response_json = json.loads(response)
        batch_sku_info = response_json['completion']['choices'][0]['message']['content']

        print(batch_sku_info)

        # 定义替换函数，该函数将计算公式的结果替换回原始字符串
        def replace_with_result(match):
            formula = match.group(1)
            result = eval(formula)
            return str(result)

        # 使用 re.sub() 函数将计算结果替换回原始字符串
        pattern = r'(\d+ \* \d+)'
        batch_sku_info_updated = re.sub(pattern, replace_with_result, batch_sku_info)

        if batch_sku_info_updated != batch_sku_info:
            print('eval fomula' + batch_sku_info_updated)

        batch_sku_info_json = json.loads(batch_sku_info_updated)

        # Loop through array
        for sku_info_json in batch_sku_info_json:
            sku_id = sku_info_json['sku_id']
            sku_name = sku_to_process[sku_id]

            # 将产品名称添加到字典中
            sku_info_json["SKU名称"] = sku_name

            # 获取字典中的键和值作为表头和数据行
            headers = list(sku_info_json.keys())
            data_row = list(sku_info_json.values())

            print(sku_info_json)

            # 将数据写入CSV文件
            with open(output_file_name, "a", encoding="utf-8", newline="") as csvfile:
                csv_writer = csv.writer(csvfile)

                if not output_file_exists:
                    csv_writer.writerow(headers)
                    output_file_exists = True

                # Write the data row
                csv_writer.writerow(data_row)

        sku_to_process = {}

        # Wait for 1 second before making the next request
        sleep(1)
