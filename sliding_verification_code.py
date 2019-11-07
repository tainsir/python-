# import  requests
# import re
# session = requests.session()


from selenium import webdriver
from selenium.webdriver import ActionChains #滑动验证
from selenium.webdriver.common.by import By #按照什么方式查找，By.ID,By.CSS_SELECTOR
from selenium.webdriver.common.keys import Keys #键盘按键操作
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException,NoSuchElementException,NoSuchFrameException
import time
from PIL import Image


def get_snap(driver):
    driver.save_screenshot('snap.png')
    snap_obj = Image.open('snap.png')
    return snap_obj


def get_image(driver):
    img = driver.find_element_by_class_name('geetest_canvas_img')
    time.sleep(2)
    size = img.size
    location = img.location
    print(size,location)
    left = location['x']+74
    top = location['y']+4
    right = left + size['width']+64
    bottom = top + size['height']+39
    snap_obj = get_snap(driver)
    print(left,top,right,bottom)
    image_obj = snap_obj.crop((left, top, right, bottom))
    # image_obj.show()
    return image_obj


def get_distance(image1,image2):
    start_x=75
    threhold=60
    # print(image1.size)
    # print(image2.size)
    for x in range(start_x,image2.size[0]):
        for y in range(image2.size[1]):
            rgb1=image1.load()[x,y]
            rgb2=image2.load()[x,y]
            res1=abs(rgb1[0]-rgb2[0])
            res2=abs(rgb1[1]-rgb2[1])
            res3=abs(rgb1[2]-rgb2[2])
            if not (res1 < threhold and res2 < threhold and res3 < threhold):
                print(x-7)
                return x-7


def get_tracks(distance):
    # distance+=20
    #v=v0+a*t
    #s=v*t+0.5*a*(t**2)
    v0=0
    s=0
    t=0.2
    mid=distance*4/5
    forward_tracks=[]
    while s < distance:
        if s < mid:
            if distance>180:
                a=7
            elif distance>150:
                a=6
            else:
                a=3
        else:
            a=-3
        v=v0
        track=v*t+0.5*a*(t**2)
        track=round(track)
        v0=v+a*t
        s+=track
        forward_tracks.append(track)
    # back_tracks=[-1,-1,-1,-2,-2,-2,-3,-3,-2,-2,-1] #20
    # return {"forward_tracks":forward_tracks,'back_tracks':back_tracks}
    return {"forward_tracks":forward_tracks}


def login():
    try:
        driver = webdriver.Chrome()
        driver.get('https://passport.cnblogs.com/user/signin')
        driver.implicitly_wait(3)
        input_user = driver.find_element_by_id('input1')
        input_pwd = driver.find_element_by_id('input2')
        login_button = driver.find_element_by_id('signin')
        input_user.send_keys('--Junior')
        input_pwd.send_keys('wang.19970923')
        login_button.click()
        button = driver.find_element_by_class_name('geetest_radar_tip')
        button.click()
        image1 = get_image(driver)
        # driver.execute_script('document.getElementsByClassName("geetest_canvas_slice")[0].setAttribute("style","opacity: 1; display: none")')
        driver.execute_script('document.getElementsByClassName("geetest_canvas_fullbg")[0].setAttribute("style","opacity: 1; display: block")')
        image2 = get_image(driver)
        distance = get_distance(image1, image2)
        traks_dic = get_tracks(distance)
        slider_button = driver.find_element_by_class_name('geetest_slider_button')
        ActionChains(driver).click_and_hold(slider_button).perform()
        # 先向前移动
        q=time.time()
        forward_tracks = traks_dic["forward_tracks"]
        print(sum(forward_tracks))
        if sum(forward_tracks)>180:
            back_tracks = [-1, -2, -3, -4, -5,-5,-6,-5,-4,-2,-2, -1]
        elif sum(forward_tracks)>150:
            back_tracks = [-1, -2, -2, -3, -3,-4,-4,-5,-4,-3, -2, -1]
        else:
            back_tracks = [ -1, -2, -2, -3, -3, -3,-2,-1, -1]
        # back_tracks = traks_dic["back_tracks"]
        for forward_track in forward_tracks:
            ActionChains(driver).move_by_offset(xoffset=forward_track, yoffset=0).perform()

        # 短暂停顿，发现傻逼，移过了
        time.sleep(0.1)

        # 先向后移动
        for back_track in back_tracks:
            # print(back_track)
            ActionChains(driver).move_by_offset(xoffset=back_track, yoffset=0).perform()
        z=time.time()
        print(z-q)
        ActionChains(driver).move_by_offset(xoffset=-3, yoffset=0).perform()
        ActionChains(driver).move_by_offset(xoffset=3, yoffset=0).perform()
        time.sleep(0.2)
        ActionChains(driver).release().perform()
        time.sleep(5)
    except NoSuchElementException:
        print('没有滑动验证')
    finally:
        driver.close()




# 3、针对没有缺口的图片进行截图
# 4、点击滑动按钮，弹出有缺口的图
# 5、针对有缺口的图片进行截图
# 6、对比两张图片，找出缺口，即滑动的位移
# 7、按照人的行为行为习惯，把总位移切成一段段小的位移
# 8、按照位移移动
if __name__ == '__main__':
    login()



