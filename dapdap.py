from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import sqlite3

EXTENSION_ID = "nkbihfbeogaeaoehlefnkodbefgpgknn"
WALLET_PWD = "d12345678d"

class Browser:
    def __init__(self, extension_path, proxy_server, chromederiver_path='chromedriver'):
        self.browserOption = webdriver.ChromeOptions()
        self.browserOption.add_extension(extension_path)
        self.browserOption.add_argument('--proxy-server=' + proxy_server)
        self.browserOption.add_argument('--mute-audio')
        service = webdriver.ChromeService(executable_path=chromederiver_path)
        self.browser = webdriver.Chrome(options=self.browserOption, service=service)
    
    def switch_to(self, index):
        self.browser.switch_to.window(self.browser.window_handles[index])

    def zoom(self):
        # 缩放浏览器到0.7, 由于很多页面不好点，缩小一点加载的多
        self.browser.get('chrome://settings/')
        self.browser.execute_script('chrome.settingsPrivate.setDefaultZoom(0.7);')

    def navigate(self, url):
        self.browser.get(url)
        sleep(1)

    def agree_terms(self):
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.ID, 'onboarding__terms-checkbox'))).click()

    def import_wallet(self, private_key):
        # 勾选同意协议
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.ID, 'onboarding__terms-checkbox'))).click()
        # 点击倒入私钥按钮
        self.browser.find_element(By.CSS_SELECTOR, 'button[data-testid=onboarding-import-wallet]').click()
        # 点击同意协议按钮
        self.browser.find_element(By.CSS_SELECTOR, 'button[data-testid="metametrics-i-agree"]').click()
        # 填入私钥
        for index in range(12):
            self.browser.find_element(By.ID, "import-srp__srp-word-"+str(index)).send_keys(private_key[index])
        # 点击确认按钮
        self.browser.find_element(By.CSS_SELECTOR, 'button[data-testid="import-srp-confirm"]').click()
        # 点击密码输入框
        self.browser.find_element(By.CSS_SELECTOR, "input[data-testid='create-password-new']").send_keys(WALLET_PWD)
        self.browser.find_element(By.CSS_SELECTOR, "input[data-testid='create-password-confirm']").send_keys(WALLET_PWD)
        self.browser.find_element(By.CSS_SELECTOR, "input[data-testid='create-password-terms']").click()
        # 点击确定导入
        self.browser.find_element(By.CSS_SELECTOR, "button[data-testid='create-password-import']").click()

        sleep(2)
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='onboarding-complete-done']"))).click()
        self.browser.find_element(By.CSS_SELECTOR, "button[data-testid='pin-extension-next']").click()
        self.browser.find_element(By.CSS_SELECTOR, "button[data-testid='pin-extension-done']").click()
        WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='popover-close']"))).click()


    def input_private_key(self, keys):
        for index in range(12):
            self.browser.find_element(By.ID, "import-srp__srp-word-"+str(index)).send_keys(keys[index])
        # 点击确认按钮
        self.browser.find_element(By.CSS_SELECTOR, 'button[data-testid="import-srp-confirm"]').click()

    def connected_wallet(self):
        # 点击链接钱包
        # self.browser.maximize_window() # 浏览器窗口最大化，不然点不到
        connect_buttons = self.browser.find_elements(By.XPATH, "//button[contains(text(), 'Connect Wallet')]")
        if len(connect_buttons) == 0:
            return
        connect_buttons[0].click()
        sleep(1)


    def connect_wallet(self):
        # 点击链接钱包
        # self.browser.maximize_window() # 浏览器窗口最大化，不然点不到
        self.browser.find_element(By.XPATH, "//button[contains(text(), 'Connect Wallet')]").click()

        # 加载影子节点
        showShadowRoot = self.browser.find_element(By.CSS_SELECTOR, "onboard-v2").get_property('shadowRoot')
        showShadowRoot.find_elements(By.CSS_SELECTOR,".wallet-button-container button")[0].click() # 第一个是metamask钱包
        sleep(1)
        # 打开metamask的tab页面，否则会调用插件的弹窗，不好控制
        self.switch_to(1)
        # browser.switch_to.window(browser.window_handles[1])
        self.browser.get("chrome-extension://{}/popup.html".format(EXTENSION_ID))
        WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='page-container-footer-next']"))).click()
        WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='page-container-footer-next']"))).click()
        sleep(1.5)
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='popover-close']"))).click()
        self.browser.close()
        self.switch_to(0)


    def earn_score(self):
        # 点击领取积分
        self.browser.get("https://www.dapdap.net/")
        sleep(1)
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Earn Rewards')]"))).click()
    
    def switch_earn_score(self):
        url = "https://www.dapdap.net/quest/leaderboard"
        self.browser.get(url)
    
    def back(self):
        self.browser.back()

    # 签到
    def sign_in(self):
        # 去签到
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".sc-54f168e4-0"))).click()
        # 签到
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".sc-80d397d3-8"))).click()
        # 点击分享
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Invite Link')]"))).click()
    
    # 点击搜索
    def click_search(self):
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.ID, "nav-top-search"))).send_keys("dodo")
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@data-bp='3001-005']"))).click()
        sleep(2)
        self.browser.back()
        
    def explore_linea(self):
        self.browser.get("https://www.dapdap.net/network/linea")
        #Explore linea
        sleep(2)
        dapps = ["https://www.dapdap.net/dapps-details?dapp_id=111", "https://www.dapdap.net/dapps-details?dapp_id=7","https://www.dapdap.net/dapps-details?dapp_id=92"]
        for i, dapp in enumerate(dapps):
            self.browser.get(dapp)
            sleep(2)
            WebDriverWait(self.browser, 5).until(lambda x: x.find_element(By.CSS_SELECTOR,".fxOwHV svg")).click()
            sleep(1)

    def play_game(self):
        # 移动屏幕
        flip_match_position = self.browser.find_element(By.CSS_SELECTOR, ".fdguFR")
        self.browser.execute_script("arguments[0].scrollIntoView(true);", flip_match_position)
        sleep(5)

        # 点击开玩
        while int(self.browser.find_element(By.CSS_SELECTOR, ".cdKzPR").text) > 0:
            # 点击开始按钮
            WebDriverWait(self.browser, 10).until(lambda x: x.find_element(By.CSS_SELECTOR,".iiaOmS")).click()
            sleep(2)
            boxes = self.browser.find_elements(By.CSS_SELECTOR, ".fKfqQB")
            for i in range(1, 10):
                for ii, box in enumerate(boxes):
                    image = box.find_element(By.CSS_SELECTOR, ".back-face").get_attribute("src")
                    if image.find(f"{i}.jpg") > -1:
                        print(f"image: {image}, position: {ii+1}")
                        box.click()
                        sleep(0.2)

            try:
                # 点击close按钮
                WebDriverWait(self.browser, 10).until(lambda x: x.find_element(By.CSS_SELECTOR,".hdtiHS")).click()
                # self.browser.find_element(By.CSS_SELECTOR, ".hdtiHS").click()
            except Exception as e:
                print(f"close error: {e}")
                pass
        sleep(2)

    def odyssey_match(self):
        sleep(60)
        self.browser.get("https://www.dapdap.net/odyssey/home?id=2")
        sleep(2)
        self.play_game()
        # self.explore_linea()
        # sleep(2)
        # self.browser.get("https://www.dapdap.net/odyssey/home?id=2")
        # sleep(2)
        # # Enter secret password
        # social_position = self.browser.find_element(By.CSS_SELECTOR, ".kWBNnk")
        # self.browser.execute_script("arguments[0].scrollIntoView(true);", social_position)
        # sleep(5)
        # try:
        #     # input_secret = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located(By.CSS_SELECTOR, ".kVBcWS"))
        #     input_secret = self.browser.find_element(By.CSS_SELECTOR, ".kVBcWS")
        #     input_secret.send_keys("DapDap X Linea")
        #     self.browser.find_element(By.CSS_SELECTOR, ".hfAkLw").click()
        # except Exception as e:
        #     print(f"enter secret password error: {e}")
        #     pass

        # sleep(2)
        # # visit the linea
        # try:
        #     visit =self.browser.find_element(By.XPATH, "//div[text()='Visit the Linea network page']")
        #     visit.click()
        #     sleep(2)
        #     self.switch_to(1)
        #     sleep(1.5)
        #     self.browser.close()
        #     self.switch_to(0)
        #     visit.find_element(By.CSS_SELECTOR, ".cqRgKD").click()
        # except Exception as e:
        #     print(f"visit linea error: {e}")
        #     pass

        # # Start
        # flip_match_position = self.browser.find_element(By.CSS_SELECTOR, ".fdguFR")
        # self.browser.execute_script("arguments[0].scrollIntoView(true);", flip_match_position)
        # sleep(1)

        # # get enegy number
        # enegy_number = self.browser.find_element(By.CSS_SELECTOR, ".cdKzPR").text
        # print(f"enegy number: {enegy_number}")

        # self.play_game()

        try:
            # 点击啊claim按钮
            self.browser.find_element(By.CSS_SELECTOR, ".goOIkB").click()
            sleep(1)
        except Exception as e:
            print(f"claim error {e}")
            pass
        sleep(20)

    # 探索Base页面
    def explore(self, base_url, base_projects):
        # https://www.dapdap.net/quest/detail?id=29
        self.browser.get(base_url)
        sleep(1.5)
        # 点击跳转浏览
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Explore the Base homepage on DapDap to discover more about Base')]"))).click()
        sleep(7)
        self.back()
        sleep(2)
        # base_projects = ["https://www.dapdap.net/dapps-details?dapp_id=74", "https://www.dapdap.net/dapps-details?dapp_id=52", "https://www.dapdap.net/dapps-details?dapp_id=39"]
        for e in base_projects[:3]:
            self.browser.get(e)
            sleep(1)
            # 点击收藏
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='sc-5df30767-3 fxOwHV']"))).click()
            sleep(1)
            # browser.back()
        

        self.browser.get(base_url)
        sleep(2)

        
    def scan_bitget(self, bitget_url):
        # url="https://www.dapdap.net/quest/detail?id=35"
        # 浏览bitget页面
        self.browser.get(bitget_url)
        sleep(1)
        self.connected_wallet()
        sleep(1)
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Visit the Bitget download page and download the Bitget wallet.')]"))).click()
        sleep(2)
        self.switch_to(1)
        self.browser.close()
        self.switch_to(0)
        sleep(1)
        self.switch_earn_score()

    def spin_game(self, game_url):
        sleep(40)
        self.browser.get(game_url)
        sleep(3.5)
        self.browser.refresh()
        sleep(5)

        ele1 = self.browser.find_element(By.XPATH, "//div[@class='sc-a2aeaff6-4 fNAbPH']")
        self.browser.execute_script("arguments[0].scrollIntoView();", ele1)
        # self.browser.execute_script("window.scrollTo(0, 800);")
        sleep(2)
        for i in range(200):
            sleep(1.5)
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='sc-a2aeaff6-23 XXEhS']"))).click()
            WebDriverWait(self.browser, 15).until(EC.presence_of_element_located((By.XPATH, "//div[@class='sc-e10d8647-2 jmgyFp']"))).click()

        sleep(1)
        # 点击提取
        WebDriverWait(self.browser, 15).until(EC.presence_of_element_located((By.XPATH, "//div[@class='sc-a2aeaff6-20 hzciMW']"))).click()
        sleep(2)


    # 游戏
    def scan_game(self, game_url):
        # url = "https://www.dapdap.net/quest/detail?id=45"
        self.browser.get(game_url)
        # 点击收藏
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='sc-5df30767-3 fxOwHV']"))).click()
        sleep(1)
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Enter Odyssey and enjoy gaming')]"))).click()
        sleep(1.5)
        self.switch_to(1)

        sleep(3.5)
        ele = self.browser.find_element(By.XPATH, "//div[@class='sc-a2aeaff6-18 fUCWfF']")
        self.browser.execute_script("arguments[0].scrollIntoView();", ele)
        # self.browser.execute_script("window.scrollTo(0, 1400);")
        sleep(2)

        will_scan = WebDriverWait(self.browser, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='sc-d8f42075-0 emLmJW']")))
        for i in range(5):
            will_scan[i].click()
            sleep(2)
            self.switch_to(2)
            sleep(1.5)
            self.browser.close()
            self.switch_to(1)
        
        self.browser.refresh()

        sleep(1)
        ele1 = self.browser.find_element(By.XPATH, "//div[@class='sc-a2aeaff6-4 fNAbPH']")
        self.browser.execute_script("arguments[0].scrollIntoView();", ele1)
        # self.browser.execute_script("window.scrollTo(0, 800);")
        sleep(2)
        for i in range(11):
            sleep(1.5)
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='sc-a2aeaff6-23 XXEhS']"))).click()
            WebDriverWait(self.browser, 15).until(EC.presence_of_element_located((By.XPATH, "//div[@class='sc-e10d8647-2 jmgyFp']"))).click()

        sleep(1)
        # 点击提取
        WebDriverWait(self.browser, 15).until(EC.presence_of_element_located((By.XPATH, "//div[@class='sc-a2aeaff6-20 hzciMW']"))).click()
        sleep(2)

        self.browser.close()
        self.switch_to(0)
        self.switch_earn_score()
    
    def do_claim(self, info):
        sleep(1)

    def claim(self, profile_url):
        self.browser.get(profile_url)


        infos = ["Explore Base on DapDap", "Explore DapDap Odyssey Vol. 1", "Visit Bitget Wallet", "Like Your Favorite dApps and Quests", "Check-In And Invite Friends On DapDap!", "Discover With Search: Unleash What You Seek!"]
        for info in infos:
            sleep(1)
            self.browser.execute_script("window.scrollTo(0, 400);")
            sleep(1)

            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '{}')]".format(info)))).click()
            sleep(1)
            # 点击提取
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Claim')]"))).click()
            self.back()
            sleep(2)
            self.browser.execute_script("window.scrollTo(0, 400);")
        
        total_pts = WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='sc-6143faca-13 cGZnhM']"))).text
        return int(total_pts.split(" ")[0])



