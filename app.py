from flask import Flask, render_template, request
import csv
import mysql.connector
from datetime import datetime

app = Flask(__name__)

DB_CONFIG = {
    'user': 'root',
    'password': 'root',
    'host': '127.0.0.1',
    'database': 'scholarship'
}

def get_db_connection():
    """Establish a new database connection."""
    return mysql.connector.connect(**DB_CONFIG)

from datetime import datetime

def parse_date(date_str):
    """Parse a date string into a datetime object."""
    try:
        # Try to parse "Month Day"
        return datetime.strptime(date_str, '%B %d')
    except ValueError:
        try:
            # Try to parse "Month Day, Year"
            return datetime.strptime(date_str, '%B %d, %Y')
        except ValueError:
            return None

# def save_scholarships_to_db(csv_file):
#     """Read scholarships from a CSV file and insert them into the MySQL database."""
#     conn = get_db_connection()
#     cursor = conn.cursor()

#     with open(csv_file, 'r', encoding='utf-8') as file:
#         csvreader = csv.reader(file)
#         header = next(csvreader)

#         for row in csvreader:
#             scholarship_name = row[0].strip()  # Clean the name
            
#             # Clean the amount value by removing commas and checking if it's a valid number
#             try:
#                 amount = float(row[2].replace(',', '').strip())
#             except ValueError:
#                 print(f"Skipping invalid amount for scholarship: {scholarship_name}. Original value: '{row[2]}'")
#                 continue  # Skip this row if the amount is invalid
            
#             # Check if the scholarship already exists
#             cursor.execute("SELECT COUNT(*) FROM scholarships WHERE name = %s", (scholarship_name,))
#             exists = cursor.fetchone()[0] > 0
            
#             if exists:
#                 print(f"Skipping duplicate scholarship: {scholarship_name}")
#                 continue  # Skip if the scholarship already exists

#             state_name = row[4]  # Assuming this is the location field

#             # Insert into database using state_name directly
#             cursor.execute("""  
#                 INSERT INTO scholarships (name, deadline, amount, description, location, level)
#                 VALUES (%s, %s, %s, %s, %s, %s)
#             """, (scholarship_name, row[1], amount, row[3], state_name, row[5]))

#     conn.commit()
#     cursor.close()
#     conn.close()

def save_scholarships_to_db(csv_file):
    """Read scholarships from a CSV file and insert them into the MySQL database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    with open(csv_file, 'r', encoding='utf-8') as file:
        csvreader = csv.reader(file)
        header = next(csvreader)

        for row in csvreader:
            scholarship_name = row[0].strip()  # Clean the name

            # Clean the amount value by removing commas and checking if it's a valid number
            try:
                amount = float(row[2].replace(',', '').strip())
            except ValueError:
                print(f"Skipping invalid amount for scholarship: {scholarship_name}. Original value: '{row[2]}'")
                continue  # Skip this row if the amount is invalid

            # Check if the scholarship already exists
            cursor.execute("SELECT COUNT(*) FROM scholarships WHERE name = %s", (scholarship_name,))
            exists = cursor.fetchone()[0] > 0

            if exists:
                print(f"Skipping duplicate scholarship: {scholarship_name}")
                continue  # Skip if the scholarship already exists

            # Handle the location
            state_names = [state.strip() for state in row[4].split(',')]  # Split by comma and strip whitespace
            for state_name in state_names:
                cursor.execute(""" 
                    INSERT INTO scholarships (name, deadline, amount, description, location, level)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (row[0], row[1], amount, row[3], state_name, row[5]))

    conn.commit()
    cursor.close()
    conn.close()


def save_apply_links_to_db(csv_file):
    """Insert apply links from apply_links.csv into the database."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Add dictionary=True here
    
    with open(csv_file, 'r', encoding='utf-8') as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        
        # Fetch valid scholarships to avoid duplicates
        cursor.execute("SELECT name FROM scholarships")
        valid_scholarships = {row['name'] for row in cursor.fetchall()}  # Accessing row as dict

        for row in csvreader:
            if row[0] in valid_scholarships:  # Check for duplicates
                cursor.execute("""
                    INSERT INTO apply_links (scholarship_name, link)
                    VALUES (%s, %s)
                """, (row[0], row[1]))

    conn.commit()
    cursor.close()
    conn.close()



def read_scholarships():
    """Retrieve scholarship details from the database."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM scholarships")
    scholarships = cursor.fetchall()
    cursor.close()
    conn.close()
    return scholarships

