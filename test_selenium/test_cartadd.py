import unittest
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import HtmlTestRunner  

class TestRegistroLogin(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        options = Options()
        service = FirefoxService(executable_path='C:/Users/Martto/Documents/Selenium tester/geckodriver.exe')
        cls.driver = webdriver.Firefox(service=service, options=options)
        cls.wait = WebDriverWait(cls.driver, 10)
        cls.base_url = "http://127.0.0.1:8000"

    def test_registro_y_login(self):
        usuario = f"testuser_{int(time.time())}"
        password = "TestPass123"

        # Registrar usuario
        self.driver.get(f"{self.base_url}/register")
        self.wait.until(EC.presence_of_element_located((By.NAME, "username")))

        self.driver.find_element(By.NAME, "username").send_keys(usuario)
        self.driver.find_element(By.NAME, "password1").send_keys(password)
        self.driver.find_element(By.NAME, "password2").send_keys(password)
        self.driver.find_element(By.TAG_NAME, "button").click()
        time.sleep(2)

        # Login usuario
        self.driver.get(f"{self.base_url}/accounts/login/")
        self.wait.until(EC.presence_of_element_located((By.NAME, "username")))

        self.driver.find_element(By.NAME, "username").send_keys(usuario)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.TAG_NAME, "button").click()
        time.sleep(2)

        self.assertIn("Cerrar sesión", self.driver.page_source)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

if __name__ == "__main__":
    unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='reports'), verbosity=2)
