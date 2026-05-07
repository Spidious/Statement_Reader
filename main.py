from lsf import LSF
import yaml
import plotly.express as px
import random

'''
Application run from here but will constantly be broken into several files
'''

# Create statement lsf data object
statement = LSF("C:\\Users\\Luke Deffenbaugh\\Documents\\cli-tools\\april_spend.csv")

# Pull config data
with open('config.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

# Initialize the transaction categories to 0
totals = {}
for key in config['transaction-category']:
    totals[key[:3]] = 0.0

for t in statement.get_transactions():
    user_in = input("\n" + t.amount + " : " + t.description + f"\n{[x + f" ({x[:3]})" for x in config['transaction-category']]}: ")
    # Temporary user in so I don't have to do this every time I test it
    # user_in = random.choice(list(totals.keys()))
    if user_in == "":
        continue
    totals[user_in] += float(t.amount)

fig = px.pie(values=totals.values(), names=totals.keys())
fig.show()
while(True):
    pass
