import requests
import csv
from bs4 import BeautifulSoup

def snip(src, sub1, sub2):
    """Given a src string, snip the text located between strings sub1 and sub2"""
    idx_start = src.find(sub1) + len(sub1)
    idx_end = src.find(sub2, idx_start)
    
    return src[idx_start:idx_end].strip()

# Function to scrape scholarships and save to CSV
def scrape_scholarships():
    with open('scholarships.csv', 'w', newline='', encoding='utf-8') as csv_file:
        csvwriter = csv.writer(csv_file)
        
        header = ['Scholarship Name', 'Deadline', 'Amount', 'Description', 'Location', 'Years', 'Link', 'Apply Online Link']
        csvwriter.writerow(header)

        total_scholarship = 0

        # Opens each of the 769 pages
        for page_num in range(1, 770):
            # Retrieve the page and html source
            url = f'http://www.collegescholarships.org/financial-aid/?page={page_num}'
            response = requests.get(url)
            print("Response Code:", response.status_code)
            
            if response.status_code != 200:
                print(f"Failed to retrieve page {page_num}")
                continue
            
            html = response.text

            # Restrict to scholarship-list html class
            scholarships_class = snip(html, '<div class="scholarship-list">', '<ul class="pagination">')

            # Split into list, remove dummy first element
            scholarships_list = scholarships_class.split('<div class="row">')
            scholarships_list.pop(0)

            # Collect string fields for each scholarship by snipping the information between HTML tags
            for scholarship in scholarships_list:
                if total_scholarship >= 200:
                    break
                try:
                    # Extract scholarship data
                    link = snip(scholarship, '<h4 class="text-uppercase"><a href="', '"')
                    name = snip(scholarship, '<h4 class="text-uppercase"><a href="' + link + '">', '</a>')
                    amount = snip(scholarship, '<strong>$', '</strong>')
                    deadline = snip(scholarship, '</span><br />\n                <strong>', '</strong>')
                    description = snip(scholarship, '</p>\n        <p>', '</p>\n')
                    location = snip(scholarship, '<i class="fa fa-li fa-map-marker"></i>\n                    ' +
                                    '<span class="trim" data-length="120">\n', '\n')
                    years = snip(scholarship, '<i class="fa fa-li fa-graduation-cap"></i>\n                    ' +
                                 '<span class="trim" data-length="120">\n                                            ',
                                 '\n                                        </span>\n                </li>\n' +
                                 '                <li>\n                    <i class="fa fa-li fa-book"></i>\n')

                    # Follow the scholarship link to get the detailed page
                    # Ensure 'link' is formatted correctly
                    if link.startswith('http'):
                        scholarship_url = link  # Use the link as it is if it's already a complete URL
                    else:
                        scholarship_url = f'https://www.collegescholarships.org{link}'

                    scholarship_response = requests.get(scholarship_url)

                    if scholarship_response.status_code == 200:
                        scholarship_html = scholarship_response.text
                        # Extract the "Apply Online" link
                        apply_online_link = snip(scholarship_html, 'href="', '" class="btn btn-primary" rel="nofollow" target="_blank">Apply Online</a>')
                    else:
                        apply_online_link = 'N/A'
                    
                    # Combine the strings into a list to write a row to the csv
                    csvwriter.writerow([name, deadline, amount, description, location, years, scholarship_url, apply_online_link])
                    total_scholarship += 1
                except Exception as e:
                    print(f"Error processing scholarship: {e}")

            if total_scholarship >= 200:
                break  
        print(f"Total scholarships scraped: {total_scholarship}")
        print("Scholarships scraped and saved to scholarships.csv!")

if __name__ == "__main__":
    scrape_scholarships()
    print("Scholarships scraped and saved to scholarships.csv!")