def do(private_key):
    browser = Browser(
        '/Users/lele/develop/Selenium/dapdap_selenium/metamask.11.10.crx', 
        'http://127.0.0.1:1087',
        '/Users/lele/develop/Selenium/chromedriver/chromedriver'
        )

    # 缩放浏览器到0.7
    browser.zoom()

    # 主账户
    #browser.navigate("https://www.dapdap.net/referral/e5be34")
    # 次账户
    browser.navigate("https://www.dapdap.net/referral/c33d56")
    browser.switch_to(1)

    browser.import_wallet(private_key)
    browser.switch_to(0)
    sleep(3)
    # 点击链接钱包按钮
    browser.connect_wallet()
    sleep(1)
    # 奥德赛游戏
    browser.odyssey_match()
    # 转轮游戏
    # browser.spin_game("https://www.dapdap.net/odyssey/home?id=1")
    # 进入赚钱页面
    '''
    browser.earn_score()
    # 签到
    browser.sign_in()
    browser.back()
    sleep(1)
    # 浏览游戏
    browser.scan_game("https://www.dapdap.net/quest/detail?id=45")
    # 浏览bigget页面
    browser.scan_bitget("https://www.dapdap.net/quest/detail?id=35")
    # 探索Base页面
    base_projects = ["https://www.dapdap.net/dapps-details?dapp_id=74", "https://www.dapdap.net/dapps-details?dapp_id=52", "https://www.dapdap.net/dapps-details?dapp_id=39"]
    browser.explore("https://www.dapdap.net/quest/detail?id=29", base_projects)
    sleep(1)
    browser.click_search()
    return browser.claim("https://www.dapdap.net/profile")
    '''


