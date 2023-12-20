import pandas as pd
from collections import defaultdict, Counter
<<<<<<< HEAD
from stop_words import get_stop_words
=======
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')
>>>>>>> ca0ac56 (stop word filtering for word count)


def create_graphs():
    messages =  pd.read_csv('imessages.csv',lineterminator='\n')
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

    #find most common words
    stop_words = set(stopwords.words('english'))
    words_used = Counter()
    for i in range(total_messages):
        row = messages.iloc[i]
        text = row['text']
        try:
            words = text.split()
            filtered = [w for w in words if not w.lower() in stop_words]
            words_used = words_used + Counter(filtered)
        except:
            pass
        
    #remove stop words
    stop_words = list(get_stop_words('en'))
    
    for word in stop_words:
        if word in words_used:
            words_used.pop(word)         
    
    print(words_used)


    # Prints
    print(f"Total Messages: {total_messages}")
    print(f"Total Sent: {total_sent}")
    print(f"Total Recieved: {total_recieved}")



if __name__ == "__main__":
    create_graphs()