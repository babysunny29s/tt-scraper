# from playwright.sync_api import sync_playwright

# def run():
#     with sync_playwright() as playwright:
#         firefox = playwright.firefox.launch(headless=False)
#         browser = firefox.new_context()
#         page = browser.new_page()

#         # Sử dụng page để thao tác với trình duyệt Firefox
#         page.goto('https://google.com')
#         page.screenshot(path='example.png')
#         page.goto('https://www.google.com/search?q="Ông Đỗ Hữu Ca khai"&num=100&tbs=qdr:w,srcf:H4sIAAAAAAAAAC3KQQqAMAwF0dt0I_1ROaY0aapIqPwVvLxV3A28eD0ThXF0TRj-on0HIw9ICafD2yRVku5Eqr0ITES64eeZGlYv_14wvfk_1x6TwAAAA&tbm=vid&prmd=isvnbtz')

#         browser.close()
#         firefox.close()

# run()

# Import necessary libraries
import requests
from bs4 import BeautifulSoup

# Define a function to retrieve Google search results
def get_google_results(query):
    # Google search URL
    proxies = {
        "http": "http://172.168.201.4:34000",
        "https": "http://172.168.201.4:34000"
    }
    url = f"https://www.google.com/search?q={query}"
    # Define headers to mimic a browser user-agent
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36"
    }
    params = {
    'q': '"Ông Đỗ Hữu Ca khai"',
    'num': '100',
    'tbs': 'qdr:w,srcf:H4sIAAAAAAAAAC3KQQqAMAwF0dt0I_1ROaY0aapIqPwVvLxV3A28eD0ThXF0TRj-on0HIw9ICafD2yRVku5Eqr0ITES64eeZGlYv_14wvfk_1x6TwAAAA',
    'tbm': 'vid',
    'prmd': 'isvnbtz'
}
    # Send GET request to Google
    response = requests.get(url,params=params, headers=headers,proxies=proxies)
    # Parse HTML content
    soup = BeautifulSoup(response.text, 'html.parser')
    results = []
    # Iterate through search results
    for i, g in enumerate(soup.find_all('div', class_='tF2Cxc')):
        # Extract link, title, and snippet (if available)
        link = g.find('a')['href']
        title = g.find('h3').text
        snippet = g.find('span', class_='aCOpRe').text if g.find('span', class_='aCOpRe') else None
        # Append result to list
        results.append({'title': title, 'link': link, 'snippet': snippet})
        # Limit to top 10 results
        if i == 9:
            break
    return results

print(get_google_results("Đỗ Hữu Ca"))