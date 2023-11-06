import re
regex = [r'(\d+(\.\d+)?) wh', r'(\d+(\.\d+)?)wh', r'(\d+(\.\d+)?)-watt', r'(\d+(\.\d+)?) whrs',
         r'(\d+(\.\d+)?)whrs', r'(\d+(\.\d+)?)whr', r'(\d+(\.\d+)?) whr']

battery = '3-cell 56.6Wh, Lithium Polymer'

for r in regex:
    match = re.search(r, battery.lower())
    if match:
        print(match.group(1))
        break
