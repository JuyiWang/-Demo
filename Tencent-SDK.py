# 导入腾讯SDK 
from tencentcloud.common import credential              
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
# 导入对应产品模块的client models。
from tencentcloud.iai.v20180301 import iai_client, models 
# 导入base64库,将图片转码为base64格式
import base64
# 导入json库
import json
# 导入Pillow库
from PIL import Image,ImageDraw

# 定义常量
APP_ID = '********'
APP_KEY = '********'

def TencentFaceDetect(filepath:str):
    img = open(filepath,'rb')
    # 对图像进行base64编码
    base64_data = base64.b64encode(img.read())
    # 对原图像进行base64解码,得到所处理图像
    image = base64_data.decode()
    # 实例化一个认证对象，入参需要传入腾讯云账户secretId，secretKey
    cred = credential.Credential(APP_ID, APP_KEY) 
    # 实例化一个http选项，可选的，没有特殊需求可以跳过。
    httpProfile = HttpProfile()
    # 指定接入地域域名(默认就近接入)
    httpProfile.endpoint = "iai.tencentcloudapi.com"
    # 实例化一个client选项，可选的，没有特殊需求可以跳过。
    clientProfile = ClientProfile()
    clientProfile.httpProfile = httpProfile
    # 实例化请求产品的client对象，clientProfile是可选的。
    client = iai_client.IaiClient(cred, "ap-beijing")#, clientProfile) 
    # 实例化一个实例信息查询请求对象,每个接口都会对应一个request对象。
    req = models.DetectFaceRequest()
    # 定义参数。 支持以标准json格式的string来赋值请求参数的方式。
    params = {"MaxFaceNum":10,"Image":image,"NeedFaceAttributes":1}
    req.from_json_string(json.dumps(params))
    # 通过client对象调用DetectFace方法发起请求。
    resp = client.DetectFace(req) 
    # 输出json格式的字符串回包
    out = resp.to_json_string()
    # 将json格式返回值转为字典
    face_dict = json.loads(out)
    # 遍历人脸信息列表，返回性别、位置等信息
    for item in face_dict['FaceInfos']:
        yield (item['FaceAttributesInfo']['Gender'],item['X'],item['Y'],item['Width'],item['Height'])

def DrawImage(filename:str):
    # 打开图像
    image = Image.open(filename)
    # 生成一个可用于画图的对象
    draw = ImageDraw.Draw(image)
    for _,item in enumerate(TencentFaceDetect(filename)):
        # 用gender,left,top,width,height分别表示性别、人脸框左上角的横、纵坐标以及人脸框的宽度、高度
        (gender,left,top,width,height) = item
        # 根据性别定义矩形框的颜色,男性为红色,RGB模型为(255,0,0);女性为绿色(0,255,0)
        outRGB = (255,0,0) if gender > 50 else (0,255,0)
        # 使用人工智能平台返回的人脸坐标信息在图像中人脸的位置画一个矩形框
        draw.polygon([(left,top),(left+width,top),(left+width,height+top),(left,height+top)], outline=outRGB)
    # 展示图像
    image.show()

if __name__ == '__main__':
    DrawImage('test.jpeg')
