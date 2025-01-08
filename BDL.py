import requests
import time
import json
import os
import subprocess
import fake_useragent
import math
import warnings
from typing import List,Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BDL:
    def __init__(self,BV):
        ua=fake_useragent.UserAgent()
        self.bvid = BV
        self.aid=None
        self.cid=None
        self.title=None
        self.requests_cookiies=None
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            'Referer': '',}

    def bv_to_aid(self):
        """非必须，经测试，可直接使用bv号获取cid。"""
        BvNo1 = self.bvid[2:]
        keys = {
            '1': '13', '2': '12', '3': '46', '4': '31', '5': '43', '6': '18', '7': '40', '8': '28', '9': '5',
            'A': '54', 'B': '20', 'C': '15', 'D': '8', 'E': '39', 'F': '57', 'G': '45', 'H': '36', 'J': '38', 'K': '51',
            'L': '42', 'M': '49', 'N': '52', 'P': '53', 'Q': '7', 'R': '4', 'S': '9', 'T': '50', 'U': '10', 'V': '44',
            'W': '34', 'X': '6', 'Y': '25', 'Z': '1',
            'a': '26', 'b': '29', 'c': '56', 'd': '3', 'e': '24', 'f': '0', 'g': '47', 'h': '27', 'i': '22', 'j': '41',
            'k': '16', 'm': '11', 'n': '37', 'o': '2',
            'p': '35', 'q': '21', 'r': '17', 's': '33', 't': '30', 'u': '48', 'v': '23', 'w': '55', 'x': '32',
            'y': '14', 'z': '19'
        }
        BvNo2 = []
        for index, ch in enumerate(BvNo1):
            BvNo2.append(int(str(keys[ch])))
        BvNo2[0] = int(BvNo2[0] * math.pow(58, 6))
        BvNo2[1] = int(BvNo2[1] * math.pow(58, 2))
        BvNo2[2] = int(BvNo2[2] * math.pow(58, 4))
        BvNo2[3] = int(BvNo2[3] * math.pow(58, 8))
        BvNo2[4] = int(BvNo2[4] * math.pow(58, 5))
        BvNo2[5] = int(BvNo2[5] * math.pow(58, 9))
        BvNo2[6] = int(BvNo2[6] * math.pow(58, 3))
        BvNo2[7] = int(BvNo2[7] * math.pow(58, 7))
        BvNo2[8] = int(BvNo2[8] * math.pow(58, 1))
        BvNo2[9] = int(BvNo2[9] * math.pow(58, 0))
        sum = 0
        for i in BvNo2:
            sum += i
        sum -= 100618342136696320
        temp = 177451812
        aid=sum^temp
        if aid<0:
            print("aid<0,请检查BV号是否正确。")
            time.sleep(3)
            exit()
        else:
            self.aid=aid
            print("aid获取成功,aid={}".format(self.aid))

class BDL_Video(BDL):#流程：BV->(aid->)cid->【参数（page,quality）】下载视频 ->转码
    def __init__ (self,BV):
        super().__init__(BV)
        super().bv_to_aid()
    
    def get_cid(self,page):
        try:    
            req1 = requests.get(url="https://api.bilibili.com/x/player/pagelist?bvid={}&jsonp=jsonp".format(self.bvid),headers=self.headers)
            rep1 = json.loads(req1.text)
            self.cid = rep1["data"][page - 1]["cid"]
            self.title = rep1["data"][page - 1]["part"]
        except Exception:
             print("获取cid失败，请检查网络连接。")
             time.sleep(2)
             exit()
        

    def save_video(self,qua):#16为360p,32为480p,64为720p,80为1080P 112, 80, 64, 32, 16
        try:    
            req = requests.get(
                url="https://api.bilibili.com/x/player/playurl?bvid={}&cid={}&qn={}&type=&otype=json".format(self.bvid,self.cid, qua),
                headers=self.headers)
            rep = json.loads(req.text)
            content_url = rep["data"]["durl"][0]["url"]
            self.headers["referer"] = "https://www.bilibili.com/av{}".format(self.aid)
            r = requests.get(url=content_url, headers=self.headers,stream=True)
            with open("{}.flv".format(self.title), "wb") as f:
                for data in r.iter_content(1024):
                    f.write(data)
        except Exception:
            print("下载失败，请检查网络连接。")
            time.sleep(2)
            exit()

    def trans(self):
        try:
            subprocess.run("ffmpeg -i {}.flv {}.mp4".format(self.title,self.title),shell=True)
            os.remove("{}.flv".format(self.title))
            print("转码完成:{}.mp4".format(self.title))
            time.sleep(3)
            exit()
        except Exception:
            print("转换失败，请检查ffmpeg是否安装正确。")
            time.sleep(3)
            exit()
    
    def start(self,page,qua):
        try:    
            self.get_cid(page)
            self.save_video(qua)
        #self.trans()
        except Exception:
            print("下载失败，请检查网络连接。")
            time.sleep(2)
            exit()
                 

