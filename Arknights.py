import cv2
import pyautogui
import numpy as np
import time
import random
import os

# 全局设置：匹配阈值 (0-1之间，越接近1越严格)
CONFIDENCE_THRESHOLD = 0.8


def get_screen_image():
    """
    获取屏幕截图并转换为OpenCV格式，无需保存到硬盘
    """
    # 获取截图 (RGB格式)
    sc_img = pyautogui.screenshot()
    # 转换为numpy数组
    sc_img = np.array(sc_img)
    # 转换为OpenCV需要的BGR格式
    sc_img = cv2.cvtColor(sc_img, cv2.COLOR_RGB2BGR)
    return sc_img


def find_image(template_path, max_retries=10):
    """
    在屏幕上寻找图片
    :param template_path: 模板图片路径
    :param max_retries: 最大重试次数（大约对应等待时间）
    :return: (x, y) 坐标元组，如果没找到返回 None
    """
    # 检查模板文件是否存在
    if not os.path.exists(template_path):
        print(f"错误：找不到模板文件 {template_path}")
        return None

    # 读取模板 (0表示灰度读取，对于简单的UI匹配通常足够且更快，也可以用1保持彩色)
    template = cv2.imread(template_path)
    if template is None:
        return None

    h, w = template.shape[:2]

    # 循环尝试寻找（相当于等待按钮出现）
    for i in range(max_retries):
        # 1. 获取屏幕画面
        target = get_screen_image()

        # 2. 模板匹配
        # 使用 TM_CCOEFF_NORMED 方法，结果越接近1表示越匹配
        result = cv2.matchTemplate(target, template, cv2.TM_CCOEFF_NORMED)

        # 3. 获取最大匹配值和位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        print(f"正在寻找 {template_path}，当前匹配度: {max_val:.2f} (尝试 {i + 1}/{max_retries})")

        # 4. 判断是否超过阈值
        if max_val >= CONFIDENCE_THRESHOLD:
            # 计算中心点
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return (center_x, center_y)

        # 没找到，稍作等待再试
        time.sleep(0.5)

    print(f"超时：未找到目标 {template_path}")
    return None


def random_click(x, y):
    """
    带随机偏移和随机延迟的点击
    """
    # 随机偏移 (-5 到 +5 像素)
    offset_x = random.randint(-5, 5)
    offset_y = random.randint(-5, 5)

    final_x = x + offset_x
    final_y = y + offset_y

    # 移动并点击
    pyautogui.moveTo(final_x, final_y, duration=random.uniform(0.1, 0.3))  # 模拟鼠标移动轨迹
    pyautogui.click()
    print(f"已点击坐标: ({final_x}, {final_y})")


def routine(img_model_path, name, wait_time=2):
    """
    执行一次完整的流程：寻找 -> 点击 -> 等待
    """
    print(f"--- 任务开始: {name} ---")
    pos = find_image(img_model_path)

    if pos:
        random_click(pos[0], pos[1])
        # 点击后随机等待一段时间，模拟人类反应
        sleep_time = wait_time + random.uniform(0, 1)
        print(f"等待 {sleep_time:.2f} 秒...")
        time.sleep(sleep_time)
        return True
    else:
        print(f"任务失败: 找不到 {name}")
        return False


if __name__ == "__main__":
    # 为了防止鼠标失控，设置这个可以在把鼠标移到屏幕左上角时强制停止脚本
    pyautogui.FAILSAFE = True

    # 示例流程
    # 假设这是刷一关的逻辑
    if routine("./pic/start.png", "打开终端"):
        # 如果点了开始，可能需要等几秒加载，再点下一个
        # 定位到没有打的关卡
        routine("pic/all citys.png", "曲谱")
        routine("pic/citys/darktime.png", "黑暗时代")
        routine("pic/citys/darktime/01.png", "黑暗时代01")
        # routine("./pic/乐章收集.png", "乐章收集", wait_time=5)

        #
        # routine("./pic/second.png", "接管作战", wait_time=5)
        # # 战斗结束结算
        # routine("./pic/end.png", "关卡结算")