#图形验证码生成原理,可在以后实际的项目中复用
import random
import string
# Image：一个画布
# ImageDraw：一个画笔
# ImageFont:画笔的字体
from PIL import Image,ImageDraw,ImageFont

from flask import current_app
import os

# pip install pillow

# Captcha验证码

class Captcha(object):
    # 生成几位数的验证码
    number = 4
    # 验证码图片的宽度和高度
    size = (100,30)
    # 验证码字体大小
    fontsize = 25
    # 加入干扰线的条数
    line_number = 2

    # 构建一个验证码源文本
    SOURCE = list(string.ascii_letters)
    for index in range(0, 10):
        SOURCE.append(str(index))


    #用来绘制干扰线
    @classmethod
    def __gene_line(cls,draw,width,height):
        begin = (random.randint(0, width), random.randint(0, height))
        end = (random.randint(0, width), random.randint(0, height))
        draw.line([begin, end], fill = cls.__gene_random_color(),width=2)


    # 用来绘制干扰点
    @classmethod
    def __gene_points(cls,draw,point_chance,width,height):
        chance = min(100, max(0, int(point_chance))) # 大小限制在[0, 100]
        for w in range(width):
            for h in range(height):
                tmp = random.randint(0, 100)
                if tmp > 100 - chance:
                    draw.point((w, h), fill=cls.__gene_random_color())


    # 生成随机的颜色
    @classmethod
    def __gene_random_color(cls,start=0,end=255):
        random.seed()
        return (random.randint(start,end),random.randint(start,end),random.randint(start,end))#随机的R,G,B


    # 随机选择一个字体
    @classmethod
    def __gene_random_font(cls):
        fonts = [
            'Courgette-Regular.ttf',
            'LHANDW.TTF',
            'Lobster-Regular.ttf',
            'verdana.ttf'
        ]#这几个是字体文件
        font = random.choice(fonts)
        fontpath = os.path.join(current_app.config['BASE_DIR'],'utils','captcha',font) #BASE_DIR项目根路径要在config中设置
        # return 'utils/captcha/'+font
        return fontpath


    # 用来随机生成一个字符串(包括英文和数字)
    @classmethod
    def gene_text(cls, number):
        # number是生成验证码的位数
        return ''.join(random.sample(cls.SOURCE, number))


    #生成验证码
    @classmethod
    def gene_graph_captcha(cls):
        # 验证码图片的宽和高
        width,height = cls.size
        # 创建图片
        # R：Red（红色）0-255
        # G：G（绿色）0-255
        # B：B（蓝色）0-255
        # A：Alpha（透明度）
        #image相当于一个画布
        image = Image.new('RGBA',(width,height),cls.__gene_random_color(0,100))#cls.__gene_random_color(0,100)生成随机颜色作为图片背景yans
        # 验证码的字体
        font = ImageFont.truetype(cls.__gene_random_font(),cls.fontsize)
        # 创建画笔
        draw = ImageDraw.Draw(image)
        # 生成字符串
        text = cls.gene_text(cls.number)
        # 获取字体的尺寸
        font_width, font_height = font.getsize(text) #没有getsize方法的话就把pillow降级到9.5
        # 填充字符串(把生成的字体放到有限的图片框中)
        draw.text(((width - font_width) / 2, (height - font_height) / 2),text,font= font,fill=cls.__gene_random_color(150,255))
        # 绘制干扰线
        for x in range(0, cls.line_number):
            cls.__gene_line(draw, width, height)
        # 绘制噪点
        cls.__gene_points(draw, 10, width, height)
        return (text,image)