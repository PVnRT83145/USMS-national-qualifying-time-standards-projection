# USMS-national-qualifying-time-standards-projection
Determines qualifying times for upcoming USMS national championchip meets. The existing code is only intended to work for spring nationals (SCY)
***You'll need to install all of the required dependencies and create folders titled "results" and "data" but without the quotes in the same directory that you're running pull-times.py and nat-times.py from***

*The dependencies for each script should be at the start. There are no import statements in either script after the initial block if memory serves*

**DISCLAIMER: I make no claims about the accuracy of these times. This is merely prediction and the times published by USMS will likely be near these times but may not neccessarily match**

Run pull-times.py after initiating the virtual environment. This script is pretty slow. If you're running on a machine with less than 32 GB of RAM, then I'd consider tweaking the max_workers value on line 215

pull-times.py uses the get_times function to scrape the relevant times from the top ten lists at https://www.usms.org/comp/tt/toptenlist.php for the previous two years. Unfortunately, due to the release schedule of the top ten times, the current year isn't available. To combat this, the current_year_time function accesses times from the current year from https://www.usms.org/comp/meets/toptimes.php. In doing so, it automatically removes entries from 2024 nationals and duplicate times from the same swimmer before determining what will be the 10th place time. This is much slower because this has to be done via selenium as the meet database uses some javascript implementation. Because of this future improvement plans would be to check to see if the current year top ten list is out before pulling the times from the meet database

following the initial loops throught the event and age space with current_year_time and get_times, the script then check the existing data to see what was missed by selenium on the first pass and tries again to see if it can pull it from the website. Any events that yeild multiple failures will cause the script to prompt the user to manually input the appropriate data for that event. 

After this, the script then checks through all the times to see if it needs to fall back to 5th place times for events that don't have enough 10th place times for the calculation. Unfortunately I couldn't find a good way to implement this automatically, especially with selenium, so all of these entries are done by prompting the user to input them. This would be an improvement project for the future as well.

following this, pull-times.py saves the data need for calculation of national qualifying times as four separate CSVs detailing the relevant times for each sex, and the rank corresponding to each time, for each sex.

After running pull-time.py, run nat-times.py. This calculates all of the NQTs and then outputs them as two separate markdown files for copy/pasting abroad. 


