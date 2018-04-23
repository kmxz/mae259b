import json

result = json.load(open('data/mid_a.json'))

ymax = 0.0

for step in result:
    for i in range(0, len(step['data']), 2):
        y = abs(step['data'][i + 1])
        if y > ymax:
            ymax = y

print("Maximum deflection %f" % ymax)