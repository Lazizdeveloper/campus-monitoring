import asyncio
import logging
import os
import re
from typing import Optional
from playwright.async_api import async_playwright

from campus_monitoring.config import settings

logger = logging.getLogger(__name__)


class School21Authenticator:
    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password

    async def get_token(self) -> str:
        """Automates login via Playwright and extracts the API token."""
        logger.info(f"Avtomatik login jarayoni boshlandi (login: {self.login})...")
        token = ""

        async with async_playwright() as p:
            # Headless mode can sometimes be detected by SSO, but let's try it first
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(ignore_https_errors=True)
            page = await context.new_page()

            # Listen for requests to extract the token
            async def handle_request(request):
                nonlocal token
                if "platform.21-school.ru/services/21-school/api/" in request.url:
                    auth_header = request.headers.get("authorization")
                    if auth_header and auth_header.startswith("Bearer "):
                        token = auth_header
                        logger.info("Muvaffaqiyatli token olindi!")

            page.on("request", handle_request)

            try:
                await page.goto("https://platform.21-school.ru/")
                
                # Sberclass / Keycloak SSO form is usually generic
                # Wait for the username input
                await page.wait_for_selector("input[name='username'], input[type='text'], input[name='login']", timeout=15000)
                
                # Try finding standard inputs
                username_inputs = await page.query_selector_all("input[name='username'], input[type='text'], input[name='login']")
                if username_inputs:
                    await username_inputs[0].fill(self.login)
                    
                password_inputs = await page.query_selector_all("input[name='password'], input[type='password']")
                if password_inputs:
                    await password_inputs[0].fill(self.password)
                
                # Find submit button
                submit_buttons = await page.query_selector_all("button[type='submit'], input[type='submit']")
                if submit_buttons:
                    await submit_buttons[0].click()
                else:
                    await page.keyboard.press("Enter")

                # Wait for a while so that redirects finish and requests are made to the API
                for _ in range(15):
                    await asyncio.sleep(1)
                    if token:
                        break

                if not token:
                    logger.warning("Kutish vaqti tugadi, token topilmadi. Sahifa skrinshoti saqlanmoqda...")
                    await page.screenshot(path="login_error.png")

            except Exception as e:
                logger.error(f"Login jarayonida xatolik: {e}")
                await page.screenshot(path="login_error.png")
            finally:
                await browser.close()

        if not token:
            raise Exception("Token olinmadi. Login/parol xato yoki xavfsizlik (captcha) so'ralgan bo'lishi mumkin.")
        
        return token

def update_env_token(token: str) -> None:
    """Updates the .env file with the newly generated token."""
    try:
        env_path = ".env"
        if not os.path.exists(env_path):
            return
            
        with open(env_path, "r") as f:
            lines = f.readlines()
            
        with open(env_path, "w") as f:
            for line in lines:
                if line.startswith("SCHOOL21_TOKEN="):
                    f.write(f"SCHOOL21_TOKEN={token}\n")
                else:
                    f.write(line)
        logger.info("Yangi token .env fayliga saqlandi.")
    except Exception as e:
        logger.error(f".env faylini yangilashda xatolik: {e}")