def read_apply_links():
    """Retrieve apply links from the database."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM apply_links")
    apply_links = cursor.fetchall()
    cursor.close()
    conn.close()
    return apply_links

# @app.route('/index', methods=['GET', 'POST'])
# def index():
#     scholarships = read_scholarships()
#     apply_links = {link['scholarship_name']: link['link'] for link in read_apply_links()}

#     # Get unique locations for the dropdown
#     unique_locations = set()
#     for scholarship in scholarships:
#         locations = scholarship['location'].split(',')
#         for location in locations:
#             unique_locations.add(location.strip())

#     sorted_locations = sorted(unique_locations)
#     if "No Geographic Restrictions" in sorted_locations:
#         sorted_locations.remove("No Geographic Restrictions")
#         sorted_locations.insert(0, "No Geographic Restrictions")

#     # Filter scholarships based on form input
#     if request.method == 'POST':
#         location_filter = request.form.get('location')
#         deadline_filter = request.form.get('deadline')
#         min_amount = float(request.form.get('min_amount', 0))
#         max_amount = float(request.form.get('max_amount', float('inf')))

#         # Apply filters to the scholarships
#         if location_filter:
#             scholarships = [scholar for scholar in scholarships if 
#                             (location_filter in scholar['location'] or 
#                              scholar['location'] == 'No Geographical Restrictions')]

#         if deadline_filter:
#             scholarships = [scholar for scholar in scholarships if 
#                             scholar['deadline'] == 'Rolling' or 
#                             parse_date(scholar['deadline']) == parse_date(deadline_filter)]

#         scholarships = [scholar for scholar in scholarships if min_amount <= float(scholar['amount']) <= max_amount]

#     return render_template('index.html', scholarships=scholarships, apply_links=apply_links, unique_locations=sorted_locations)

# @app.route('/index', methods=['GET', 'POST'])
# def index():
#     scholarships = read_scholarships()
#     apply_links = {link['scholarship_name']: link['link'] for link in read_apply_links()}

#     # Filter scholarships based on form input
#     if request.method == 'POST':
#         location_filter = request.form.get('location')
#         deadline = request.form.get('deadline')
#         min_amount = float(request.form.get('min_amount', 0))
#         max_amount = float(request.form.get('max_amount', 100000))
#         level_filter = request.form.get('level')

#         # Apply filters to the scholarships
#         if location_filter:
#             scholarships = [scholar for scholar in scholarships if 
#                             location_filter in scholar['location'] or 
#                             scholar['location'] == 'No Geographical Restrictions']
        
#         if deadline:
#             scholarships = [scholar for scholar in scholarships if 
#                             scholar['deadline'] == 'Rolling' or 
#                             scholar['deadline'] == deadline]

#         scholarships = [scholar for scholar in scholarships if min_amount <= float(scholar['amount']) <= max_amount]
        
#         if level_filter:
#             scholarships = [scholar for scholar in scholarships if level_filter in [level.strip() for level in scholar['level'].split(',')]]

#     return render_template('index.html', scholarships=scholarships, apply_links=apply_links)

# @app.route('/index', methods=['GET', 'POST'])
# def index():
#     scholarships = read_scholarships()
#     apply_links = {link['scholarship_name']: link['link'] for link in read_apply_links()}

#     # Get unique locations for the dropdown, taking into account multiple locations per scholarship
#     unique_locations = set()
#     for scholarship in scholarships:
#         locations = scholarship['location'].split(',')  # Split by comma
#         for location in locations:
#             unique_locations.add(location.strip())  # Strip whitespace and add to the set

#     # Sort locations alphabetically, ensuring "No Geographic Restrictions" comes first
#     sorted_locations = sorted(unique_locations)
#     if "No Geographic Restrictions" in sorted_locations:
#         sorted_locations.remove("No Geographic Restrictions")  # Remove it from the list
#         sorted_locations.insert(0, "No Geographic Restrictions")  # Add it as the first item

#     # Filter scholarships based on form input
#     if request.method == 'POST':
#         location_filter = request.form.get('location')
#         deadline = request.form.get('deadline')
#         min_amount = float(request.form.get('min_amount', 0))
#         max_amount = float(request.form.get('max_amount', 100000))
#         level_filter = request.form.get('level')

#         print(f"Filters applied: Location: {location_filter}, Deadline: {deadline}, Min Amount: {min_amount}, Max Amount: {max_amount}, Level: {level_filter}")

#         # Apply filters to the scholarships
#         if location_filter:
#             scholarships = [scholar for scholar in scholarships if 
#                             (location_filter in [loc.strip() for loc in scholar['location'].split(',')] or 
#                              scholar['location'] == 'No Geographic Restrictions')]

#         if deadline:
#             scholarships = [scholar for scholar in scholarships if 
#                             scholar['deadline'] == 'Rolling' or 
#                             scholar['deadline'] == deadline]

#         if min_amount:
#             scholarships = [scholar for scholar in scholarships if float(scholar['amount']) >= min_amount]

#         if max_amount:
#             scholarships = [scholar for scholar in scholarships if float(scholar['amount']) <= max_amount]

#         if level_filter:
#             scholarships = [scholar for scholar in scholarships if scholar['level'] == level_filter]

#         print(f"Number of scholarships after filters: {len(scholarships)}")

#     return render_template('index.html', scholarships=scholarships, apply_links=apply_links, unique_locations=sorted_locations)

from datetime import datetime

from datetime import datetime

def parse_date(date_str):
    """Parse a date string into a datetime object using the current year."""
    try:
        # Check if the date is in 'YYYY-MM-DD' format
        if '-' in date_str:
            return datetime.strptime(date_str, '%Y-%m-%d')
        else:
            # Fall back to 'Month Day' (assume current year)
            current_year = datetime.now().year
            return datetime.strptime(f"{date_str} {current_year}", '%B %d %Y')
    except ValueError as e:
        print(f"Error parsing date '{date_str}': {e}")  # Debugging statement
        return None


@app.route('/index', methods=['GET', 'POST'])
def index():
    scholarships = read_scholarships()
    apply_links = {link['scholarship_name']: link['link'] for link in read_apply_links()}

    # Get unique locations for the dropdown
    unique_locations = set()
    for scholarship in scholarships:
        locations = scholarship['location'].split(',')  # Split by comma
        for location in locations:
            unique_locations.add(location.strip())  # Strip whitespace

    # Sort locations alphabetically, ensuring "No Geographic Restrictions" comes first
    sorted_locations = sorted(unique_locations)
    if "No Geographic Restrictions" in sorted_locations:
        sorted_locations.remove("No Geographic Restrictions")  # Remove it
        sorted_locations.insert(0, "No Geographic Restrictions")  # Add it first

    # Filter scholarships based on form input
    if request.method == 'POST':
        location_filter = request.form.get('location')
        selected_deadline = request.form.get('deadline')  # Getting selected deadline as a string
        min_amount = float(request.form.get('min_amount', 0))
        max_amount = float(request.form.get('max_amount', 100000))
        level_filter = request.form.get('level')

        print(f"Location Filter: {location_filter}")  # Debugging
        print(f"Selected Deadline: {selected_deadline}")  # Debugging

        # Apply filters to the scholarships
        if location_filter:
            scholarships = [scholar for scholar in scholarships if 
                            (location_filter in [loc.strip() for loc in scholar['location'].split(',')] or 
                             scholar['location'] == 'No Geographic Restrictions')]

        # Filter scholarships by deadline
        if selected_deadline:
            selected_deadline_parsed = parse_date(selected_deadline)  # Parse the selected deadline
            print(f"Parsed Selected Deadline: {selected_deadline_parsed}")  # Debugging
            if selected_deadline_parsed:  # Only proceed if the parsed date is valid
                scholarships = [scholar for scholar in scholarships if 
                                scholar['deadline'] == 'Rolling' or 
                                (scholar['deadline'] != 'None' and 
                                 parse_date(scholar['deadline']) is not None and 
                                 parse_date(scholar['deadline']) >= selected_deadline_parsed)]

                # Debugging output to check which scholarships are being filtered out
                print(f"Filtered Scholarships Count: {len(scholarships)}")
                for sch in scholarships:
                    sch_deadline = parse_date(sch['deadline'])
                    print(f"Scholarship: {sch['name']}, Deadline: {sch['deadline']}, Parsed Deadline: {sch_deadline}")  # Debugging

        if min_amount:
            scholarships = [scholar for scholar in scholarships if float(scholar['amount']) >= min_amount]

        # Filter by level (Year) using comma-separated values
        if level_filter:
            scholarships = [scholar for scholar in scholarships if level_filter in [level.strip() for level in scholar['level'].split(',')]]

    return render_template('index.html', scholarships=scholarships, apply_links=apply_links, unique_locations=sorted_locations)

@app.route('/about')
def about():
    """Render the About Us page."""
    return render_template('about.html')

@app.route('/')
def home():
    """Render the Home page."""
    return render_template('home.html')

if __name__ == '__main__':
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if scholarships already exist
    cursor.execute("SELECT COUNT(*) FROM scholarships")
    scholarship_count = cursor.fetchone()[0]

    # Check if apply links already exist
    cursor.execute("SELECT COUNT(*) FROM apply_links")
    apply_links_count = cursor.fetchone()[0]

    # Import scholarships if none exist
    if scholarship_count == 0:
        save_scholarships_to_db('scholarships.csv')
    else:
        print("Scholarships already imported. Skipping import.")

    # Import apply links if none exist
    if apply_links_count == 0:
        save_apply_links_to_db('apply_links.csv')
    else:
        print("Apply links already imported. Skipping import.")

    cursor.close()
    conn.close()

    app.run(debug=True)