class BDL_anime(BDL):#流程：medai_id->season_id->epid->【参数（quality）】下载视频 ->转码
    sum=0
    def __init__(self,epid:List[int]=None,media_id:int=None):
        super().__init__(None)
        self.epid=epid
        self.season_id=None
        self.media_id=media_id
        if epid==None and media_id==None:
            print("epid和media_id不能同时为空")
            time.sleep(2)
            exit()
        elif epid!=None and media_id!=None:
            print("epid和media_id只能有一个不为空")
            time.sleep(2)
            exit()
        elif epid!=None and media_id==None:
            warnings.warn("不建议使用epid参数，请使用media_id参数")
        else:
            print("程序初始化成功。") 


    def get_cookies(self):
        try:
            user=input("请输入账号：")
            password=input("请输入密码：")
            driver = webdriver.Edge()
            driver.get("https://passport.bilibili.com/login")
            wait=WebDriverWait(driver,20)
            wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="app-main"]/div/div[2]/div[3]/div[2]/div[1]/div[1]/input')))
            if not user and not password:
                warnings.warn("账号密码不能为空，将使用扫码登录")
            elif not user or not password:
                print("账号密码不能为空,请重新输入。")
                time.sleep(2)
                self.get_cookies()
            else:
                driver.find_element(By.XPATH,'//*[@id="app-main"]/div/div[2]/div[3]/div[2]/div[1]/div[1]/input').send_keys(user)
                driver.find_element(By.XPATH,'//*[@id="app-main"]/div/div[2]/div[3]/div[2]/div[1]/div[3]/input').send_keys(password)
                driver.find_element(By.XPATH,'//*[@id="app-main"]/div/div[2]/div[3]/div[2]/div[2]/div[2]').click()
            wait=WebDriverWait(driver,60)
            wait.until(EC.presence_of_element_located((By.XPATH,'//*[@id="i_cecream"]/div[2]/div[1]/div[2]/div[2]/a/img')))
            cookies=driver.get_cookies()
            self.requests_cookies={cookie['name']:cookie['value'] for cookie in cookies}
            print("cookies获取成功。")
        except Exception:
            print("登录失败，请检查账号密码是否正确。")
            time.sleep(2)
            exit()
        finally:
            driver.quit()

    def get_saeon_id_and_epids(self):
        try:
            req1=requests.get("https://api.bilibili.com/pgc/review/user?media_id={}".format(self.media_id),headers=self.headers,cookies=self.requests_cookies)
            rep1=json.loads(req1.text)
            self.season_id=rep1["result"]["media"]["season_id"]
            index=rep1["result"]["media"]["new_ep"]["index"]
            req2=requests.get("https://api.bilibili.com/pgc/view/web/ep/list?season_id={}".format(self.season_id),headers=self.headers,cookies=self.requests_cookies)
            rep2=json.loads(req2.text)
            self.epid=(rep2["result"]["episodes"][i]["id"] for i in range(int(index)))
            self.title=(rep2["result"]["episodes"][i]["long_title"] for i in range(int(index)))
            print("season_id和epid获取成功。")
        except Exception:
            print("获取season_id和epid失败，请检查media_id是否正确。")
            time.sleep(2)
            exit()

    def save(self,qua,i,epid,title):
        if sum==5:
            print("达到最大下载次数，请稍后再试。")
            time.sleep(2)
            exit()
        self.headers["Referer"]="https://www.bilibili.com/bangumi/play/ep{}".format(epid[i])
        req=requests.get("https://api.bilibili.com/pgc/player/web/playurl?qn={}&ep_id={}".format(qua,epid[i]),headers=self.headers,cookies=self.requests_cookies)
        rep=json.loads(req.text)
        try:
            url=rep["result"]["video_info"]["durl"][0]["url"]
        except Exception:
            url=rep["result"]["durl"][0]["url"]
        print("正在下载：{}".format(title[i]))
        #try:
            #with requests.get(url,stream=True,headers=self.headers,cookies=self.requests_cookies) as r:
                #with open("{}.flv".format(title[i]),"wb") as f:
                    #for data in r.iter_content(1024):
                        #t2=time.time()
                        #f.write(data)
                        #size=len(1024)
                        #speed=size/(t2-t1)
                        #print("下载速度：{:.2f}KB/s".format(speed))
                        #exit()
        with requests.get(url,stream=True,headers=self.headers,cookies=self.requests_cookies) as r:
            with open("{}.flv".format(i+1),"wb") as f:
                for data in r.iter_content(1024):
                    t1=time.time()
                    f.write(data)
                    size=1024
                    t2=time.time()
                    speed=size/(t2-t1)
                    print("下载速度：{:.2f}KB/s".format(speed))
        print("{} 下载完成 ".format(title[i]))
        

    def saves(self,qua):
        try:
            epid=list(self.epid)
            title=list(self.title)
            for i in range(len(epid)):
                self.save(qua,i,epid,title)
        except requests.exceptions.Timeout:
            self.saves(qua,i,epid,title)
            sum+=1
        except Exception as e:
            print("下载失败，请检查网络连接。")
            print(e)
            with open("log.txt") as f:
                f.write(epid[i-1:])
            print("已将未下载完成的epid写入log.txt，请重新运行程序。")
            time.sleep(2)
            exit()

    def trans(self):
        try:
            for i in range(len(list(self.epid))):
                subprocess.run("ffmpeg -i {}.flv -c:v libx264 -c:a aac {}.mp4".format(i+1,list(self.epid)[i]),shell=True)
                os.remove("{}.flv".format(i+1))
                print("转码完成：{}.mp4".format(list(self.epid)[i]))
                time.sleep(2)
                exit()
        except Exception:
            print("转码失败，请检查ffmpeg是否安装。")
            time.sleep(2)
            exit()

    def start(self,qua):
        try:
            if not self.epid:
                self.get_cookies()
                self.get_saeon_id_and_epids()
                warnings.warn("此方法不能正常获取标题名，将使用epid作为文件名。")
                epid=list(self.epid)
                self.save(qua,0,epid,epid)
                #self.trans()
            else:
                self.get_cookies()
                self.get_saeon_id_and_epids()
                self.saves(qua)
                #self.trans()
        except Exception:
            print("程序运行失败，请重新运行。")
            time.sleep(2)
            exit()
        
def start():
    a=int(input("0：番剧，1：视频 "))
    if a==0:
        media_id=input("请输入番剧的media_id：")
        if not media_id:
            print("media_id不能为空,请输入epid")
            epid=int(input("请输入epid："))
            b=BDL_anime(epid=epid)
        else:    
            b=BDL_anime(media_id=media_id)
        qua=int(input("请输入画质：16为360p,32为480p,64为720p,80为1080P "))
        match qua:
            case 16:
                pass
            case 32:
                pass
            case 64:
                pass
            case 80:
                pass
            case _:
                print("请输入正确的画质")
                time.sleep(2)
                start()
        b.start(qua)
    elif a==1:
        BV=input("请输入视频的BV：例：BV1XJ411w7Gq ")
        page=int(input("请输入页数："))
        qua=int(input("请输入画质：16为360p,32为480p,64为720p,80为1080P "))
        match qua:
            case 16:
                pass
            case 32:
                pass
            case 64:
                pass
            case 80:
                pass
            case _:
                print("请输入正确的画质")
                time.sleep(2)
                start()
        b=BDL_Video(BV)
        b.start(page=page,qua=qua)

start()