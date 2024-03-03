import os
from datetime import datetime
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import json
import shutil
from io import StringIO
from dateutil import parser
import re

PDF_DIR = './PDF_DIR'
PDF_TEST_DIR = './PDF_TEST'
# 保存结果
CORPUS_PATH = './Corpus_Path'

def get_date_filename(filepath,suffix="txt",filename=""):
    # 获取当前时间的时间戳
    current_time = datetime.now().strftime("%Y年%m月%d日%H时%M分")
    print(current_time)
    # 新文件名
    new_file_name = filepath + "/" + current_time + "-" + filename + "."+ suffix
    return new_file_name

def get_date_dir(filepath,filename=""):
    # 获取当前时间的时间戳
    current_time = datetime.now().strftime("%Y年%m月%d日%H时%M分")
    print(current_time)
    # 新文件名
    if filename != "":
        new_file_name = filepath + "/" + current_time + "-" + filename
    else:
        new_file_name = filepath + "/" + current_time
    return new_file_name

def get_default_tags(filename, json_file_path='Corpus_Path/all_tag.json'):
    # 定义默认的tags格式
    default_tags_format = {
        "name": "",
        "bir": "",
        "gend": "",
        "tel": "",
        "acad": "",
        "nati": "",
        "live": "",
        "poli": "",
        "unv": "",
        "work_experience": "",
        "education": "",
        "project_experience": "",
        "training_experience": "",
        "awards": "",
        "social_experience": "",
        "self_assessment": "",
        "career_objective": "",
        "skills": "",
        "interests": "",
        "certifications": "",
        "lab_experience": "",
        "language_skills": "",
        "research_work": "",
        "publications": "",
        "philosophy": "",
        "major_courses": "",
        "personal_experience": "",
        "self_introduction": "",
        "other": ""
    }

    # 检查文件是否存在
    if os.path.exists(json_file_path):
        # 文件存在，读取现有内容
        with open(json_file_path, 'r', encoding='utf-8') as file:
            tags = json.load(file)
    else:
        # 文件不存在，创建一个新的空字典
        tags = {}

    # 检查给定的filename是否已经存在于tags中
    if filename not in tags:
        # 如果filename不存在，添加新的键值对
        tags[filename] = default_tags_format

        # 将更新后的tags字典写回文件
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(tags, file, ensure_ascii=False, indent=4)
    else:
        # 如果filename已存在，什么也不做
        print(f"'{filename}' 已经存在于 '{json_file_path}'")

# 获取pdf文本
def get_str_from_pdf(pdf_path):
    content = ''  # 初始化空字符串，用于累积提取的文本内容

    # 检查给定的文件路径是否指向一个PDF文件
    if pdf_path.endswith('.pdf'):
        # 创建PDF资源管理器，用于存储共享资源
        rsrcmgr = PDFResourceManager(caching=True)
        # 设置文本布局分析的参数
        laparams = LAParams()
        # 创建一个字符串流，用于临时存储提取的文本
        retstr = StringIO()
        # 创建一个文本转换器，结合资源管理器、字符串流和布局参数
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)

        # 以二进制读取模式打开PDF文件
        with open(pdf_path, 'rb') as fp:
            # 创建PDF页面解释器，需要资源管理器和转换设备作为参数
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            # 遍历PDF文件中的每一页
            for page in PDFPage.get_pages(fp, pagenos=set()):
                # 确保页面旋转角度有效
                page.rotate = page.rotate % 360
                # 用页面解释器处理当前页，提取文本
                interpreter.process_page(page)

        # 完成所有页面的处理后，关闭转换设备
        device.close()
        # 从字符串流中获取累积的文本内容
        content = retstr.getvalue()
    # 对提取的文本进行后处理：去除首尾空白、删除换行符、分割成单词、重新连接成字符串
    words = content.strip().replace('\n', '').split()
    ret = ''.join(words)
    # 返回处理和清理后的纯文本字符串
    return ret


def create_or_find_date_dir(is_mkdir_date=False, corpus_path=CORPUS_PATH):
    now = datetime.now()
    date_str = now.strftime("%Y年%m月%d日%H时%M分")

    if is_mkdir_date:
        # 创建以当前日期时间命名的文件夹
        file_dir = os.path.join(corpus_path, date_str)
        os.makedirs(file_dir, exist_ok=True)
    else:
        # 查找最接近当前日期时间的文件夹
        closest_date = None
        closest_dir = None
        for dirname in os.listdir(corpus_path):
            try:
                dir_date = parser.parse(dirname, fuzzy=True)
                if closest_date is None or abs((now - dir_date).total_seconds()) < abs((now - closest_date).total_seconds()):
                    closest_date = dir_date
                    closest_dir = dirname
            except ValueError:
                # 如果文件夹名不能转换为日期，则忽略
                continue

        if closest_dir is not None:
            file_dir = os.path.join(corpus_path, closest_dir)
        else:
            # 如果没有找到接近的文件夹，创建一个新的
            file_dir = os.path.join(corpus_path, date_str)
            os.makedirs(file_dir, exist_ok=True)

    return file_dir


