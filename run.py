import requests
import pandas as pd
from bs4 import BeautifulSoup


df = pd.read_csv('projects.csv')
domains = [row['Project_URL'] for index, row in df.iterrows()]


def get_content(domain):
    try:
        r = requests.get(domain)
    except:
        r = requests.get(domain.replace('https', 'http'))
    soup = BeautifulSoup(r.content, 'html.parser')
    return r.status_code, soup


def get_domain(link):
    domain = link.split('/')[2].replace('https', '').replace('http', '').replace('www.', '')
    return '.'.join(domain.split('.')[-2:])


def collect_domain_data(domain):
    dd = dict()
    status_code, content = get_content(domain)
    dd['domain'] = domain
    dd['response'] = status_code
    try:
        dd['page_title'] = content.find('head').find('title').get_text()
    except:
        dd['page_title'] = ''
    dd['page_text'] = [s.get_text() for s in content.find_all('p')]
    links = list()
    for s in content.find_all('a', href = True):
        if s['href'].startswith('http'):
            links.append(s['href'])
    dd['external_links'] = links
    dd['external_domains'] = set([get_domain(link) for link in links])
    return dd

data = list()
for domain in domains:
    print(domain)
    try:
        data.append(collect_domain_data(domain.split(' (')[0]))
    except:
        print(f'[!] Failed to collect data for {domain}')

df = pd.DataFrame(data)
df.to_csv('projects_enriched.csv')
