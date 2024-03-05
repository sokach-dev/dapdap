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
    def __init__(self, extension_path, proxy_server, private_key_path):
        self.browserOption = webdriver.ChromeOptions()
        self.browserOption.add_extension(extension_path)
        self.browserOption.add_argument('--proxy-server=' + proxy_server)
        self.browser = webdriver.Chrome(options=self.browserOption)
        self.private_key_path = private_key_path
        self.private_keys = [[]]
    
    def switch_to(self, index):
        self.browser.switch_to.window(self.browser.window_handles[index])

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

        sleep(3)
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='onboarding-complete-done']"))).click()
        self.browser.find_element(By.CSS_SELECTOR, "button[data-testid='pin-extension-next']").click()
        self.browser.find_element(By.CSS_SELECTOR, "button[data-testid='pin-extension-done']").click()
        WebDriverWait(self.browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='popover-close']"))).click()

    def get_private_key(self):
        # key_file content like this
        '''
        "a" "b" "c"
        "d" "e" "f"
        '''
        with open(self.private_key_path, "r") as f:
            line = f.readlines()
            keys = []
            for l in line:
                keys.append(l.strip().split(" "))
            self.private_keys.append(keys)


    def input_private_key(self, keys):
        for index in range(12):
            self.browser.find_element(By.ID, "import-srp__srp-word-"+str(index)).send_keys(keys[index])
        # 点击确认按钮
        self.browser.find_element(By.CSS_SELECTOR, 'button[data-testid="import-srp-confirm"]').click()

    def connect_wallet(self, invite_code):
        # 点击链接钱包
        self.browser.maximize_window() # 浏览器窗口最大化，不然点不到
        self.browser.find_element(By.CSS_SELECTOR, "button[data-bp='2001-001']").click()

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
        sleep(1)
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "button[data-testid='popover-close']"))).click()
        self.switch_to(0)

        sleep(5)

        # 如果有邀请码（新用户）
        if len(self.browser.find_elements(By.CSS_SELECTOR, ".sc-fb91731b-10")) > 0:
            inputs = self.browser.find_elements(By.CSS_SELECTOR, ".sc-fb91731b-10")
            # 填写邀请码
            for index in range(6):
                inputs[index].send_keys(invite_code[index])
            self.browser.find_element(By.CSS_SELECTOR, "img[data-nimg='1']").click()
            sleep(4)
            self.switch_earn_score()
    
    def earn_score(self):
        # 点击领取积分
        self.browser.find_element(By.XPATH, "//div[contains(text(), 'Earn Rewards')]").click()
        #self.browser.find_element(By.CSS_SELECTOR, "[data-bp='20011-001']").click()
    
    def switch_earn_score(self):
        url = "https://www.dapdap.net/quest/leaderboard"
        self.browser.get(url)
    
    def back(self):
        self.browser.back()

    # 签到
    def sign_in(self, visit_cursor, visit_connection):
        # 去签到
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".sc-54f168e4-0"))).click()
        # 签到
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".sc-80d397d3-8"))).click()
        # 点击邀请好友
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Invite code')]"))).click()
        sleep(2)
        # 获取邀请码并写入文件
        codes = WebDriverWait(self.browser, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='sc-15cbb10a-7 qZDBh']")))
        for code in codes:
            visit_cursor.execute('''
            INSERT INTO visit (visit_code) VALUES (?)
            ''', (code.text,))
        visit_connection.commit()
        
    
    # 点击收藏
    # def add_favorite(self):
        # self.switch_earn_score()
        # 进入任务
        # WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-bp='100151-001']"))).click()

        # 点击刷新按钮
        #WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='sc-bbe29444-6 bcCFJQ']"))).click()
        # 点击提取
        # sleep(2)
        # WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Claim')]"))).click()
        # self.browser.back()
    
    # 点击搜索
    def click_search(self):
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.ID, "nav-top-search"))).send_keys("dodo")
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@data-bp='3001-005']"))).click()
        sleep(2)
        self.browser.back()
        
    # 探索Base页面
    def explore(self, base_url,base_projects):
        # https://www.dapdap.net/quest/detail?id=29
        self.browser.get(base_url)
        sleep(1)
        # BNS
        # WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Explore Base on DapDap')]"))).click()
        # 点击浏览
        sleep(3)
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='sc-bbe29444-4 cqppgl']"))).click()
        sleep(3)
        # browser.back()
        # sleep(1)
        # 点击收藏3个项目
        # WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Like at least three Dapps within Base')]"))).click()
        sleep(1)
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
        # 点击提取
        # WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Claim')]"))).click()

        
    def scan_bitget(self, bitget_url):
        # url="https://www.dapdap.net/quest/detail?id=35"
        # 浏览bitget页面
        self.browser.get(bitget_url)
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Visit the Bitget download page and download the Bitget wallet.')]"))).click()
        sleep(1)
        self.switch_to(1)
        self.browser.close()
        self.switch_to(0)
        # 点击刷新按钮
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='sc-bbe29444-6 bcCFJQ']"))).click()
        # 点击提取
        # sleep(2)
        # WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Claim')]"))).click()
        sleep(1)
        self.switch_earn_score()

    # 游戏
    def scan_game(self, game_url):
        # url = "https://www.dapdap.net/quest/detail?id=45"
        self.browser.get(game_url)
        # 点击收藏
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='sc-5df30767-3 fxOwHV']"))).click()
        sleep(1)
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Enter Odyssey and enjoy gaming')]"))).click()
        sleep(1)
        self.switch_to(1)
        self.browser.close()
        self.switch_to(0)
        # 点击刷新按钮
        WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[@class='sc-bbe29444-6 bcCFJQ']"))).click()
        
        sleep(2)
        # 点击提取
        # WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Claim')]"))).click()
        # sleep(1)
        self.switch_earn_score()
    
    def do_claim(self, info):
        sleep(1)

    def claim(self, profile_url):
        self.browser.get(profile_url)

        infos = ["Explore Base on DapDap", "Explore DapDap Odyssey Vol. 1", "Visit Bitget Wallet", "Like Your Favorite dApps and Quests", "Check-In And Invite Friends On DapDap!", "Discover With Search: Unleash What You Seek!"]
        for info in infos:
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '{}')]".format(info)))).click()
            sleep(1)
            # 点击提取
            WebDriverWait(self.browser, 10).until(EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Claim')]"))).click()
            self.back()
            sleep(2)


def do(private_key, visit_code, visit_cursor, visit_connection):
    browser = Browser(
        '/Users/lele/develop/Selenium/hello_selenium/metamask.11.10.crx', 
        'http://127.0.0.1:1087',
        '/Users/lele/develop/Selenium/hello_selenium/private_keys.txt'
        )
    browser.navigate("https://www.dapdap.net")
    browser.switch_to(1)
    # acoustic neutral poverty half acid return flag cat empower they arrow alarm
    # key = ["acoustic", "neutral", "poverty", "half", "acid", "return", "flag", "cat", "empower", "they", "arrow", "alarm"]

    browser.import_wallet(private_key)
    browser.switch_to(0)
    # 2e13b2
    # visite_code = ["2", "e", "1", "3", "b", "2"]
    sleep(3)
    # 点击链接钱包按钮
    browser.connect_wallet(visit_code)
    sleep(1)
    # 进入赚钱页面
    browser.earn_score()
    # 签到
    browser.sign_in(visit_cursor, visit_connection)
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
    # browser.add_favorite()
    browser.claim("https://www.dapdap.net/profile")


if __name__ == '__main__':
    connection = sqlite3.connect('dapdap.db')
    cursor = connection.cursor()
    visit_connection = sqlite3.connect('dapdap_visit.db')
    visit_cursor = connection.cursor()

    for i in range(1, 30000):
        # 选择一个未使用过的wallet
        cursor.execute('''
        SELECT * FROM wallet WHERE used = 0 LIMIT 1
        ''')
        wallet = cursor.fetchone()
        cursor.execute('''
        UPDATE wallet SET used = 1 WHERE id = ?
        ''', (wallet[0],))

        # 查找一个邀请码
        visit_cursor.execute('''
        SELECT * FROM visit WHERE used = 0 LIMIT 1
        ''')   
        visit = visit_cursor.fetchone()
        visit_cursor.execute('''
        UPDATE visit SET used = 1 WHERE id = ?
        ''', (visit[0],))
        visit_connection.commit()

        mnemonic = wallet[1].strip().split(" ")
        # abic => 'a' 'b' 'i' 'c'
        visit_code = []
        for v in visit[1].strip():
            visit_code.append(v)

        try:
            do(mnemonic, visit_code, visit_cursor, visit_connection)
        except Exception as e:
            print("error: ", e)
            print("mnemonic: ", mnemonic)
            print("visit_code: ", visit_code)
            continue

        print("done: ", i, " mnemonic: ", mnemonic, " visit_code: ", visit_code)
        sleep(2)

    cursor.close()
    connection.close()

    visit_cursor.close()
    visit_connection.close()



    sleep(550)

