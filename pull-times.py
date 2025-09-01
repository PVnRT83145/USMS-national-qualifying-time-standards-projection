# Before executing this script, navigate to the nat-times folder within the prjects folder. then run the command "source nat-times-env/bin/activate"
# After running this script, run "deactivate" in the terminal
# https://www-usms-hhgdctfafngha6hr.z01.azurefd.net/-/media/usms/pdfs/pool%20national%20championships/national%20qualifying%20times%20frequently%20asked%20questions.pdf?rev=e12f6e7f006146149badbfa70e7030bd&hash=91EF8A1CC21104E3FC063C68424DC4AD&hash=91EF8A1CC21104E3FC063C68424DC4AD
# The function of this script is to either project or calculate all NQTs for the current year prior to USMS' official release which can happen fairly late in the season relative to nationals.
# Some tweaking might be needed if there is an interval between when the top ten is published but before USMS releases the NQTs, in which case, the official times are entirely
# knowable and calculable.
# SCRIPT IS ONLY SET UP TO WORK FOR SCY!!!!! DON'T @ ME ABOUT LONG COURSE. Make your own maybe?

import numpy as np, requests as rq, pandas as pd, re
from bs4 import BeautifulSoup as bs
from datetime import datetime as dt
import warnings, math
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium.webdriver.common.by import By


options = Options()
options.add_argument("--headless")
warnings.simplefilter(action='ignore', category=FutureWarning)
np.set_printoptions(linewidth=256)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 300)


# Function handles rounding up to 24 for the 18 to 24 age group
def roundup(n):
    return math.ceil(n / 5) * 5

# Determines current year.
year  =  dt.now().year

# Create selectable variables
seasons = [str(year - 1) + "-" + str(year) , str(year - 2) + "-" + str(year - 1) , str(year - 3) + "-" + str(year - 2)]
strokes = ["Free" , "Back" , "Breast", "Fly" , "IM"]
distances = [50 , 100 , 200 , 400 , 500 , 1000 , 1650]
genders = ["Men" , "Women"]
lower_ages = [18]
years = [year - 2, year - 1, year]
for i in range(12):
    lower_ages.append(5 * (i + 5))

# Dimensionalize and add initial data to master tables
men_data = np.empty([20, 40], dtype=object)
women_data = np.empty([20, 40], dtype=object)
men_ranks = np.empty([20, 40], dtype=object)
women_ranks = np.empty([20, 40], dtype=object)

j = 0
for i in range(18):
    if i < 6:
        men_data[i + 2, 0] = str(distances[i]) + " " + strokes[0] if i < 3 else str(distances[i + 1]) + " " + strokes[0]
        women_data[i + 2, 0] = str(distances[i]) + " " + strokes[0] if i < 3 else str(distances[i + 1]) + " " + strokes[0]
        men_ranks[i + 2, 0] = str(distances[i]) + " " + strokes[0] if i < 3 else str(distances[i + 1]) + " " + strokes[0]
        women_ranks[i + 2, 0] = str(distances[i]) + " " + strokes[0] if i < 3 else str(distances[i + 1]) + " " + strokes[0]
    else:
        j = j + 1 if i % 3 == 0 else j
        men_data[i + 2, 0] = str(distances[i % 3]) + " " + strokes[j] if i < 15 else str(distances[(i % 3) + 1]) + " " + strokes[j]
        women_data[i + 2, 0] = str(distances[i % 3]) + " " + strokes[j] if i < 15 else str(distances[(i % 3) + 1]) + " " + strokes[j]
        men_ranks[i + 2, 0] = str(distances[i % 3]) + " " + strokes[j] if i < 15 else str(distances[(i % 3) + 1]) + " " + strokes[j]
        women_ranks[i + 2, 0] = str(distances[i % 3]) + " " + strokes[j] if i < 15 else str(distances[(i % 3) + 1]) + " " + strokes[j]
        
j = 0 
for i in  range (len(men_data[0, :]) - 1):
    j = j + 1 if i % 3 == 0 else j
    men_data[0, i + 1] = str(lower_ages[j - 1]) + " - " + str(roundup(lower_ages[j - 1] + 4) - 1)
    women_data[0, i + 1] = str(lower_ages[j - 1]) + " - " + str(roundup(lower_ages[j - 1] + 4) - 1)
    men_ranks[0, i + 1] = str(lower_ages[j - 1]) + " - " + str(roundup(lower_ages[j - 1] + 4) - 1)
    women_ranks[0, i + 1] = str(lower_ages[j - 1]) + " - " + str(roundup(lower_ages[j - 1] + 4) - 1)
    men_data[1, i + 1] = years[i % 3]
    women_data[1, i + 1] = years[i % 3]
    men_ranks[1, i + 1] = years[i % 3]
    women_ranks[1, i + 1] = years[i % 3]

