"""
Personal AI Command Center - Browser Automation Service
"""
import asyncio
from typing import Dict, Optional, List
from datetime import datetime
import os

from app.core.config import settings


class BrowserService:
    """Browser automation service using Playwright"""
    
    def __init__(self):
        self.headless = settings.PLAYWRIGHT_HEADLESS
        self.timeout = settings.BROWSER_TIMEOUT
        self.screenshots_dir = "screenshots"
        self._browser = None
        self._context = None
    
    async def _ensure_browser(self):
        """Ensure browser is initialized"""
        if self._browser is None:
            try:
                from playwright.async_api import async_playwright
                self._playwright = await async_playwright().start()
                self._browser = await self._playwright.chromium.launch(
                    headless=self.headless
                )
                self._context = await self._browser.new_context()
            except ImportError:
                print("Playwright not installed. Install with: pip install playwright && playwright install")
                return False
            except Exception as e:
                print(f"Browser initialization error: {e}")
                return False
        return True
    
    async def execute_task(
        self,
        task_type: str,
        config: Dict,
        params: Optional[Dict] = None
    ) -> Dict:
        """Execute a browser automation task"""
        params = params or {}
        
        if not await self._ensure_browser():
            return {
                "status": "error",
                "message": "Browser not available. Install Playwright."
            }
        
        try:
            if task_type == "form_fill":
                return await self.fill_form(
                    config.get("url"),
                    config.get("fields", {}),
                    params.get("submit", False)
                )
            elif task_type == "screenshot":
                return await self.take_screenshot(
                    config.get("url"),
                    params.get("full_page", False)
                )
            elif task_type == "data_extraction":
                return await self.extract_data(
                    config.get("url"),
                    config.get("selectors", {})
                )
            elif task_type == "login":
                return await self.login(
                    config.get("url"),
                    config.get("username"),
                    config.get("password")
                )
            elif task_type == "price_monitor":
                return await self.monitor_price(
                    config.get("url"),
                    config.get("selector")
                )
            else:
                return {
                    "status": "error",
                    "message": f"Unknown task type: {task_type}"
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def fill_form(
        self,
        url: str,
        fields: Dict[str, str],
        submit: bool = False
    ) -> Dict:
        """Fill a web form"""
        if not await self._ensure_browser():
            return {"status": "error", "message": "Browser not available"}
        
        try:
            page = await self._context.new_page()
            
            # Navigate to URL
            await page.goto(url, timeout=self.timeout)
            
            # Fill fields
            filled_fields = []
            for selector, value in fields.items():
                try:
                    await page.fill(selector, value, timeout=5000)
                    filled_fields.append(selector)
                except Exception as e:
                    print(f"Error filling {selector}: {e}")
            
            # Submit form if requested
            if submit:
                try:
                    # Try common submit buttons
                    submit_selectors = [
                        "button[type=submit]",
                        "input[type=submit]",
                        ".submit-button",
                        "#submit"
                    ]
                    for sel in submit_selectors:
                        try:
                            await page.click(sel, timeout=2000)
                            break
                        except:
                            continue
                except Exception as e:
                    print(f"Error submitting form: {e}")
            
            await page.close()
            
            return {
                "status": "success",
                "url": url,
                "fields_filled": filled_fields,
                "submitted": submit
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def take_screenshot(
        self,
        url: str,
        full_page: bool = False
    ) -> Dict:
        """Take a screenshot of a web page"""
        if not await self._ensure_browser():
            return {"status": "error", "message": "Browser not available"}
        
        try:
            page = await self._context.new_page()
            
            # Navigate to URL
            await page.goto(url, timeout=self.timeout)
            
            # Create screenshots directory
            os.makedirs(self.screenshots_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = os.path.join(self.screenshots_dir, filename)
            
            # Take screenshot
            await page.screenshot(path=filepath, full_page=full_page)
            
            await page.close()
            
            return {
                "status": "success",
                "url": url,
                "screenshot_path": filepath,
                "screenshot_url": f"/screenshots/{filename}",
                "full_page": full_page
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def extract_data(
        self,
        url: str,
        selectors: Dict[str, str]
    ) -> Dict:
        """Extract data from a web page"""
        if not await self._ensure_browser():
            return {"status": "error", "message": "Browser not available"}
        
        try:
            page = await self._context.new_page()
            
            # Navigate to URL
            await page.goto(url, timeout=self.timeout)
            
            # Extract data
            data = {}
            for name, selector in selectors.items():
                try:
                    element = await page.query_selector(selector)
                    if element:
                        data[name] = await element.inner_text()
                except Exception as e:
                    data[name] = f"Error: {e}"
            
            await page.close()
            
            return {
                "status": "success",
                "url": url,
                "data": data
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def login(
        self,
        url: str,
        username: str,
        password: str
    ) -> Dict:
        """Login to a website"""
        if not await self._ensure_browser():
            return {"status": "error", "message": "Browser not available"}
        
        try:
            page = await self._context.new_page()
            
            # Navigate to URL
            await page.goto(url, timeout=self.timeout)
            
            # Try common login selectors
            username_selectors = [
                "input[name=username]",
                "input[name=email]",
                "input[type=email]",
                "input[type=text][name*=user]",
                "#username",
                "#email"
            ]
            
            password_selectors = [
                "input[type=password]",
                "input[name=password]",
                "#password"
            ]
            
            # Fill username
            for sel in username_selectors:
                try:
                    await page.fill(sel, username, timeout=2000)
                    break
                except:
                    continue
            
            # Fill password
            for sel in password_selectors:
                try:
                    await page.fill(sel, password, timeout=2000)
                    break
                except:
                    continue
            
            # Click login button
            login_selectors = [
                "button[type=submit]",
                "input[type=submit]",
                ".login-button",
                "#login"
            ]
            
            for sel in login_selectors:
                try:
                    await page.click(sel, timeout=2000)
                    break
                except:
                    continue
            
            # Wait for navigation
            await page.wait_for_load_state("networkidle", timeout=10000)
            
            # Check if logged in
            current_url = page.url
            
            await page.close()
            
            return {
                "status": "success",
                "url": url,
                "final_url": current_url,
                "message": "Login attempted"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def monitor_price(
        self,
        url: str,
        selector: str
    ) -> Dict:
        """Monitor a price on a web page"""
        result = await self.extract_data(url, {"price": selector})
        
        if result.get("status") == "success":
            price_text = result.get("data", {}).get("price", "")
            # Extract numeric price
            import re
            price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
            price = float(price_match.group()) if price_match else None
            
            return {
                "status": "success",
                "url": url,
                "price_text": price_text,
                "price": price,
                "monitored_at": datetime.utcnow().isoformat()
            }
        
        return result
    
    async def close(self):
        """Close the browser"""
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if hasattr(self, '_playwright'):
            await self._playwright.stop()


# Create instance
browser_service = BrowserService()
