from bs4 import BeautifulSoup as bs

def process_text(text: str):
    # Strip
    text = text.strip()
    # Remove '\n'
    text = text.replace('\n', ' ')
    # Remove '\t'
    text = text.replace('\t', ' ')
    # Remove long spaces
    list_text = text.split(' ')
    # Remove empty string
    list_text = list(filter(lambda x: x != '', list_text))
    # Join
    text = ' '.join(list_text)
    
    return text 

def parse_html(html):
    soup = bs(html, 'html.parser')
    
    # Find all the tables with class: table-horizontal
    tables = soup.find_all('table', {'class' : 'table-horizontal'})
    
    list_keys = ['brand', '']
    
    data = {}
    
    for table in tables:
        tbody = table.find('tbody')
        rows = tbody.find_all('tr')
        
        for row in rows:
            th = row.find('th')
            
            print(process_text(th.text), end = '|')
            cells = row.find_all('td')
            for cell in cells:
                print(process_text(cell.text), end = '|')
            print()
        
if __name__ == '__main__':
    with open('test.html', 'r', encoding='utf-8') as f:
        html = f.read()
    
    parse_html(html)
    
    