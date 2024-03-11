import os
# 封装底层os，写文件路径
import shutil
# 多线程
import subprocess
from datetime import datetime
from pprint import pprint
import re
from time import sleep
import json

from selenium import webdriver
from selenium.common import StaleElementReferenceException, SessionNotCreatedException, TimeoutException, \
    ElementNotInteractableException,ElementClickInterceptedException
from selenium.webdriver import ActionChains
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.wait import WebDriverWait

from functools import wraps


class Selenium_Edge:
    def __init__(self, update=False, cookies=False, cookies_url = None,proxy=False):
        self.update  = update
        self.cookies = cookies
        self.cookies_url = cookies_url
        self.proxy = proxy
        self.driver = self.create_driver()


    def create_driver(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 Edg/110.0.1587.57'}
        s = Service('./drive/msedgedriver.exe')

        def init_webdriver():
            download_path = os.getcwd()
            print(f"下载目录:\n{download_path}")
            options = Options()
            # 尝试添加detach选项
            # options.add_experimental_option("detach", True)
            # 设置下载路径
            prefs = {"download.default_directory": download_path}
            options.add_experimental_option("prefs", prefs)
            if self.update:
                Selenium_Edge.update_driver()
            driver = webdriver.Edge(service=s, options=options)
            if self.cookies:
                driver.get(self.cookies_url)
                self.set_cookies(driver)
            if self.proxy:
                proxy = 'localhost:7890'
                # 配置Edge选项
                options.use_chromium = True  # 指明使用基于Chromium的Edge
                options.add_argument(f'--proxy-server={proxy}')
            return driver

        driver = init_webdriver()
        action = ActionChains(driver)
        return driver

    # 更新驱动
    @staticmethod
    def update_driver():
        def get_edge_version():
            try:
                command = r'reg query "HKEY_CURRENT_USER\Software\Microsoft\Edge\BLBeacon" /v version'
                output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
                version_match = re.search(r"version\s+REG_SZ\s+([\d.]+)", output)
                if version_match:
                    return version_match.group(1)
                else:
                    return "Edge 版本号未找到"
            except subprocess.CalledProcessError as e:
                return f"命令执行错误: {e.output}"

        def get_driver_version(driver_path):
            # 检查驱动路径是否存在
            if not os.path.exists(driver_path):
                print("驱动不存在。")
                return "0.0.0.0"
            print("正在测试驱动版本")
            s = Service(driver_path)
            try:
                driver = webdriver.Edge(service=s)
                version = driver.capabilities['browserVersion']
                driver.quit()
            except SessionNotCreatedException as e:
                # 使用正则表达式从异常消息中提取版本信息
                match = re.search(r"Microsoft Edge version (\d+)", str(e))
                if match:
                    unsupported_version = match.group(1)
                    print(f"驱动不支持的版本是:{unsupported_version}")
                current_version_match = re.search(r"Current browser version is (\d+\.\d+\.\d+\.\d+)", str(e))
                if current_version_match:
                    current_version = current_version_match.group(1)
                    print(f"驱动不支持的版本是: {current_version}")
                return unsupported_version

            return version

        browser_version = get_edge_version()
        driver_version = get_driver_version("./drive/msedgedriver.exe")
        print(f"您的浏览器版本{driver_version}\n驱动版本{browser_version}")
        if (browser_version != driver_version):
            print(".........正在更新驱动.........")

            def delete_directory(target_directory):
                # 检查目标目录是否存在
                if os.path.exists(target_directory):
                    try:
                        # 使用rmtree删除目录及其所有内容
                        shutil.rmtree(target_directory)
                        print(f"{target_directory} 已成功删除。")
                    except Exception as e:
                        print(f"删除 {target_directory} 时出错: {e}")
                else:
                    print(f"{target_directory} 不存在。")

            driver_path = EdgeChromiumDriverManager().install()
            print(f"正在下载驱动，默认位置:\n{driver_path}")
            # 获取驱动程序所在的文件夹路径
            driver_directory = os.path.dirname(driver_path)
            # 获取当前工作目录
            current_directory = os.getcwd()
            # 构建目标文件夹路径
            target_directory = os.path.join(current_directory, "drive")
            # 将驱动程序文件夹移动到目标文件夹
            if os.path.exists(target_directory):
                shutil.rmtree(target_directory)
            shutil.move(driver_directory, target_directory)
            print(f"正在从\n{driver_path}\n移动驱动至\n{target_directory}")
            # 更新驱动程序路径为目标文件夹下的路径
            driver_path = os.path.join(target_directory, os.path.basename(driver_path))
            # 从driver_directory变量中截取.wdm的路径
            wdm_directory = os.path.join(*driver_directory.split(os.sep)[:3], ".wdm")
            # 删除驱动目录与缓存目录
            print(f"正在删除驱动目录:\n{wdm_directory}")
            delete_directory(wdm_directory)
            selenium_cache_directory = os.path.join(*driver_directory.split(os.sep)[:3], ".cache", "selenium")
            print(f"正在删除缓存目录:\n{selenium_cache_directory}")
            delete_directory(selenium_cache_directory)
            # 多线程废弃
            # 初始化webdriver
            # driver = webdriver.Edge(executable_path=driver_path)
            # return driver
            driver_state = False
            print(".........更新驱动完毕.........")
        else:
            print("驱动已更新")

    def get_driver(self, url, wait_time=10, wait_element_xpath=None):
        try:
            self.driver.get(url)
        except TimeoutException:
            print(f"页面在 {wait_time} 秒内未完全加载或未找到元素：{wait_element_xpath}")
            self.driver.get(url)
            return
        # 如果提供了等待元素的XPath，则等待该元素加载
        if wait_element_xpath:
            try:
                WebDriverWait(self.driver, wait_time).until(
                    EC.presence_of_element_located((By.XPATH, wait_element_xpath))
                )
            except TimeoutException:
                print(f"页面在 {wait_time} 秒内未完全加载或未找到元素：{wait_element_xpath}")

    @staticmethod
    def locate_element(func):
        @wraps(func)
        def wrapper(self, xpath, xpath_kind=By.XPATH, father_element=None, default_value="Null",timeout=3, *args, **kwargs):
            if father_element is None:
                father_element = self.driver
            element = None
            try:
                element = WebDriverWait(father_element, timeout).until(
                    EC.presence_of_element_located((xpath_kind, xpath))
                )
            except (TimeoutException, AttributeError):
                # 如果无法找到元素，不调用func)
                return default_value
            # 如果找到了元素，调用func
            return func(self, element, *args, **kwargs)
        return wrapper

    @locate_element
    def get_element_attribute(self, element, default_value, attribute='textContent'):
        try:
            # 'textContent' 标签内的文字
            # 'innerHTML'   标签的html
            # 'outerHTML'   标签的完整 html
            # ’href'        链接地址
            return element.get_attribute(attribute)
        except Exception as e:
            return default_value

    @locate_element
    def get_element(self, element, default_value):
        return element if element is not None else default_value

    @locate_element
    def get_element_text(self, element, default_value):
        try:
            text = element.text.strip()  # 移除可能的前后空白字符
            return text if text else "None"  # 如果文本不为空，则返回文本，否则返回None
        except Exception as e:
            return default_value  # 发生异常时返回默认值

    @staticmethod
    def locate_elements(func):
        @wraps(func)
        def wrapper(self, xpath, xpath_kind=By.XPATH, father_element=None, default_value="Null", *args, **kwargs):
            if father_element is None:
                father_element = self.driver
            try:
                elements = WebDriverWait(father_element, 3).until(
                    EC.presence_of_all_elements_located((xpath_kind, xpath))
                )
                return func(self, elements, *args, **kwargs)
            except (TimeoutException, AttributeError):
                return default_value
        return wrapper

    # 批量解决同一类型元素，对特殊元素需自己进行调用单个元素方法处理
    @locate_elements
    def get_elements(self, elements, default_value):
        return elements if elements else [default_value]

    @locate_elements
    def get_elements_text(self, elements, default_value):
        text_list = []
        for element in elements:
            try:
                text = element.text.strip()  # 移除可能的前后空白字符
                text_list.append(text if text else "None")
            except Exception as e:
                text_list.append(default_value)  # 发生异常时添加默认值
        return text_list

    @locate_element
    def click_element(self, element):
        try:
            element.click()
        except (ElementNotInteractableException,ElementClickInterceptedException):
            print("点击失败！")

    @locate_element
    def input_text(self, element, text):
        element.clear()
        element.send_keys(text)

    def get_cookies(self):
        cookie_dict = {}
        for cookie in self.driver.get_cookies():
            cookie_dict[cookie['name']] = cookie['value']
        with open('cookies.json', 'w') as file:
            json.dump(cookie_dict, file)
            print("Cookies已保存至cookies.json")
        return cookie_dict

    def set_cookies(self, driver):
        # 从文件中读取cookies
        with open('cookies.json', 'r') as file:
            cookies = json.load(file)
        # 遍历字典，为每个cookie调用add_cookie方法
        for name, value in cookies.items():
            cookie_dict = {
                'name': name,
                'value': value
            }
            driver.add_cookie(cookie_dict)
        print("已从cookies.txt中加载cookies")

    def get_text(self,element):
        return element.text.strip()

    @locate_element
    def wait_element(self,element, checktext):
        text = self.get_text(element)
        if(checktext == text):
            return True
        else:
            print(f"应获取文字:{checktext},实获取文字:{text}")
            return False


    @locate_element
    def check_element(self,element):
        try:
            element
            print("查找到当前元素")
            return True
        except :
            print("没有当前元素")
            return False

    def destory(self):
        self.driver.quit()

class OpenCv_Util:
    def __init__(self):
        pass

    @staticmethod
    def mkdir(url):
        if not os.path.exists(url):
            os.mkdir(url)
            print(f"{url}文件夹已创建")
        else:
            print(f"{url}文件夹已存在")

