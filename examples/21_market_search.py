# 市场信息搜集
# 运行前置条件: 
# 1. 安装 BeutifulSoup 库：pip install beautifulsoup4
# 2. 安装 playwrite 库: pip install playwright
from GeneralAgent import Agent
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import quote
import time

def get_baidu_search_url(keyword):
    """生成百度搜索URL，只处理关键词和时间戳"""
    current_timestamp = int(time.time())
    past_timestamp = current_timestamp - (24 * 3600)  # 24小时前
    base_url = "https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=1&tn=baidu&wd={}&fenlei=256&rqlang=cn&rsv_dl=tb&rsv_enter=1&rsv_btype=i&tfflag=1&gpc=stf%3D{}%2C{}|stftype%3D1"
    return base_url.format(quote(keyword), past_timestamp, current_timestamp)

def extract_news_articles(url):
    """提取网页中的新闻文章和URL"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            page.goto(url)
            page.wait_for_load_state('networkidle')
            
            content = page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            articles = []
            if 'baidu.com' in url:
                # 百度搜索结果处理
                search_results = soup.find_all('div', class_=['result-op', 'result'])
                for result in search_results:
                    title_elem = result.find('h3')
                    if title_elem:
                        link = title_elem.find('a')
                        if link:
                            articles.append({
                                'title': title_elem.get_text().strip(),
                                'url': link.get('href', ''),
                                'source': '百度搜索'
                            })
            else:
                # 懂车帝处理（保持原来的逻辑）
                links = soup.find_all('a', href=True)
                base_url = "https://www.dongchedi.com"
                
                for link in links:
                    href = link.get('href', '')
                    title = link.get_text().strip()
                    if title and href:  # 保留所有可能的文章，让LLM判断
                        full_url = href if href.startswith('http') else base_url + href
                        articles.append({
                            'title': title,
                            'url': full_url,
                            'source': url
                        })
            
            return articles
            
        except Exception as e:
            return f"提取文章时出错: {str(e)}"
        finally:
            browser.close()

def process_single_url(url: str, keyword: str, search_description: str, agent: Agent):
    """处理单个URL的文章"""
    if 'baidu.com' in url:
        url = get_baidu_search_url(keyword)
    
    articles = extract_news_articles(url)
    if not isinstance(articles, list):
        return f"处理URL {url} 时出错: {articles}"
    
    if not articles:
        return f"URL {url} 未找到任何文章"
    
    prompt = f"""
    请从以下文章列表中严格筛选出仅与"{keyword}"直接相关的最新新闻。

    文章列表：
    {articles}

    筛选标准：
    1. 必须在标题中直接提到"{keyword}"或与{keyword}直接相关的产品/事件
    2. 必须是最新的新闻内容，不要选择普通的产品介绍页面
    3. 新闻必须具有时效性和重要性

    请按照以下格式整理符合条件的文章：
    标题,网址

    要求：
    1. 使用逗号分隔字段
    2. 每行一篇文章
    3. 第一行为表头
    4. 如果标题包含逗号，用双引号括起来
    5. 按相关性和重要性排序
    6. 只输出100%确定与{keyword}直接相关的文章
    """
    return agent.run(prompt, display=False)

def process_articles_with_command(urls: list, keyword: str, search_description: str = None):
    """处理所有URL的文章"""
    load_dotenv()
    
    if not search_description:
        search_description = f"寻找与{keyword}相关的最新资讯"
    
    agent = Agent(f'''你是一个专业的资讯分析助手。
你的任务是找出与用户需求相关的文章。
用户搜索需求：{search_description}
''')
    
    try:
        print(f"\n搜索关键词: {keyword}")
        print(f"搜索需求: {search_description}\n")
        
        all_results = []
        for url in urls:
            print(f"\n处理URL: {url}")
            result = process_single_url(url, keyword, search_description, agent)
            all_results.append(f"\n来自 {url} 的结果：\n{result}")
        
        return "\n".join(all_results)
            
    except Exception as e:
        return f"处理出错: {str(e)}"

# 使用示例
if __name__ == "__main__":
    keyword = "新能源汽车"
    description = "寻找所有和新能源汽车可能相关的动态，只找和新能源汽车最直接相关的最新重要信息（企业，行业政策等）"
    
    urls = [
        "https://www.dongchedi.com/",
        "https://www.baidu.com/s",
        "https://www.dongchedi.com/",
        "https://36kr.com/",
    ]
    
    result = process_articles_with_command(urls, keyword, description)
    print(result)
