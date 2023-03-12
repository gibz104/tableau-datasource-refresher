import logging
import os
import time
import selenium

from functools import cached_property
from random import randint
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium_stealth import stealth
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from typing import Optional
from webdriver_manager.chrome import ChromeDriverManager


class TableauPublic:
    """Class for interacting with Tableau Public"""

    def __init__(
        self,
        username: Optional[str] = None,  # username to log in to Tableau with
        password: Optional[str] = None,  # password to log in to Tableau with
        server_url: Optional[str] = 'https://public.tableau.com',  # Tableau server/public URL
        headless: Optional[bool] = False,  # run browser in headless mode
    ):
        self.username = username if username else os.getenv('TABLEAU_USER')
        self.password = password if password else os.getenv('TABLEAU_PASS')
        self.server_url = server_url
        self.headless = headless

    @cached_property
    def base_url(self):
        """Returns the base URL for the Tableau server."""

        return self.server_url if self.server_url[-1] != '/' else self.server_url[:-1]

    @cached_property
    def browser(self):
        """Creates a new selenium browser instance."""

        # Create options object
        options = webdriver.ChromeOptions()

        # Set preferences
        preferences = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
        }

        # Set headless mode
        if self.headless:
            options.add_argument("--headless")

        # Set other options
        options.add_argument("--window-size=1920,1080")
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_experimental_option("prefs", preferences)

        # Create driver
        driver = webdriver.Chrome(
            options=options,
            service=ChromeService(ChromeDriverManager().install()),
        )

        # Uses selenium-stealth to hide the browser and avoid bot detection
        stealth(
            driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        # Return driver
        return driver

    def check_stealth(self):
        """
        Opens URL to check if bot-detection picking up browser.
        """

        return self.browser.get('https://pixelscan.net/')

    def signin(self):
        """
        Signs in to Tableau Public.
        """

        # Open login page
        url = self.base_url + '/app/discover?authMode=signIn'
        self.browser.get(url)

        # Get and fill-in email text box (wait 15 seconds for element)
        email_element = WebDriverWait(self.browser, 15).until(
            ec.presence_of_element_located((By.ID, "email"))
        )
        email_element.clear()
        email_element.send_keys(self.username)
        time.sleep(randint(1, 5))

        # Get and fill-in password text box (wait 15 seconds for element)
        password_element = WebDriverWait(self.browser, 15).until(
            ec.presence_of_element_located((By.ID, "password"))
        )
        password_element.clear()
        password_element.send_keys(self.password)
        time.sleep(randint(1, 5))

        # Get and click login button (wait 15 seconds for element)
        try:
            login_button = WebDriverWait(self.browser, 15).until(
                ec.element_to_be_clickable((By.XPATH, "/html/body/div[5]/div/div/div/div/form/div[4]/button"))
            )
        except TimeoutException:
            login_button = WebDriverWait(self.browser, 15).until(
                ec.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div/div/div/div/form/div[4]/button"))
            )
        login_button.click()

        logging.info(f'Logged in to {self.base_url}')

        # wait for login to complete
        time.sleep(3)

    def signout(self):
        """
        Signs out of Tableau Public.
        """

        # Open discover page
        url = self.base_url + '/app/discover'
        self.browser.get(url)

        # Click on avatar (wait 30 seconds for element)
        avatar_element = WebDriverWait(self.browser, 15).until(
            ec.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/header/div/div[2]/div/div'))
        )
        avatar_element.click()
        time.sleep(1)

        # Select sign out option from dropdown menu
        signout_element = WebDriverWait(self.browser, 15).until(
            ec.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div/div/div/div/div[2]/ul/li[3]'))
        )
        signout_element.click()

        logging.info(f'Logged out of {self.base_url}')

        # Wait for logout to complete
        time.sleep(3)

        # Close selenium browser
        self.browser.close()

    def refresh_datasource(
        self,
        dashboard_endpoint: str,
    ):
        """
        Refreshes the data source for a Tableau dashboard.
        """

        # Open dashboard
        url = self.base_url + dashboard_endpoint
        self.browser.get(url)

        # Select 'request data refresh' button
        refresh_element = WebDriverWait(self.browser, 15).until(
            ec.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/div[4]/div[3]/div[2]/div[2]/div[2]/button'))
        )
        refresh_element.click()

        logging.info(f'Refreshed data source for {url}')

        # Wait for page
        time.sleep(3)
