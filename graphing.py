import pandas as pd
from collections import defaultdict

def create_graphs():
    messages =  pd.read_csv('imessages.csv')
    # print(messages.head())

    # Total Messages
    total_messages = messages.shape[0]

    # Message Sent/Rec
    total_sent = messages['is_sent'].sum()
    total_recieved = total_messages - total_sent

    # Message Sent/Recieved Per Person
    def default_list():
        return [0, 0]
    
    numbers = defaultdict(default_list)

    for i in range(total_messages):
        row = messages.iloc[i]
        numbers[row['phone_number']][row['is_sent']] += 1

    for n in numbers.keys():
        print(f"{n} : {numbers[n]}")

    # Prints
    print(f"Total Messages: {total_messages}")
    print(f"Total Sent: {total_sent}")
    print(f"Total Recieved: {total_recieved}")



if __name__ == "__main__":
    create_graphs()