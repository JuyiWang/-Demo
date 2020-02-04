'''
1.注册百度AI账号,可用手机号快速注册
2.导入人脸识别AIP,pip: pip install baidu-ai 
3.百度AI中点击控制台,创建新应用获取APP_ID、API_KEY、SECRET_KEY
'''
# 导入base64库
import base64
# 导入百度AI人脸识别库
from aip import AipFace
# 导入Pillow库
from PIL import Image,ImageDraw

# 定义常量
APP_ID = '********'
API_KEY = '********'
SECRET_KEY = '********'

# 初始化AipFace对象
client = AipFace(APP_ID, API_KEY, SECRET_KEY)

def baiduAiFace(filename:str):
    # 打开图像
    f = open(filename, 'rb')
    # 对图像进行base64编码
    base64_data = base64.b64encode(f.read())
    # 对原图像进行base64解码,得到所处理图像
    image = base64_data.decode()
    # 定义图像类型
    imageType = "BASE64"
    # 定义可选参数
    options = {}
    # 定义可识别的人脸数为最大值10
    options['max_face_num'] = 10
    # 定义可选返回信息，性别gender
    options['face_field'] = 'gender'
    # 调用AIP接口,返回值类型为字典
    imageDic = client.detect(image,imageType,options=options)
    # 获取人脸信息列表
    face_list = imageDic['result']["face_list"]
    # 由人脸信息列表中提取所需性别、位置信息
    for item in face_list:
        gender = item['gender']['type']
        left = item['location']['left']
        top = item['location']['top']
        width = item['location']['width']
        height = item['location']['height']
        # 构建迭代器
        yield (gender,left,top,width,height)

def DrawImage(filename:str):
    # 打开图像
    image = Image.open(filename)
    # 生成一个可用于画图的对象
    draw = ImageDraw.Draw(image)
    # 使用百度平台返回的人脸坐标信息在图像中人脸的位置画一个矩形框
    for _,item in enumerate(baiduAiFace(filename)):
        # 用gender,left,top,width,height分别表示性别、人脸框左上角的横、纵坐标以及人脸框的宽度、高度
        (gender,left,top,width,height) = item
        # 根据性别定义矩形框的颜色,男性为红色,RGB模型为(255,0,0);女性为绿色(0,255,0)
        outRGB = (255,0,0) if gender == 'male' else (0,255,0)
        draw.polygon([(left,top),(left+width,top),(left+width,height+top),(left,height+top)], outline=outRGB)
    # 展示图像
    image.show()

if __name__ == '__main__':
    DrawImage('****.jpeg')
    