if __name__ == '__main__':
    connection = sqlite3.connect('dapdap_1.db')
    cursor = connection.cursor()

    for i in range(1,2):
        #for i in range(1,30000):
        # 选择一个未使用过的wallet
        cursor.execute('''
        SELECT * FROM wallet WHERE used = 0 LIMIT 1
        ''')
        wallet = cursor.fetchone()
        cursor.execute('''
        UPDATE wallet SET used = 1 WHERE id = ?
        ''', (wallet[0],))
        connection.commit()
        mnemonic = wallet[1].strip().split(" ")

        
        mnemonic = ['ice','wedding','grant', 'flame', 'used', 'great', 'deny', 'make', 'nasty', 'club', 'exotic', 'health']

        # try:
            # pts = do(mnemonic)
            # cursor.execute('''
            # UPDATE wallet SET used = ? WHERE id = ?
            # ''', (pts, wallet[0]))
            # connection.commit()
            # print("total_pts: ", pts)
        # except Exception as e:
            # print("error: ", e)
            # print("id: ", wallet[0], "mnemonic: ", mnemonic)
            # sleep(2)
            # continue

        pts = do(mnemonic)
        # cursor.execute('''
        # UPDATE wallet SET used = ? WHERE id = ?
        # ''', (pts, wallet[0]))
        # connection.commit()
        # print("total_pts: ", pts)

        # print("success done: ", i, "id: ", wallet[0], " mnemonic: ", mnemonic)
        sleep(5)

    cursor.close()
    connection.close()
    print("done all")

