import unittest
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import HtmlTestRunner

base_url = "http://127.0.0.1:8000"

class TestRegistroUsuario(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        options = Options()
        cls.service = FirefoxService(executable_path='./drivers/geckodriver.exe')
        cls.driver = webdriver.Firefox(service=cls.service, options=options)
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def abrir_registro(self):
        self.driver.get(f"{base_url}/register")
        self.wait.until(EC.presence_of_element_located((By.NAME, "username")))

    def test_registro_correcto(self):
        """Registro con datos válidos"""
        self.abrir_registro()
        username = f"testuser{int(time.time())}"  # único para evitar duplicados
        self.driver.find_element(By.NAME, "username").send_keys(username)
        self.driver.find_element(By.NAME, "password1").send_keys("Testpass123")
        self.driver.find_element(By.NAME, "password2").send_keys("Testpass123")
        self.driver.find_element(By.TAG_NAME, "button").click()

        time.sleep(2)
        current_url = self.driver.current_url
        self.assertNotIn("/register", current_url, "[FAIL] Registro válido no redirigió")
        print("[PASS] Registro válido")

    def test_registro_sin_usuario(self):
        """Intento de registro sin nombre de usuario"""
        self.abrir_registro()
        self.driver.find_element(By.NAME, "password1").send_keys("Testpass123")
        self.driver.find_element(By.NAME, "password2").send_keys("Testpass123")
        self.driver.find_element(By.TAG_NAME, "button").click()

        self.assertIn("Este campo es obligatorio", self.driver.page_source)
        print("[PASS] Registro sin usuario rechazado correctamente")

    def test_registro_sin_contraseña(self):
        """Intento de registro sin contraseña"""
        self.abrir_registro()
        self.driver.find_element(By.NAME, "username").send_keys("usuario_sin_pass")
        self.driver.find_element(By.TAG_NAME, "button").click()

        self.assertIn("Este campo es obligatorio", self.driver.page_source)
        print("[PASS] Registro sin contraseña rechazado correctamente")

    def test_registro_contraseñas_diferentes(self):
        self.abrir_registro()
        self.driver.find_element(By.NAME, "username").send_keys("usuario_mismatch")
        self.driver.find_element(By.NAME, "password1").send_keys("Testpass123")
        self.driver.find_element(By.NAME, "password2").send_keys("OtraPass456")
        self.driver.find_element(By.TAG_NAME, "button").click()

        time.sleep(2)  

        # La URL debe seguir siendo la página de registro
        self.assertIn("/register", self.driver.current_url)

        # El formulario debe seguir visible, comprobamos que el input username esté visible
        username_input = self.driver.find_element(By.NAME, "username")
        self.assertTrue(username_input.is_displayed())


    def test_registro_usuario_existente(self):
        """Usuario ya existe"""
        self.abrir_registro()
        self.driver.find_element(By.NAME, "username").send_keys("testuser_existente")
        self.driver.find_element(By.NAME, "password1").send_keys("Testpass123")
        self.driver.find_element(By.NAME, "password2").send_keys("Testpass123")
        self.driver.find_element(By.TAG_NAME, "button").click()

        # Repetimos intento con mismo usuario
        self.abrir_registro()
        self.driver.find_element(By.NAME, "username").send_keys("testuser_existente")
        self.driver.find_element(By.NAME, "password1").send_keys("Testpass123")
        self.driver.find_element(By.NAME, "password2").send_keys("Testpass123")
        self.driver.find_element(By.TAG_NAME, "button").click()

        self.assertIn("Un usuario con ese nombre ya existe", self.driver.page_source)
        print("[PASS] Registro con usuario duplicado rechazado correctamente")


if __name__ == '__main__':
    unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='reports'), verbosity=2)
