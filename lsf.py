# Convert CSV from bank format to light standard format (lsf) specific to my uses

from dataclasses import dataclass
import csv
import re 

'''
Data format handler for an individual transaction
Description: String - Transaction description
Date: string - mm/dd/yyy 
amount: float - transacition amount
action: bool - withdrawal (0) or deposit (1)
'''
@dataclass 
class Transaction:
    description: str
    date: str
    amount: float
    is_deposit: bool

# Occasionally a bank may use a different keyword to denote the same thing. This is what that's for
_WITHDRAWAL_LIST = ["withdrawal", "purchase"]
_H_DESCRIPTION_LIST = ["description"]
_H_DATE_LIST = ["date"]
_H_AMOUNT_LIST = ["amount"]

class LSF:
    _transaction_list: list[Transaction] = []

    # Path sconstructor
    def __init__(self, path:str):
        self._read_file(path)

    # Retrieve is_deposit from regex
    def _def_action(self, desc: str) -> bool:
        _WITHDRAWAL_RE = re.compile(f".*(?:{'|'.join(_WITHDRAWAL_LIST)}).*", re.IGNORECASE)
        m = _WITHDRAWAL_RE.match(desc)
        return m is None

    def _read_file(self, path:str) -> None:
        # variable to hold the list of raw header and transaction lines
        header: list[str] = ""
        lines: list[list[str]] = []

        # Open file for reading
        with open(path, "rt") as f:
            # Grab header
            header = f.readline().lower().strip().split(',')
            # Loop over each line and split using regex 
            # Occasionally a cell will have a ',' in it so it cannot be broken using that deliminator
            _CSV_RE = re.compile(r"((\")?.*?(?(2)\"|))(?:,|$|\n)", re.IGNORECASE)
            for line in f:
                m = _CSV_RE.findall(line.lower().strip())
                lines.append([x[0] for x in m])
                
        # Identify indexes
        indexes = {"desc": -1,
                   "amount": -1,
                   "date": -1}
        for c_index, c in enumerate(header):
            # Find description if not found
            if indexes["desc"] < 0:
                for h in _H_DESCRIPTION_LIST:
                    if c.find(h) != -1:
                        indexes["desc"] = c_index
                        break
            # Find amount if not found
            if indexes["amount"] < 0:
                for h in _H_AMOUNT_LIST:
                    if c.find(h) != -1:
                        indexes["amount"] = c_index
                        break
            # Find date if not found
            if indexes["date"] < 0:
                for h in _H_DATE_LIST:
                    if c.find(h) != -1:
                        indexes["date"] = c_index
                        break
            

        # Create a transaction for each line
        for l in lines:
            self._transaction_list.append(Transaction(
                description = l[indexes["desc"]],
                is_deposit = self._def_action(l[indexes["desc"]]),
                amount=l[indexes["amount"]],
                date=l[indexes["date"]]
            ))

    def get_total_remaining(self) -> float:
        sum: float = 0

        # loop over each transaction
        for item in self._transaction_list:
            sum += float(item.amount) * (1 if item.is_deposit else -1)

        return sum
    
if __name__ == "__main__":
    lsf = LSF("C:\\Users\\Luke Deffenbaugh\\Documents\\cli-tools\\april_spend.csv")
    print(lsf.get_total_remaining())