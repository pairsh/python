from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json

class Taobao:
    def __init__(self,word):
        self.word=word
        self.driver=webdriver.Edge()

    def search(self):
        try:
            self.text={"商品名称":"","价格":"", "链接":""}
            self.driver.get("https://login.taobao.com/member/login.jhtml?spm=a21bo.jianhua.754894437.1.5af92a89IASoHb&f=top&redirectURL=https%3A%2F%2Fwww.taobao.com%2F")
            wait=WebDriverWait(self.driver,100)
            wait.until(EC.presence_of_element_located((By.ID,"q")))
            self.driver.find_element(By.ID,"q").send_keys(self.word)
            self.driver.find_element(By.XPATH,"/html/body/div[2]/div/div/div[2]/div/div[1]/form/div[1]/button").click()
        except Exception:
            print("搜索出错")
        finally:
            self.driver.quit()


    def parse(self):
        try:    
            count=self.driver.find_element(By.XPATH,"/html/body/div[2]/div/div[2]/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]/div[2]/div[8]/div/span/text()[2]").text
            for l in range(1,int(count)+1):
                    self.page=BeautifulSoup(self.driver.page_source,"html.parser")
                    self.page=self.page.find("div",{"class":"Content--contentInner--QVTcU0M"})
                    links=self.page.findAll("a",{"class":"Card--doubleCardWrapper--L2XFE73"})
                    price=self.page.findAll("div",{"class":"Price--price--18-yW"})
                    name=self.page.findAll("div",{"class":"Card--title--2U9X8"})
                    for i in len(links):
                        self.text["商品名称"]=name[i].get_text()
                        self.text["价格"]=price[i].get_text()
                        self.text["链接"]=links[i].get("href")
                    self.driver.find_element(By.XPATH,"/html/body/div[2]/div/div[2]/div[1]/div[1]/div[2]/div[2]/div[1]/div[2]/div[2]/div[8]/div/button[2]/i").click()
        except Exception as e:
            print("解析出错")
            print(e)
        finally:
            self.driver.quit()
              
    def save(self):
        with open("taobao.json","w",encoding="utf-8") as f:
            f.write(json.dumps(self.text,ensure_ascii=False))
            print("保存成功")

if __name__=="__main__":
    start=Taobao("手机")
    start.search()
    start.parse()
    start.save()