from web3 import Web3
import csv

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))

accounts = w3.eth.accounts

with open("balances.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Address", "ETH Balance"])

    for acc in accounts:
        balance = w3.eth.get_balance(acc)
        writer.writerow([acc, balance])

print("CSV exported!")
