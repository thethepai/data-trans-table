from bs4 import BeautifulSoup

class HTMLTableParser:
    def __init__(self, html):
        self.html = html
        self.cell_data = []

    def parse_html_table(self):
        soup = BeautifulSoup(self.html, 'html.parser')
        table = soup.find('table')
        
        cell_data = []
        for row_idx, row in enumerate(table.find_all('tr')):
            row_data = []
            for cell in row.find_all(['td', 'th']):
                cell_text = cell.get_text(strip=True)
                rowspan = int(cell.get('rowspan', 1))
                colspan = int(cell.get('colspan', 1))
                row_data.append((cell_text, rowspan, colspan, row_idx))
            cell_data.append(row_data)
        
        self.cell_data = cell_data

    def generate_md_table(self):
        md_table = []
        max_cols = max(sum(cell[2] for cell in row) for row in self.cell_data)
        
        # Initialize a list to keep track of rowspan cells
        rowspan_tracker = [0] * max_cols
        
        for row in self.cell_data:
            md_row = [''] * max_cols
            col_idx = 0
            for cell_text, rowspan, colspan, row_idx in row:
                # Skip columns that are occupied by rowspan from previous rows
                while col_idx < max_cols and rowspan_tracker[col_idx] > 0:
                    rowspan_tracker[col_idx] -= 1
                    col_idx += 1
                
                for i in range(colspan):
                    if col_idx + i < max_cols:
                        md_row[col_idx + i] = cell_text # if i == 0 else ''
                        if rowspan > 1:
                            rowspan_tracker[col_idx + i] = rowspan - 1
                
                col_idx += colspan
            
            # Decrease rowspan tracker for new row from col_idx to the end
            for i in range(col_idx, max_cols):
                if rowspan_tracker[i] > 0:
                    rowspan_tracker[i] -= 1
            
            md_table.append('| ' + ' | '.join(md_row) + ' |')
        
        return '\n'.join(md_table)

    def convert_html_to_md(self):
        self.parse_html_table()
        return self.generate_md_table()

def main():
    html_string = """
    <html>
    </html>
    """
    parser = HTMLTableParser(html_string)
    md_output = parser.convert_html_to_md()
    print(md_output)
    
if __name__ == "__main__":
    main()