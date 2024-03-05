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
import logging

PDF_DIR = './PDF_DIR'
PDF_TEST_DIR = './PDF_TEST'
# 保存结果
CORPUS_PATH = './Corpus_Path'

def get_index_by_automaton(segments, tag, txt_text):
    """
    通过自动机实例检索文本下标
    :param segments: 列表文本
    :param tag: 标记
    :param txt_text: 大段文本
    :return:
    """
    log_config = get_log_config()
    import ahocorasick
    # 创建 Aho-Corasick 自动机实例
    A = ahocorasick.Automaton()
    # 将列表中的每个文本项添加到自动机中作为模式
    for idx, pattern in enumerate(segments):
        A.add_word(pattern, (idx, pattern))
    # 构建自动机
    A.make_automaton()
    found_patterns = set()  # 用于存储找到的模式
    all_split_text = []
    # 遍历txt_text大段文字，查找列表中的文本
    for end_idx, (pattern_idx, pattern) in A.iter(txt_text):
        start_idx = end_idx - len(pattern) + 1
        split_text = {
            pattern: {
                "start_index": start_idx,
                "end_index": end_idx,
                "tag": tag,
            }
        }
        # print(split_text)
        log_config.warning(f"分词:{split_text} 标注为 {tag}")
        all_split_text.append(split_text)
        found_patterns.add(pattern)
    # 检查未找到的模式
    not_found_patterns = [pattern for pattern in segments if pattern not in found_patterns]
    # 处理未找到的模式
    for pattern in not_found_patterns:
        log_config.error(f"分词:{pattern} 未标注为 {tag}")
    return all_split_text

def get_log_config(log_path='./Corpus_Path/Log'):
    """
    获取日志配置
    :param log_path: 日志路径
    :return:
    """
    logger = logging.getLogger('my_logger')
    logger.setLevel(logging.DEBUG)  # 设置最低的日志级别

    if not os.path.exists(log_path):
        os.makedirs(log_path)
        print(f"日志路径已生成于{log_path}")

    info_path = os.path.join(log_path, 'Info.log')
    warning_path = os.path.join(log_path, 'Warning.log')
    error_path = os.path.join(log_path, 'Error.log')

    # 定义日志格式
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    class InfoFilter(logging.Filter):
        def filter(self, record):
            # 只允许INFO级别的日志记录通过过滤器
            return record.levelno == logging.INFO

    class WarningFilter(logging.Filter):
        def filter(self, record):
            # 只允许INFO级别的日志记录通过过滤器
            return record.levelno == logging.WARNING

    # 检查是否已存在相同配置的INFO级别处理器
    if not any(handler for handler in logger.handlers if isinstance(handler, logging.FileHandler) and handler.level == logging.INFO):
        info_handler = logging.FileHandler(info_path, encoding='utf-8')
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)
        info_handler.addFilter(InfoFilter())
        logger.addHandler(info_handler)

    # 检查是否已存在相同配置的WARNING级别处理器
    if not any(handler for handler in logger.handlers if isinstance(handler, logging.FileHandler) and handler.level == logging.WARNING):
        warning_handler = logging.FileHandler(warning_path, encoding='utf-8')
        warning_handler.setLevel(logging.WARNING)
        warning_handler.setFormatter(formatter)
        warning_handler.addFilter(WarningFilter())
        logger.addHandler(warning_handler)

    # 检查是否已存在相同配置的ERROR级别处理器
    if not any(handler for handler in logger.handlers if isinstance(handler, logging.FileHandler) and handler.level == logging.ERROR):
        error_handler = logging.FileHandler(error_path, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)

    return logger

def get_date_filename(filepath,suffix="txt",filename=""):
    """
    默认以时间为单位+filename命名的txt文件
    :param filepath: 文件路径
    :param suffix: 后缀
    :param filename: 添加的名字
    :return:
    """
    # 获取当前时间的时间戳
    current_time = datetime.now().strftime("%Y年%m月%d日%H时%M分")
    print(current_time)
    # 新文件名
    new_file_name = filepath + "/" + current_time + "-" + filename + "."+ suffix
    return new_file_name

# 获取时间+文件名，若无文件名返回时间
def get_date_dir(filepath,filename=""):
    """
    默认以时间为单位命名的文件夹名称
    :param filepath:
    :param filename:
    :return:
    """
    # 获取当前时间的时间戳
    current_time = datetime.now().strftime("%Y年%m月%d日%H时%M分")
    print(current_time)
    # 新文件名
    if filename != "":
        new_file_name = filepath + "/" + current_time + "-" + filename
    else:
        new_file_name = filepath + "/" + current_time
    return new_file_name

def get_str_from_pdf(pdf_path):
    """
    从PDF文件中提取文本内容
    :param pdf_path: pdf路径
    :return:
    """
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
    """
    # 寻找离当前时间最近的文件夹，或者由当前时间命名的文件夹
    :param is_mkdir_date: 是否创建以当前日期时间命名的文件夹
    :param corpus_path: 父文件目录
    :return:
    """
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


