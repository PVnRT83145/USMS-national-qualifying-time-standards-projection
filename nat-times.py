# Make sure that pull-times.py has been run, and the CSV files are up to date before running this script
# Below link gives USMS guidlines on how NQTs are caclulated based on times from the previous years.
# https://www-usms-hhgdctfafngha6hr.z01.azurefd.net/-/media/usms/pdfs/pool%20national%20championships/national%20qualifying%20times%20frequently%20asked%20questions.pdf?rev=e12f6e7f006146149badbfa70e7030bd&hash=91EF8A1CC21104E3FC063C68424DC4AD&hash=91EF8A1CC21104E3FC063C68424DC4AD
import pandas as pd, numpy as np, math
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime as dt

year  =  dt.now().year

men_times, men_ranks, women_times, women_ranks = [pd.read_csv("data/men_data.csv"),pd.read_csv("data/men_ranks.csv"),pd.read_csv("data/women_data.csv"),pd.read_csv("data/women_ranks.csv")]
men_qts = men_times[[col for col in men_times.columns if '.' not in col]].copy()
men_qts.iloc[:, 1:] = None
men_qts = men_qts.iloc[1:]
men_qts.rename(columns={'Unnamed: 0': 'Event'}, inplace=True)
women_qts = men_qts.copy()
men_ranks.rename(columns={'Unnamed: 0': 'Event'}, inplace=True)
women_ranks.rename(columns={'Unnamed: 0': 'Event'}, inplace=True)
ages = ['18 - 24']
for i in range(12):
    ages.append(str(5 * (i + 5)) + ' - ' + str((5 * (i +5)) + 4))

def is_finite_float(s):
    
    try:
        val = float(s)
        return math.isfinite(val)
    except ValueError:
        return False

def sec(str):
    
    if ":" in str:
        minutes, seconds = str.split(":")
        return int(minutes) * 60 + float(seconds)             
    elif is_finite_float(str):
        return float(str)
    else:
        return None

def minsec(t):
    
    try:
        if t >= 60:
            minutes = int(t // 60)
            sec = t % 60
            return f"{minutes}:{sec:05.2f}"
        else:
            return f"{t:.2f}"
    except:
        raise ValueError("input to minsec function must be a number")

def multiplier(sex, age_group, event):
    
    if sex == "Men":
        row_index = men_ranks[men_ranks['Event'] == event].index[0]
        rank1 = men_ranks.at[row_index, age_group]
        rank2 = men_ranks.at[row_index, age_group + '.1']
        rank3 = men_ranks.at[row_index, age_group + '.2']
    elif sex == "Women":
        row_index = men_ranks[men_ranks['Event'] == event].index[0]
        rank1 = women_ranks.at[row_index, age_group]
        rank2 = women_ranks.at[row_index, age_group + '.1']
        rank3 = women_ranks.at[row_index, age_group + '.2']
    else:
        raise ValueError('''input of "sex" to multiplier must be either "Men" or "Women"''')

    if sum([rank1 == 10, rank2 == 10, rank3 == 10]) >= 2:
        dist = int(event.split(" ")[0])
        if dist < 200:
            return 1.15
        else:
            return 1.1
    elif sum([5 <= rank1 <= 10, 5 <= rank2 <= 10, 5 <= rank3 <= 10]) >= 2:
        dist = int(event.split(" ")[0])
        if dist < 200:
            return 1.2
        else:
            return 1.15
    else:
        return "No Time"

def grab_times(sex, age_group, event):
    try:
        mult = multiplier(sex, age_group, event)
        
        if mult == "No Time":
                return "NO TIME"
    
    
        if sex == "Men":
            row_index = men_ranks[men_ranks['Event'] == event].index[0]
            time1 = men_times.at[row_index, age_group]
            time2 = men_times.at[row_index, age_group + '.1']
            time3 = men_times.at[row_index, age_group + '.2']
        elif sex == "Women":
            row_index = men_ranks[men_ranks['Event'] == event].index[0]
            time1 = women_times.at[row_index, age_group]
            time2 = women_times.at[row_index, age_group + '.1']
            time3 = women_times.at[row_index, age_group + '.2']
        else:
            raise ValueError('''input of "sex" to grab_times must either be "Men" or "Women"''')
        data = [time1, time2, time3]
        converted_data = [sec(x) for x in data]
        filtered_data = [x for x in converted_data if isinstance(x, (int, float))]        
        mean = np.average(converted_data)
        return minsec(mult * mean)
    except:
        raise ValueError('''Confirm input to grab_times function is correct. All inputs must be strings. The first input must be a gender, the second input must be an age group and the third must be a valid event''')


for row_index, row in men_qts.iterrows():
    for col_name in men_qts.columns:
        try:
            men_qts.at[row_index, col_name] = grab_times("Men", col_name, men_qts.at[row_index, 'Event'])
            women_qts.at[row_index, col_name] = grab_times("Women", col_name, men_qts.at[row_index, 'Event'])
        except:
            continue

men_markdown = men_qts.to_markdown(index=False)
women_markdown = women_qts.to_markdown(index=False)

with open(f"results/{year + 1} Anticipated National Qualifying Times for Men (SCY).md", "w") as f:
    f.write(men_markdown)

with open(f"results/{year + 1} Anticipated National Qualifying Times for Women (SCY).md", "w") as f:
    f.write(women_markdown)

print(men_qts)
print(women_qts)