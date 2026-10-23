import asyncio
import hashlib
from pathlib import Path
import os

from playwright.async_api import async_playwright

LOGIN_URL = "https://qalam.nust.edu.pk/"
DASHBOARD_URL = "https://qalam.nust.edu.pk/student/dashboard"
FILE_PATH = Path(__file__).parent
USERNAME = os.getenv("PORTAL_USER")
PASSWORD = os.getenv("PORTAL_PASS")

quizes = ["Focp","English"]
assignments = ["ICT"]


async def login_and_scrape(quiz,assignment):
  async with async_playwright() as p:
    browser = await p.chromium.launch(headless=True)
    
    context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080})
    page = await context.new_page()

    try:
      print("[*] Navigating to login page...")
      await page.goto(LOGIN_URL, wait_until="domcontentloaded")

      print("[*] Clicking and filling username...")
      username_locator = page.locator("#login")
      await username_locator.click()  
      await username_locator.fill(USERNAME)

      print("[*] Clicking and filling password...")
      password_locator = page.locator("#password")
      await password_locator.click()  
      await password_locator.fill(PASSWORD)

      print("[*] Submitting login form...")
      await asyncio.gather(
          page.wait_for_url("**/dashboard**", timeout=15000),
          page.locator("button[type='submit']").click(),
      )
      b = {"Focp":0, "English":1, "Calculus":2, "Discrete":3, "ICT":5}
    
      if quiz:
        for i in quiz:         
          print("[*] Successfully authenticated. Scraping target value...")
          await page.goto(DASHBOARD_URL, wait_until="domcontentloaded")
          await page.locator("a[href*='/student/course/info/']").nth(b[i]).click()
          await page.locator("a[href*='/student/course/']").nth(7).click()
          await page.locator("a.js-toggle-children-row").filter(has_text="Quiz").click()
          await asyncio.sleep(2)

          quiz_parent_row = page.locator("tr.table-parent-row").filter(has_text="Quiz")
          quiz_child_rows = quiz_parent_row.locator("xpath=following-sibling::tr[contains(@class, 'table-child-row')]")
          html_content = await quiz_child_rows.evaluate_all("elements => elements.map(el => el.outerHTML).join('')")
          current_hash = hashlib.sha256(html_content.encode("utf-8")).hexdigest()
          folder_path = FILE_PATH / f"{i}"
          file_path = FILE_PATH / f"{i}/old_hash.txt"
          if os.path.exists(file_path):
            with open(file_path,"r") as f:
              previous_hash = f.read().strip()
              if previous_hash != current_hash:
                print(f"Changes detected in {i}.")
                with open(file_path, "w") as f:
                  f.write(current_hash)
              elif previous_hash == current_hash:
                print(f"No changes detected in {i}.")
              else:
                print("Something is wrong with the hash file.")
          else:
            if os.path.exists(folder_path):
              with open(file_path, "w") as f:
                f.write(current_hash)
                print(f"New hash file for {i} created.")
            elif not os.path.exists(folder_path):
              os.path.makedirs(folder_path)
              with open(file_path, "w") as f:
                f.write(current_hash)
                print(f"New file and folder for {i} created.")
            else:
              print("File does not exist and some error in creating file or folder")

      if assignment:
        for i in assignment:         
            print("[*] Successfully authenticated. Scraping target value...")
            await page.goto(DASHBOARD_URL, wait_until="domcontentloaded")
            await page.locator("a[href*='/student/course/info/']").nth(b[i]).click()
            await page.locator("a[href*='/student/course/']").nth(7).click()
            await page.locator("a.js-toggle-children-row").filter(has_text="Assignments ").click()
            await asyncio.sleep(2)

            quiz_parent_row = page.locator("tr.table-parent-row").filter(has_text="Assignments")
            quiz_child_rows = quiz_parent_row.locator("xpath=following-sibling::tr[contains(@class, 'table-child-row')]")
            html_content = await quiz_child_rows.evaluate_all("elements => elements.map(el => el.outerHTML).join('')")
            current_hash = hashlib.sha256(html_content.encode("utf-8")).hexdigest()
            folder_path = FILE_PATH / f"{i}_assignments"
            file_path = FILE_PATH / f"{i}_assignments/old_hash.txt"
            if os.path.exists(file_path):
                with open(file_path,"r") as f:
                    previous_hash = f.read().strip()
                    if previous_hash != current_hash:
                        print(f"Changes detected in {i} assignments.")
                        with open(file_path, "w") as f:
                            f.write(current_hash)
                    elif previous_hash == current_hash:
                        print(f"No changes detected in {i} assignments.")
                    else:
                        print(f"Something is wrong with the hash file of {i} assignments.")
            else:
                print(folder_path)
                print(file_path)
                if os.path.exists(folder_path):
                    with open(file_path, "w") as f:                          
                        f.write(current_hash)
                        print(f"New hash file for {i} assignments created.")
                elif not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    with open(file_path, "w") as f:
                            f.write(current_hash)
                    print(f"New file and folder for {i} assignments created.")
                else:
                    print("File does not exist and some error in creating file or folder of assignments")
        
           


      await asyncio.sleep(2)
      await browser.close()


    finally:
      await browser.close()

if __name__ == "__main__":
  asyncio.run(login_and_scrape(quizes,assignments))