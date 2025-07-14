import unittest
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

base_url = "http://127.0.0.1:8000"

class TestRegistroLogin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        options = Options()
        cls.service = FirefoxService(executable_path='C:/Users/Martto/Documents/Selenium tester/geckodriver.exe')
        cls.driver = webdriver.Firefox(service=cls.service, options=options)
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_registro_y_login(self):
        username = f"usuario_test_{int(time.time())}"
        password = "Testpass123"

        # Registro
        self.driver.get(f"{base_url}/register")
        self.wait.until(EC.presence_of_element_located((By.NAME, "username")))

        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password1").send_keys(password)
        self.driver.find_element(By.NAME, "password2").send_keys(password)
        self.driver.find_element(By.TAG_NAME, "button").click()

        # Esperar redirect (registro exitoso)
        self.wait.until(lambda d: d.current_url != f"{base_url}/register")

        # Login
        self.driver.get(f"{base_url}/login")
        self.wait.until(EC.presence_of_element_located((By.NAME, "username")))

        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password").send_keys(password)
        self.driver.find_element(By.TAG_NAME, "button").click()

        # Esperar redirect (login exitoso)
        self.wait.until(lambda d: d.current_url != f"{base_url}/login")

        # Verificar que haya texto que confirme login, como "Cerrar sesión"
        self.assertIn("Cerrar sesión", self.driver.page_source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
