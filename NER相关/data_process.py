from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

import shutil
import os
import json
from io import StringIO
import time
import logging

from Util import util





# 移动pdf并创建相关文件夹
def mkdir_from_pdf(pdf_path,is_mkdir_date=False):
    output_dir = util.create_or_find_date_dir(is_mkdir_date)
    print(f"输出路径:'{output_dir}'")
    # 遍历pdf_dir目录下的所有文件
    for filename in os.listdir(pdf_path):
        # 检查文件是否为PDF
        if filename.endswith('.pdf'):
            # 从文件名创建文件夹名称，去除.pdf扩展名
            folder_name = filename[:-4]
            # 在corpus_path下创建以PDF文件名命名的文件夹
            folder_path = os.path.join(output_dir, folder_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            # 构建原PDF文件的完整路径和目标路径
            src_file = os.path.join(pdf_path, filename)
            dest_file = os.path.join(folder_path, filename)
            # 移动PDF文件到新创建的文件夹
            shutil.move(src_file, dest_file)



if __name__ == '__main__':
    # text = get_str_from_pdf('./105.pdf')
    # with open('./Corpus_Path/Txt/105.txt', 'w', encoding='utf-8') as f:
    #     f.write(text)
    # tagging2txt()
    mkdir_from_pdf('./PDF_TEST',is_mkdir_date=False)
