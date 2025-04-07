import requests
import csv
from bs4 import BeautifulSoup

def get_apply_link(scholarship_url):
    """Fetch the 'Apply Online' link from the scholarship detail page."""
    try:
        response = requests.get(scholarship_url)
        if response.status_code == 200:
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            # Find the 'Apply Online' button
            apply_button = soup.find('a', text='Apply Online')
            
            # Check if the button exists and has an href attribute
            if apply_button and 'href' in apply_button.attrs:
                return apply_button['href']
            else:
                return None
        else:
            print(f"Failed to retrieve: {scholarship_url} (Status Code: {response.status_code})")
            return None
    except Exception as e:
        print(f"Error fetching apply link for {scholarship_url}: {e}")
        return None

def scrape_apply_links(input_csv, output_csv):
    """Read the input CSV, scrape the 'Apply Online' links, and save to output CSV."""
    with open(input_csv, 'r', encoding='utf-8') as csv_file:
        csvreader = csv.reader(csv_file)
        next(csvreader)  # Skip the header row

        with open(output_csv, 'w', newline='', encoding='utf-8') as output_file:
            csvwriter = csv.writer(output_file)
            header = ['Scholarship Name', 'Apply Link']
            csvwriter.writerow(header)

            for row in csvreader:
                name = row[0]  # Assuming the scholarship name is the first column
                scholarship_link = row[-2]  # Assuming the link is the last column

                apply_link = get_apply_link(scholarship_link)
                if apply_link:
                    csvwriter.writerow([name, apply_link])
                    print(f"Scraped Apply link for {name}: {apply_link}")
                else:
                    print(f"No Apply link found for {name}")

if __name__ == "__main__":
    input_csv = 'scholarships.csv'  # Input CSV containing scholarship data
    output_csv = 'apply_links.csv'   # Output CSV to save Apply links
    scrape_apply_links(input_csv, output_csv)
