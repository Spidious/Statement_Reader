from lsf import LSF
import yaml

'''
Application run from here but will constantly be broken into several files
'''

# Create statement lsf data object
statement = LSF("C:\\Users\\Luke Deffenbaugh\\Documents\\cli-tools\\april_spend.csv")

# Pull config data
with open('config.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.SafeLoader)

# Initialize the transaction categories to 0
for key in config['transaction-category'].keys():
    config['transaction-category'][key] = 0

for t in statement.get_transactions():
    user_in = input(t.amount + " : " + t.description + f"\n{[x + f" ({x[:2]})" for x in config['transaction-category'].keys()]}: ")
    if user_in == "":
        continue


print(config)
