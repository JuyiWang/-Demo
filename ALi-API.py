import hmac                             # 导入hmac库
import hashlib                          # 导入hashilib库
import json                             # 导入json库
import base64                           # 导入base64库
import datetime                         # 导入datetime库
from urllib.parse import urlparse       # 导入urlparse
import http.client                      # 导入Client
from PIL import Image,ImageDraw         # 导入Pillow库

# 定义常量
API_ID = '********'
API_KEY = '********'

# 计算MD5+BASE64
def getcode(bodyData):
    # 定义md5加密方法
    md5 = hashlib.md5()
    # 对body内容进行加密
    md5.update(bodyData.encode("utf-8"))
    md5str = md5.digest()
    # 将加密后的内容进行BASE64编码 
    b64str = base64.b64encode(md5str)
    return b64str.decode(encoding='utf-8')

# 计算 HMAC-SHA1
def to_sha1_base64(stringToSign, secret):
    hmacsha1 = hmac.new(secret.encode(), stringToSign.encode(), hashlib.sha1)
    return base64.b64encode(hmacsha1.digest())

def ALiFaceDetect(filename):
    # 获取当前时间
    Datetime = datetime.datetime.strftime(datetime.datetime.utcnow(), "%a, %d %b %Y %H:%M:%S GMT")
    # 打开图像
    img = open(filename,'rb')
    # 对图像进行base64编码
    base64_data = base64.b64encode(img.read())
    # 对原图像进行base64解码,得到所处理图像
    image = base64_data.decode()
    # 定义选项集合
    options = {
        # API接口地址
        'url': 'https://dtplus-cn-shanghai.data.aliyuncs.com/face/attribute',
        # 访问方式
        'method': 'POST',
        # body内容，即参数
        'body': json.dumps({"type": "1", "content": image}, separators=(',', ':')),
    }
    # 对body内容进行md5加密即BASE64编码
    body = options['body']
    bodymd5 = getcode(options['body'])
    # 解析URL
    urlPath = urlparse(options['url'])
    restUrl,path = urlPath[1],urlPath[2]
    # Signature = Base64( HMAC-SHA1( AccessSecret, UTF-8-Encoding-Of(StringToSign) ) )
    # StringToSign =HTTP-Verb + "\n" +  //GET|POST|PUT...Accept + "\n" + Content-MD5 + "\n" + //Body的MD5值放在此处Content-Type + "\n" + Date + "\n" + url
    stringToSign = 'POST' + '\n' + 'application/json' + '\n' + bodymd5 + '\n' + 'application/json' + '\n' + Datetime + '\n' + path
    # 对签名进行RFC 2104HMAC-SHA1规范加密
    signature = to_sha1_base64(stringToSign, API_KEY).decode(encoding='utf-8')
    # 签名请求格式为Authorization: Dataplus AccessKeyId:Signature
    authHeader = 'Dataplus ' + API_ID + ':' + signature
    # 公共请求头计算签名
    # 计算签名必须包含参数，Accept、Content-Type、Date的值（Content-Length不计入签名），并按顺序排列；若值不存在则以”\n”补齐
    headers = {
        'Content-Type': 'application/json',
        'Authorization': authHeader,
        'Date': Datetime,
        'Accept': 'application/json'
    }
    # 定义连接方式
    conn = http.client.HTTPSConnection(restUrl)
    # 定义连接请求
    conn.request(options['method'], path, body, headers)
    # 获取API答复
    response = conn.getresponse()
    str1 = str(response.read(), encoding = "utf-8") 
    # 将输出结果转为字典格式 
    data = eval(str1)
    conn.close()
    # 构造生成器逐个返回人脸信息
    for num in range(data['face_num']):
        yield (data['gender'][num],data['face_rect'][num*4],data['face_rect'][num*4+1]
        ,data['face_rect'][num*4+2],data['face_rect'][num*4+3])

def DrawImage(filename:str):
    # 打开图像
    image = Image.open(filename)
    # 生成一个可用于画图的对象
    draw = ImageDraw.Draw(image)
    # 使用百度平台返回的人脸坐标信息在图像中人脸的位置画一个矩形框
    for _,item in enumerate(ALiFaceDetect(filename)):
        # 用gender,left,top,width,height分别表示性别、人脸框左上角的横、纵坐标以及人脸框的宽度、高度
        (gender,left,top,width,height) = item
        # 根据性别定义矩形框的颜色,男性为红色,RGB模型为(255,0,0);女性为绿色(0,255,0)
        outRGB = (255,0,0) if gender == 1 else (0,255,0)
        draw.polygon([(left,top),(left+width,top),(left+width,height+top),(left,height+top)], outline=outRGB)
    # 展示图像
    image.show()

if __name__ == '__main__':
    DrawImage('test.jpeg')
