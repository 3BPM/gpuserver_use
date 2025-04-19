import requests
from bs4 import BeautifulSoup
import yaml,re

# 目标网页URL
# # url = "https://www.aminer.cn/profile/honggang-qi/53f43960dabfaec22ba9d9f7"
# # 发送HTTP请求
# response = requests.get(url)
# response.raise_for_status()  # 确保请求成功

# # 解析HTML内容
# soup = BeautifulSoup(response.content, 'html.parser')
url = "/home/jinyue/a/qi.html"

# 从本地文件读取HTML内容
with open(url, 'r', encoding='utf-8') as file:
    content = file.read()

# 解析HTML内容
soup = BeautifulSoup(content, 'html.parser')
# 找到所有论文的容器
papers = soup.find_all('div', class_='paper-item')

# 存储解析后的论文信息
publications = []

for paper in papers:
    # 提取论文标题
    title_span = paper.find('span', class_='paper-title')
    if title_span:
        title = ' '.join(title_span.get_text(strip=True).split())
    else:
        title = None

    # 提取论文链接
    link_tag = paper.find('a', class_='title-link')
    link = link_tag['href'] if link_tag else None

    # 提取作者信息
    authors_tag = paper.find('div', class_='authors')
    if authors_tag:
        authors = authors_tag.text.strip()
        authors = re.sub(r'\s+', ' ', authors)  # Replace multiple spaces/newlines with a single space
        authors = authors.replace('Authors:', '').strip()  # Remove "Authors:" label if present
    else:
        authors = None

    # 提取期刊或会议名称
    venue_tag = paper.find('div', class_='venue-link')  # Corrected to look for 'venue-link'
    if venue_tag:
        publication = venue_tag.get_text(strip=True)
        publication = re.sub(r'\s+', ' ', publication)  # Replace multiple spaces/newlines with a single space
    else:
        publication = None
        # 提取DOI链接
    doi_tag = paper.find('a', class_='url')
    if doi_tag:
        doi = doi_tag['href'] if doi_tag else None
    else:
        doi = None


    # Create the dictionary for the YAML output
    paper_info = {
        'title': title,
        'authors': authors,
        'publication': publication,
        'link': doi,
        'highlight': authors.split()[0] if authors else None  # You could extract the first author for highlight
    }




    publications.append(paper_info)

# # 将解析后的论文信息写入YAML文件
# with open('publications0000.yaml', 'w', encoding='utf-8') as f:
#     yaml.dump(publications, f, allow_unicode=True, sort_keys=False)


# Safely write to YAML
with open('publications0000.yaml', 'w', encoding='utf-8') as f:
    yaml.dump(publications, f, allow_unicode=True, sort_keys=False)


print("爬取完成，数据已保存到publications0000.yaml文件中。")