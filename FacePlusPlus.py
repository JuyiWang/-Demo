# 访问API接口
import requests
# 导入Pillow库
from PIL import Image,ImageDraw
# 定义常量
key = "********"
secret = "********"

def FaceppAI(filepath):
    # 调用URL
    http_url = "https://api-cn.faceplusplus.com/facepp/v3/detect"
    # 定义文件
    files = {"image_file": open(filepath, "rb")}
    # 定义参数
    data = {"api_key":key, "api_secret": secret,'return_attributes':'gender'}
    # 调用API,调用方式为post
    response = requests.post(http_url, data=data, files=files)
    # 将返回值转化为字典
    req_dict = response.json()
    # 读取人脸信息列表
    face_list = req_dict['faces']
    # 对于每个人脸读取位置信息
    for item in face_list:
        gender = item['attributes']['gender']['value']
        left = item['face_rectangle']['left']
        top = item['face_rectangle']['top']
        width = item['face_rectangle']['width']
        height = item['face_rectangle']['height']
        # 构造迭代器
        yield (gender,left,top,width,height)
 
def DrawImage(filename:str):
    # 打开图像
    image = Image.open(filename)
    # 生成一个可用于画图的对象
    draw = ImageDraw.Draw(image)
    # 使用百度平台返回的人脸坐标信息在图像中人脸的位置画一个矩形框
    for _,item in enumerate(FaceppAI(filename)):
        # 用gender,left,top,width,height分别表示性别、人脸框左上角的横、纵坐标以及人脸框的宽度、高度
        (gender,left,top,width,height) = item
        # 根据性别定义矩形框的颜色,男性为红色,RGB模型为(255,0,0);女性为绿色(0,255,0)
        outRGB = (255,0,0) if gender == 'Male' else (0,255,0)
        draw.polygon([(left,top),(left+width,top),(left+width,height+top),(left,height+top)], outline=outRGB)
    # 展示图像
    image.show()
 
if __name__ == "__main__":
    DrawImage('********.jpeg')
