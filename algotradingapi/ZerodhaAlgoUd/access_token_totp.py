# -*- coding: utf-8 -*-
"""
Zerodha kiteconnect automated authentication

@author: Mayank Rasu (http://rasuquant.com/wp/)
"""

from kiteconnect import KiteConnect
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import os
from pyotp import TOTP
from selenium.webdriver.chrome.options import Options
cwd = os.chdir(r"C:\Users\LENOVO\OneDrive\Documents\A_Udeyme\ppts\Algo_trradiing\algocode")

def autologin():
    token_path = "C:/Users/LENOVO/OneDrive/Documents/A_Udeyme/ppts/Algo_trradiing/algocode/api_key.txt"
    key_secret = open(token_path,'r').read().split()
    kite = KiteConnect(api_key=key_secret[0])
    print(kite.login_url())
    option = webdriver.ChromeOptions()
    option.add_experimental_option("detach", True)

    driver = webdriver.Chrome(options=option)


    driver.get(kite.login_url())
    driver.implicitly_wait(10)
    username = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[1]/input')
    password = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[2]/input')
    username.send_keys(key_secret[2])
    password.send_keys(key_secret[3])
    driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[4]/button').click()
    pin = driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div[1]/div[2]/div/div[2]/form/div[1]/input')
    totp = TOTP(key_secret[4])
    token = totp.now()
    pin.send_keys(token)
    driver.find_element(By.XPATH,'/html/body/div[1]/div/div[2]/div[1]/div[2]/div/div[2]/form/div[2]/button').click()
    time.sleep(10)
    request_token=driver.current_url.split('request_token=')[1][:32]
    with open('C:/Users/LENOVO/OneDrive/Documents/A_Udeyme/ppts/Algo_trradiing/algocode/request_token.txt', 'w') as the_file:
        the_file.write(request_token)
    driver.quit()

autologin()

#generating and storing access token - valid till 6 am the next day
request_token = open("C:/Users/LENOVO/OneDrive/Documents/A_Udeyme/ppts/Algo_trradiing/algocode/request_token.txt",'r').read()
key_secret = open("C:/Users/LENOVO/OneDrive/Documents/A_Udeyme/ppts/Algo_trradiing/algocode/api_key.txt",'r').read().split()
kite = KiteConnect(api_key=key_secret[0])
data = kite.generate_session(request_token, api_secret=key_secret[1])
with open('C:/Users/LENOVO/OneDrive/Documents/A_Udeyme/ppts/Algo_trradiing/algocode/access_token.txt', 'w') as file:
        file.write(data["access_token"])




# =============================================================================
# C:/Users/LENOVO/OneDrive/Documents/A_Udeyme/ppts/Algo_trradiing/algocode/access_token.txt
# =============================================================================
