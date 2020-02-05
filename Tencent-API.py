import requests                         # 访问API接口
import hashlib                          # 导入hashlib库
import base64                           # 导入base64库
import time                             # 导入time库
import random                           # 导入random库
import string                           # 导入String库
import json                             # 导入json库
from urllib.parse import urlencode      # 导入urlencode
from PIL import Image,ImageDraw         # 导入Pillow库

APP_ID = '*********'
APP_KEY = '*********'

# 鉴权计算并返回请求参数
def get_params(image):
    # 请求时间戳,防止请求重放(保证签名5分钟内有效)
    time_stamp = str(int(time.time()))
    # 请求随机字符串,保证签名不可预测
    nonce_str = ''.join(random.sample(string.ascii_letters + string.digits,16))

    params = {
        'app_id' : APP_ID,          # 应用标识    
        'time_stamp' : time_stamp,  # 请求时间戳（秒级）        
        'nonce_str' : nonce_str,    # 随机字符串       
        # ‘sign’:None               # 签名信息       
        'image' : image,            # 待识别图片       
        'mode' : '0',               # 签名信息
    }
    # 字典排序
    sort_dict = sorted(params.items(),key = lambda item:item[0],reverse = False)
    # 尾部添加APP_KEY
    sort_dict.append(('app_key',APP_KEY))
    # URLencod编码
    rawtext = urlencode(sort_dict).encode()
    # 实例化MD5加密对象
    encrypt = hashlib.md5()
    # MD5加密计算
    encrypt.update(rawtext)
    mad5text = encrypt.hexdigest().upper()
    # 将签名赋值到sign字段
    params['sign'] = mad5text
    # 返回请求参数
    return params

def TencentOpenAi(filename):
    # 打开图像
    img = open(filename,'rb')
    # 对图像进行base64编码
    base64_data = base64.b64encode(img.read())
    # 对原图像进行base64解码,得到所处理图像
    image = base64_data.decode()
    # 获取鉴权签名并获取请求参数
    params = get_params(image)
    # 腾讯OpenAI人脸识别接口
    url = 'https://api.ai.qq.com/fcgi-bin/face/face_detectface'
    # 检测给定图片（Image）中的所有人脸（Face）的位置和相应的面部属性。位置包括（x
    res = requests.post(url,params).json()
    # 提取人脸信息列表
    face_list = res['data']['face_list']
    # 构造生成器,逐个返回人脸信息元组
    for item in face_list:
        yield (item['gender'],item['x'],item['y'],item['width'],item['height'])

def DrawImage(filename:str):
    # 打开图像
    image = Image.open(filename)
    # 生成一个可用于画图的对象
    draw = ImageDraw.Draw(image)
    # 使用百度平台返回的人脸坐标信息在图像中人脸的位置画一个矩形框
    for _,item in enumerate(TencentOpenAi(filename)):
        # 用gender,left,top,width,height分别表示性别、人脸框左上角的横、纵坐标以及人脸框的宽度、高度
        (gender,left,top,width,height) = item
        # 根据性别定义矩形框的颜色,男性为红色,RGB模型为(255,0,0);女性为绿色(0,255,0)
        outRGB = (255,0,0) if gender > 50 else (0,255,0)
        draw.polygon([(left,top),(left+width,top),(left+width,height+top),(left,height+top)], outline=outRGB)
    # 展示图像
    image.show()

if __name__ == '__main__':
    DrawImage('********.jpeg')

    
