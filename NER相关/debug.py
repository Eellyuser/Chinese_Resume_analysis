

# import torch
#
# model = torch.load('./Model_Save/latest_model.pth')
# print(model)

from Util.Selenium_Util import Selenium_Edge
edge_driver = Selenium_Edge(update=True)




# import json
# with open('./Corpus_Path/key_mapping.json', 'r', encoding='utf-8') as file:
#     tag_mapping = json.load(file)
# # 定义中文标签到英文缩写的映射
# print(tag_mapping)
# from Util.util import get_date_filename
#
# # 现在可以直接使用这个函数
# filename = get_date_filename('haha')
# print(filename)
# os.makedirs(new_file_name, exist_ok=True)

# from Util import util
#
# util.get_default_tags('104.pdf')

# tag_to_biname = {'姓名': 'name', '出生年月': 'bir', '性别': 'gend', '电话': 'tel', '最高学历': 'acad',
#                          '籍贯': 'nati', '落户市县': 'live', '政治面貌': 'poli', '毕业院校': 'unv', '工作单位': 'comp',
#                          '工作内容': 'work', '职务': 'post', '项目名称': 'proj', '项目责任': 'resp', '学位': 'degr',
#                          '毕业时间': 'grti', '工作时间': 'woti', '项目时间': 'prti'}
#
# biname_to_tag = {v: k for k, v in tag_to_biname.items()}
# print(biname_to_tag)
# import json
# biname_to_tag = json.dump(biname_to_tag)
# print(biname_to_tag)


