import pandas as pd
import json

# # 读取Excel文件并获取所有工作表名称
# excel_file = pd.ExcelFile('./organization_data.xlsx')
# sheet_names = excel_file.sheet_names
# print(f"Excel文件包含以下工作表: {sheet_names}")

# # 创建字典存储所有工作表的数据
# all_sheets_data = {}

# # 创建最终的JSON数组
# final_json_data = []

# # 遍历并读取每个工作表
# for sheet_name in sheet_names:
#     # 读取当前工作表，使用第二行(索引1)作为列名
#     df = pd.read_excel(excel_file, sheet_name=sheet_name, header=1)
    
#     # 将数据存入字典
#     all_sheets_data[sheet_name] = df
    
#     # 输出当前工作表的基本信息
#     # print(f"\n工作表 '{sheet_name}' 包含 {len(df)} 行数据")
#     # print(f"列名: {list(df.columns)}")
#     # print("前3行数据预览:")
#     # print(df.head(3).to_string(index=False))  # 不显示索引列
    
#     # 示例：对每个工作表进行特定处理（根据实际需求修改）
#     # 获取所有数据
#     sheet_data = df.values
    
#         # 创建当前sheet的数据结构
#     sheet_data = {
#         "name": sheet_name,
#         "ifChoose": True,  # 默认为True，可根据需求修改
#         "organizationList": []
#     }
    
#     # 将DataFrame转换为字典列表
#     for _, row in df.iterrows():
#         org_item = {
#             "index": str(row.get('序号', '')),  # 假设Excel中有"序号"列
#             "name": str(row.get('名称', '')),   # 假设Excel中有"名称"列
#             "address": str(row.get('地址', '')), # 假设Excel中有"地址"列
#             "type": str(row.get('类型', '')),   # 假设Excel中有"类型"列
#             "mobile": str(row.get('服务电话', ''))  # 假设Excel中有"电话"列
#         }
#         sheet_data["organizationList"].append(org_item)
    
#     # 将当前sheet的数据添加到最终数组
#     final_json_data.append(sheet_data)

# # 将数据写入JSON文件
# with open('output.json', 'w', encoding='utf-8') as f:
#     json.dump(final_json_data, f, ensure_ascii=False, indent=2)

# print(f"已成功处理 {len(sheet_names)} 个工作表的数据并导出到 output.json")

# # 关闭Excel文件
# excel_file.close()

# 读取JSON文件
with open('byorg.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

print(f"成功读取JSON文件，包含 {len(json_data)} 个组织分类")

# 创建Excel写入器
excel_writer = pd.ExcelWriter('big_organization_data_output.xlsx', engine='xlsxwriter')

# 遍历JSON数据中的每个分类
for org_category in json_data:
    category_name = org_category.get('name', '未命名分类')
    org_list = org_category.get('organizationList', [])
    
    print(f"处理分类: {category_name}，包含 {len(org_list)} 个组织")
    
    # 如果组织列表为空，创建一个空DataFrame
    if not org_list:
        df = pd.DataFrame()
    else:
        # 将组织列表转换为DataFrame
        df = pd.DataFrame(org_list)
        
        # 重命名列以匹配原Excel格式
        columns_mapping = {
            'index': '序号',
            'name': '名称',
            'address': '地址',
            'type': '类型',
            'mobile': '服务电话'
        }
        
        # 应用列重命名（仅对存在的列）
        existing_columns = set(df.columns).intersection(columns_mapping.keys())
        rename_dict = {col: columns_mapping[col] for col in existing_columns}
        df = df.rename(columns=rename_dict)
    
    # 获取工作簿和工作表对象
    workbook = excel_writer.book
    worksheet = workbook.add_worksheet(category_name)
    excel_writer.sheets[category_name] = worksheet
    
    # 创建格式对象
    header_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#D9E1F2',  # 浅蓝色背景
        'border': 1
    })
    
    column_header_format = workbook.add_format({
        'bold': True,
        'font_size': 11,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#E2EFDA',  # 浅绿色背景
        'border': 1
    })
    
    cell_format = workbook.add_format({
        'align': 'left',
        'valign': 'vcenter',
        'border': 1
    })
    
    
    # 写入标题并合并单元格
    if not df.empty:
        worksheet.merge_range(0, 0, 0, len(df.columns) - 1, f"{category_name}组织列表", header_format)
        
        # 写入列标题
        for col_num, col_name in enumerate(df.columns):
            worksheet.write(1, col_num, col_name, column_header_format)
        
        # 写入数据
        for row_num, row_data in enumerate(df.values):
            for col_num, cell_value in enumerate(row_data):
                worksheet.write(row_num + 2, col_num, cell_value, cell_format)
        
        # 自动调整列宽
        for col_num, col_name in enumerate(df.columns):
            # 获取列中最长内容的长度
            max_len = 0
            # 检查列名长度
            max_len = max(max_len, len(str(col_name)))
            # 检查数据长度
            for row_num in range(len(df)):
                cell_value = df.iloc[row_num, col_num]
                cell_len = len(str(cell_value)) if cell_value else 0
                max_len = max(max_len, cell_len)
            
            # 设置列宽 (根据字符数调整，中文字符需要更宽)
            adjusted_width = max_len * 1.2  # 乘以1.2以适应中文字符
            worksheet.set_column(col_num, col_num, adjusted_width)
    else:
        # 如果没有数据，只写入标题
        worksheet.write(0, 0, f"{category_name}组织列表", header_format)

# 保存Excel文件
excel_writer.close()

print(f"已成功将JSON数据转换为Excel文件: big_organization_data_output.xlsx")