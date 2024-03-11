import cv2
import numpy as np

# 由于执行环境被重置，需要重新加载图片并定义函数

# 定义空函数，用于创建滑动条
def empty(a):
    pass

# 读取图片
path_bg = './ip_img/target_bg.png'
img_bg = cv2.imread(path_bg)

# 转换到HSV色彩空间
imgHSV = cv2.cvtColor(img_bg, cv2.COLOR_BGR2HSV)

# 设定颜色阈值，这里我们使用蓝色的阈值作为示例
color = (61,80,79,241,232,255)
lower = np.array([color[0], color[2], color[4]])
upper = np.array([color[1], color[3], color[5]])

# 根据阈值创建掩码
mask = cv2.inRange(imgHSV, lower, upper)

# 应用掩码获取结果
imgResult = cv2.bitwise_and(img_bg, img_bg, mask=mask)

# 保存处理后的图片
cv2.imwrite('./ip_img/mask.png', mask)
cv2.imwrite('./ip_img/result.png', imgResult)

# 返回文件路径以便下载
mask_path = '/mnt/data/mask.png'
result_path = '/mnt/data/result.png'