# function translates index of strokes array to match the index of the dropdown on the database
def discip_index(i):
    if i == 0:
        j = 3
    elif i < 4:
        j = i - 1
    elif i == 4:
        j = 4
    else:
        raise TypeError("input beyond boundary")
    return(j)

def create_driver():
    options = Options()
    options.add_argument("--headless")
    return webdriver.Firefox(options=options)

# Function returns the relevant time for qualifying standard calculation in 0th position, followed by the rank of that time in the 1st position.
# Does this for the current year. Use this for calculating anticipated national qual times before USMS has released the given year's top ten.

def current_year_time(driver, sex, lowerage, discipline, dist):
    driver.get("https://www.usms.org/comp/meets/toptimes.php")

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "Sex")))
        # Form inputs
        gender = Select(driver.find_element(By.NAME, "Sex"))
        stroke = Select(driver.find_element(By.NAME, "StrokeID"))
        distance = Select(driver.find_element(By.NAME, "Distance"))
        low_age = Select(driver.find_element(By.NAME, "lowage"))
        high_age = Select(driver.find_element(By.NAME, "highage"))

        # Selections
        gender.select_by_index(genders.index(sex))
        lowage_index = lower_ages.index(lowerage)
        low_age.select_by_index(lowage_index)
        high_age.select_by_index(lowage_index)
        stroke.select_by_index(discip_index(strokes.index(discipline)))
        distance.select_by_index(distances.index(dist) + 1)

        # Submit
        driver.find_element(By.XPATH, "/html/body/div[2]/div[2]/div[1]/div[2]/div[3]/div[2]/form[1]/p/input[1]").click()

        # Wait and get table
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".meet_event-rank"))
        )
        html = table.get_attribute("outerHTML")
        df = pd.read_html(html)[0]

        # Remove Nationals times and duplicates
        nationals_name = f"{str(year - 1)} U.S. Masters Swimming Spring National Championship"
        df = df[df['Meet'] != nationals_name]
        df = df.drop_duplicates(subset=['Name'])

        if df.shape[0] >= 10:
            return [df['Time'].iloc[9], 10]
        elif df.shape[0] >= 5:
            return [df['Time'].iloc[4], 5]
        elif df.shape[0] > 0:
            return [df['Time'].iloc[-1], df.shape[0]]
        else:
            return [None, 0]

    except Exception as e:
        print(f"Error fetching time for {sex} {lowerage} {dist} {discipline}: {e}")
        return [None, 0]

def fetch_time_parallel(args):
    sex, age, discipline, dist = args
    driver = create_driver()
    result = current_year_time(driver, sex, age, discipline, dist)
    driver.quit()
    return (sex, age, f"{dist} {discipline}", result)

def get_times(sex, year_of_interest, lowerage):
    url = "https://www.usms.org/comp/tt/toptenlist.php"
    payload = {
        "CourseID": "1",  # 1 = SCY
        "Year": str(year_of_interest),
        "Sex": sex[0],
        "AgeGroupID": str(lower_ages.index(lowerage) + 1)
    }

    session = rq.Session()
    res = session.post(url, data=payload)
    soup = bs(res.text, "html.parser")
    tables_html = soup.find_all("table", class_="toptenlist")

    tables = np.empty([19, 3], dtype=object)
    tables[0, :] = ["Event", "Time of interest", "Time Rank"]
    tables[1:, 0] = men_data[2:, 0]

    for i, table in enumerate(tables_html[:18]):  # Only process 18 tables
        df = pd.read_html(str(table))[0]
        if df.empty:
            continue
        tables[i + 1, 1] = str(df.iloc[-1, 5])  # Time
        tables[i + 1, 2] = int(min(df.index[-1] + 1, 10))  # Rank

    return tables

