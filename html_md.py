from bs4 import BeautifulSoup

def html_to_markdown(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')
    markdown = []

    for row in table.find_all('tr'):
        cells = row.find_all(['td', 'th'])
        row_data = [cell.get_text(strip=True) for cell in cells]
        markdown.append('| ' + ' | '.join(row_data) + ' |')

    # Add header separator for markdown table
    if markdown:
        header = markdown[0]
        num_columns = len(header.split('|')) - 2  # Subtract 2 for the leading and trailing '|'
        separator = '| ' + ' | '.join(['---'] * num_columns) + ' |'
        markdown.insert(1, separator)

    return '\n'.join(markdown)

if __name__ == '__main__':
    # Read HTML content from file
    with open('table1.html', 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Convert HTML to Markdown
    markdown_content = html_to_markdown(html_content)

    # Write Markdown content to file
    with open('table.md', 'w', encoding='utf-8') as file:
        file.write(markdown_content)