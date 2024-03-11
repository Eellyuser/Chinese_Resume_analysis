import cv2
import numpy as np
# 滑动条的回调函数，获取滑动条位置处的值
def empty(a):
    h_min = cv2.getTrackbarPos("Hue Min","TrackBars")
    h_max = cv2.getTrackbarPos("Hue Max", "TrackBars")
    s_min = cv2.getTrackbarPos("Sat Min", "TrackBars")
    s_max = cv2.getTrackbarPos("Sat Max", "TrackBars")
    v_min = cv2.getTrackbarPos("Val Min", "TrackBars")
    v_max = cv2.getTrackbarPos("Val Max", "TrackBars")
    print(h_min, h_max, s_min, s_max, v_min, v_max)
    return h_min, h_max, s_min, s_max, v_min, v_max

# path = './ip_img/blue_yellow_qing.png'
path = './ip_img/target_bg.png'
# path = './test_img/yellow_orange.png'

# 白色部分为目标部分
# 青黄色 35 49 85 239 86 255
# 青黄色 24 89 171 255 180 255
# 蓝色 0 147 196 255 229 255
# 蓝色 68 179 204 255 157 255（墨色也包含）
# 橙色与黄色 0 68 153 255 146 255
# 青色 61 80 79 241 232 255(去除绿色)
color = (0,68,153,255,146,255)
color = (61,80,79,241,232,255)
# 创建一个窗口，放置6个滑动条
cv2.namedWindow("TrackBars")
cv2.resizeWindow("TrackBars",640,240)
cv2.createTrackbar("Hue Min","TrackBars",color[0],179,empty)
cv2.createTrackbar("Hue Max","TrackBars",color[1],179,empty)
cv2.createTrackbar("Sat Min","TrackBars",color[2],255,empty)
cv2.createTrackbar("Sat Max","TrackBars",color[3],255,empty)
cv2.createTrackbar("Val Min","TrackBars",color[4],255,empty)
cv2.createTrackbar("Val Max","TrackBars",color[5],255,empty)





while True:
    img = cv2.imread(path)
    imgHSV = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
    # 调用回调函数，获取滑动条的值
    h_min,h_max,s_min,s_max,v_min,v_max = empty(0)
    lower = np.array([h_min,s_min,v_min])
    upper = np.array([h_max,s_max,v_max])
    # 获得指定颜色范围内的掩码
    mask = cv2.inRange(imgHSV,lower,upper)
    # 对原图图像进行按位与的操作，掩码区域保留
    imgResult = cv2.bitwise_and(img,img,mask=mask)

    cv2.imshow("Mask", mask)
    cv2.imshow("Result", imgResult)

    cv2.waitKey(1)