for i in range(1, len(men_data[0, :])):
    year_index = (i - 1) % 3
    age_index = (i - 1) // 3

    year = years[year_index]
    age = lower_ages[age_index]
    print(f"🧠 Working on past year age group: {age} - {roundup(age + 4) - 1}")
    men_event_table = get_times("Men", year, age)
    women_event_table = get_times("Women", year, age)
    for j in range(18):  # 18 events
        men_data[j + 2 , i] = men_event_table[j + 1, 1]
        men_ranks[j + 2, i] = men_event_table[j + 1, 2]
        women_data[j + 2 , i] = women_event_table[j + 1, 1]
        women_ranks[j + 2, i] = women_event_table[j + 1, 2]

men_data = pd.DataFrame(data=men_data[1:], columns=men_data[0])
men_ranks = pd.DataFrame(data=men_ranks[1:], columns=men_ranks[0])
women_data = pd.DataFrame(data=women_data[1:], columns=women_data[0])
women_ranks = pd.DataFrame(data=women_ranks[1:], columns=women_ranks[0])


driver = webdriver.Firefox(options=options)
tasks = []
for i in range(1, men_data.shape[1]):
    if (i - 1) % 3 == 2: # Current year
        age = lower_ages[(i -1) // 3]
        print(f"🧠 Working on current year age group: {age} - {roundup(age + 4) - 1}")
        for j in range(18):
            dist = int(men_data.iloc[j + 1, 0].split()[0])
            discipline = men_data.iloc[j + 1, 0].split()[1]
            tasks.append(("Men", age, discipline, dist))
            tasks.append(("Women", age, discipline, dist))

results = []
with ThreadPoolExecutor(max_workers=6) as executor:
    futures = [executor.submit(fetch_time_parallel, task) for task in tasks]
    for future in as_completed(futures):
        results.append(future.result())

for sex, age, event_name, (time, rank) in results:
    col_index = (lower_ages.index(age) * 3) + 3  # Find the current year column

    if sex == "Men":
        row_index = men_data[men_data.iloc[:, 0] == event_name].index[0]
        men_data.iloc[row_index, col_index] = time
        men_ranks.iloc[row_index, col_index] = rank
    else:
        row_index = women_data[women_data.iloc[:, 0] == event_name].index[0]
        women_data.iloc[row_index, col_index] = time
        women_ranks.iloc[row_index, col_index] = rank

# Track failures
missing_entries = []

# Fill results into the tables
for sex, age, event_name, (time, rank) in results:
    col_index = (lower_ages.index(age) * 3) + 3  # Find the current year column

    row_index = (men_data if sex == "Men" else women_data)[(men_data if sex == "Men" else women_data).iloc[:, 0] == event_name].index[0]

    if time:
        if sex == "Men":
            men_data.iloc[row_index, col_index] = time
            men_ranks.iloc[row_index, col_index] = rank
        else:
            women_data.iloc[row_index, col_index] = time
            women_ranks.iloc[row_index, col_index] = rank
    else:
        missing_entries.append((sex, age, event_name, row_index, col_index))

# Auto-retry missing entries
print("🔄 Retrying failed current-year lookups...")
driver = create_driver()
for sex, age, event_name, row_index, col_index in missing_entries[:]:  # copy to allow safe removal
    dist = int(event_name.split()[0])
    discipline = event_name.split()[1]
    print(f"🔁 Retrying {sex} {event_name} age {age}...")

    time_val, rank_val = current_year_time(driver, sex, age, discipline, dist)
    if time_val:
        if sex == "Men":
            men_data.iloc[row_index, col_index] = time_val
            men_ranks.iloc[row_index, col_index] = rank_val
        else:
            women_data.iloc[row_index, col_index] = time_val
            women_ranks.iloc[row_index, col_index] = rank_val

        missing_entries.remove((sex, age, event_name, row_index, col_index))

driver.quit()

# Regex pattern: matches either mm:ss.xx or ss.xx
time_pattern = re.compile(r'^(\d{1,2}:\d{2}\.\d{2}|\d{1,3}\.\d{2})$')

def is_valid_time_format(t):
    return bool(time_pattern.match(t))

def is_valid_rank_format(r):
    return r.isdigit() and 1 <= int(r) <= 10

if missing_entries:
    print("\n🧑‍💻 Manual input required for missing times:")
    for sex, age, event_name, row_index, col_index in missing_entries:
        print(f"\n❓ {sex} | Age group: {age} - {age + 5} | Event: {event_name}")

        while True:
            time_val = input("   ↪ Enter time (mm:ss.xx or ss.xx), or press Enter to skip: ").strip()
            if time_val == "":
                time_val = None
                break
            if is_valid_time_format(time_val):
                break
            else:
                print("   ❌ Invalid time format. Try again (e.g., 1:05.23 or 54.12)")

        while time_val and True:  # Only ask for rank if time_val was entered
            rank_val = input("   ↪ Enter rank (1-10), or press Enter to skip: ").strip()
            if rank_val == "":
                rank_val = None
                break
            if is_valid_rank_format(rank_val):
                rank_val = int(rank_val)
                break
            else:
                print("   ❌ Invalid rank. Enter an integer from 1 to 10.")

        if time_val:
            try:
                if sex == "Men":
                    men_data.iloc[row_index, col_index] = time_val
                    men_ranks.iloc[row_index, col_index] = rank_val
                else:
                    women_data.iloc[row_index, col_index] = time_val
                    women_ranks.iloc[row_index, col_index] = rank_val
            except Exception as e:
                print(f"❌ Failed to record manual entry: {e}")

print("🔁 Rechecking for missing data: prompting user for 5th-place fallback times where needed...")

# Use this to validate time input
def is_valid_time_format(t):
    return bool(time_pattern.match(t))

# Use this to validate rank input
def is_valid_rank_format(r):
    return r.isdigit() and 1 <= int(r) <= 10

# Helper to prompt user for manual fallback input
def prompt_user_for_fallback(sex, year, event, age_range):
    print(f"\n❓ Manual fallback required for {sex} | {event} | Age {age_range} | Year {year}")
    
    while True:
        time_val = input("   ↪ Enter 5th-place time (mm:ss.xx or ss.xx), or press Enter to skip: ").strip()
        if time_val == "":
            return None, None
        if is_valid_time_format(time_val):
            break
        print("   ❌ Invalid time format. Try again (e.g., 1:05.23 or 54.12)")

    while True:
        rank_val = input("   ↪ Enter 5th-place rank (1-5), or press Enter to skip: ").strip()
        if rank_val == "":
            return time_val, None
        if is_valid_rank_format(rank_val) and int(rank_val) <= 5:
            return time_val, int(rank_val)
        print("   ❌ Invalid rank. Enter an integer from 1 to 5.")

# Go through men and women dataframes
for df_data, df_ranks, sex in [(men_data, men_ranks, "Men"), (women_data, women_ranks, "Women")]:
    for row in range(1, df_data.shape[0]):  # skip header row
        event = df_data.iat[row, 0]
        if not isinstance(event, str):
            continue

        dist, discipline = int(event.split()[0]), event.split()[1]

        for col_group in range((df_data.shape[1] - 1) // 3):
            col_2023 = 1 + col_group * 3
            col_2024 = col_2023 + 1
            col_2025 = col_2023 + 2

            age_range = df_data.columns[col_2025]
            lower_age = int(age_range.split(" - ")[0])

            if lower_age >= 85:
                continue  # no standards for 85+

            # Check how many 10th-place ranks exist across the 3 years
            tenth_place_years = 0
            for c in [col_2023, col_2024, col_2025]:
                rank = df_ranks.iat[row, c]
                if isinstance(rank, (int, float)) and rank == 10:
                    tenth_place_years += 1

            if tenth_place_years >= 2:
                continue  # No fallback needed

            # If we get here, 5th-place fallback logic applies
            print(f"\n🛠 Fetching 5th-place fallbacks for {sex} | {event} | Age {age_range}...")

            for col, year in zip([col_2023, col_2024, col_2025], years):
                existing_rank = df_ranks.iat[row, col]

                # Only prompt if no rank or rank > 5
                if not (isinstance(existing_rank, (int, float)) and existing_rank <= 5):
                    time_val, rank_val = prompt_user_for_fallback(sex, year, event, age_range)

                    if time_val:
                        df_data.iat[row, col] = time_val
                        df_ranks.iat[row, col] = rank_val
                        print(f"   ✅ Added fallback for {year}: {time_val} (Rank {rank_val})")
                    else:
                        print(f"   ⚠️ Skipped fallback for {year} due to no input.")

men_data.to_csv("data/men_data.csv", index=False)
men_ranks.to_csv("data/men_ranks.csv", index=False)
women_data.to_csv("data/women_data.csv", index=False)
women_ranks.to_csv("data/women_ranks.csv", index=False)

print("✅ Export complete: CSV files saved.")
