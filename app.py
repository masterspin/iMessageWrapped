from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sqlite3
import datetime
import shutil
import json
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import string
import re
from collections import defaultdict, Counter
import json

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def calculate_average_response_time(messages_df, threshold_seconds=18000):
    messages_df['timestamp'] = pd.to_datetime(messages_df['timestamp'], unit='s')

    messages_sorted = messages_df.sort_values(by=['phone_number', 'timestamp'])
    conversations = messages_sorted.groupby('phone_number')

    average_response_times = {}  # Dictionary to store average response times

    # Iterate through each conversation
    for phone_number, conversation in conversations:
        conversation_sorted = conversation.sort_values('timestamp')

        # Filter rows where cache_roomname is null
        null_cache_conversation = conversation_sorted[conversation_sorted['cache_roomname'].isnull()]

        if null_cache_conversation.empty:
            continue  # Skip if there are no rows with cache_roomname as null

        # Calculate time differences between consecutive messages
        time_diff = null_cache_conversation['timestamp'].diff().fillna(pd.Timedelta(seconds=0))

        valid_responses = time_diff[time_diff.dt.total_seconds() <= threshold_seconds]

        # Exclude initial message
        valid_responses = valid_responses.iloc[1:]

        # Store valid response times as timedeltas in seconds
        response_times = valid_responses.dt.total_seconds()

        full_name = (null_cache_conversation['full_name'].iloc[0]) if 'full_name' in null_cache_conversation else None

        # Calculate average response time for this conversation
        if len(response_times) > 0:
            average_response_time_seconds = response_times.sum() / len(response_times)
            if pd.isnull(full_name):  # Check if full_name is NaN
                average_response_times[phone_number] = average_response_time_seconds/60
            else:
                average_response_times[full_name] = average_response_time_seconds/60
        else:
            if pd.isnull(full_name):  # Check if full_name is NaN
                average_response_times[phone_number] = None
            else:
                average_response_times[full_name] = None

    return average_response_times



def create_graphs(messages):

    # Total Messages
    total_messages = messages.shape[0]

    threshold = 43200  # For example, 1 hour threshold

    average_response = calculate_average_response_time(messages, threshold)
    print(f"Average response time: {average_response} seconds")

    # Message Sent/Rec
    total_sent = messages['is_from_me'].sum()
    total_received = total_messages - total_sent

    #Person who you've sent the most texts to (direct messaging only)
    sentDM_df = messages.loc[(messages['is_from_me'] == 1) & (messages['cache_roomname'].isnull())]
    sentDM_frequency = sentDM_df['full_name'].value_counts()
    top_3_sentDM_with_freq = [(name, freq) for name, freq in sentDM_frequency.head(3).items()]

    #Person who you've received the most texts to (direct messaging only)
    receivedDM_df = messages.loc[(messages['is_from_me'] == 0) & (messages['cache_roomname'].isnull())]
    receivedDM_frequency = receivedDM_df['full_name'].value_counts()
    top_3_receivedDM_with_freq = [(name, freq) for name, freq in receivedDM_frequency.head(3).items()]

    #Most active group chats (includes sent and received messages)
    groupChats = messages.loc[(messages['cache_roomname'].notnull())]
    groupChats_frequency = groupChats['group_chat_name'].value_counts()
    top_3_groupChats_with_freq = groupChats_frequency.head(3)
    gc_max_list = list(zip(top_3_groupChats_with_freq.index, top_3_groupChats_with_freq))

    #group chats where you were most active in (only includes sent messages)
    groupChats_sent = messages.loc[(messages['is_from_me'] == 1) & (messages['cache_roomname'].notnull())]
    groupChats_frequency_sent = groupChats_sent['group_chat_name'].value_counts()
    top_3_groupChats_sent_with_freq = groupChats_frequency_sent.head(3)
    gc_sent_max_list = list(zip(top_3_groupChats_sent_with_freq.index, top_3_groupChats_sent_with_freq))

    # Message Sent/Recieved Per Person (includes group chats)
    def default_list():
        return [0, 0]
    
    numbers = defaultdict(default_list)
    numbersSent = {}
    numbersReceived = {}

    for i in range(total_messages):
        row = messages.iloc[i]
        if(pd.isna(row["full_name"])):
            numbers[row['phone_number']][row['is_from_me']] += 1
        else:
            numbers[row["full_name"]][row['is_from_me']] += 1

    for n in numbers.keys():
        print(f"{n} : {numbers[n]}")
        numbersSent[n]=numbers[n][0]
        numbersReceived[n]=numbers[n][1]

    print(numbersSent)
    print(numbersReceived)

    game_pigeon_words = ["Word Hunt", "Anagrams", "Four in a Row", "8 Ball", "9 Ball", "Darts", "Chess", "Shuffleboard", "Word Bites", "Basketball", "Cup Pong", "Checkers", "Archery", "Miniature Golf", "Dots & Boxes"]
    game_pigeon_freq = {game: 0 for game in game_pigeon_words}

    emoji_pattern = re.compile(r'[\U0001F300-\U0001F5FF\U0001F600-\U0001F64F\U0001F680-\U0001F6FF'
                           r'\U0001F700-\U0001F77F\U0001F780-\U0001F7FF\U0001F800-\U0001F8FF'
                           r'\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U00002639\U0000263A'
                           r'\U0001F9E0-\U0001F9FF]+', flags=re.UNICODE)

    #find most common words
    extra_stopwords = ["https","good","http","ok","yes","yea","it's","its",' ',"�","0","1","2","3","4","5","6","7","8","9","0o", "0s", "3a", "3b", "3d", "6b", "6o", "a", "a1", "a2", "a3", "a4", "ab", "able", "about", "above", "abst", "ac", "accordance", "according", "accordingly", "across", "act", "actually", "ad", "added", "adj", "ae", "af", "affected", "affecting", "affects", "after", "afterwards", "ag", "again", "against", "ah", "ain", "ain't", "aj", "al", "all", "allow", "allows", "almost", "alone", "along", "already", "also", "although", "always", "am", "among", "amongst", "amoungst", "amount", "an", "and", "announce", "another", "any", "anybody", "anyhow", "anymore", "anyone", "anything", "anyway", "anyways", "anywhere", "ao", "ap", "apart", "apparently", "appear", "appreciate", "appropriate", "approximately", "ar", "are", "aren", "arent", "aren't", "arise", "around", "as", "a's", "aside", "ask", "asking", "associated", "at", "au", "auth", "av", "available", "aw", "away", "awfully", "ax", "ay", "az", "b", "b1", "b2", "b3", "ba", "back", "bc", "bd", "be", "became", "because", "become", "becomes", "becoming", "been", "before", "beforehand", "begin", "beginning", "beginnings", "begins", "behind", "being", "believe", "below", "beside", "besides", "best", "better", "between", "beyond", "bi", "bill", "biol", "bj", "bk", "bl", "bn", "both", "bottom", "bp", "br", "brief", "briefly", "bs", "bt", "bu", "but", "bx", "by", "c", "c1", "c2", "c3", "ca", "call", "came", "can", "cannot", "cant", "can't", "cause", "causes", "cc", "cd", "ce", "certain", "certainly", "cf", "cg", "ch", "changes", "ci", "cit", "cj", "cl", "clearly", "cm", "c'mon", "cn", "co", "com", "come", "comes", "con", "concerning", "consequently", "consider", "considering", "contain", "containing", "contains", "corresponding", "could", "couldn", "couldnt", "couldn't", "course", "cp", "cq", "cr", "cry", "cs", "c's", "ct", "cu", "currently", "cv", "cx", "cy", "cz", "d", "d2", "da", "date", "dc", "dd", "de", "definitely", "describe", "described", "despite", "detail", "df", "di", "did", "didn", "didn't", "different", "dj", "dk", "dl", "do", "does", "doesn", "doesn't", "doing", "don", "done", "don't", "down", "downwards", "dp", "dr", "ds", "dt", "du", "due", "during", "dx", "dy", "e", "e2", "e3", "ea", "each", "ec", "ed", "edu", "ee", "ef", "effect", "eg", "ei", "eight", "eighty", "either", "ej", "el", "eleven", "else", "elsewhere", "em", "empty", "en", "end", "ending", "enough", "entirely", "eo", "ep", "eq", "er", "es", "especially", "est", "et", "et-al", "etc", "eu", "ev", "even", "ever", "every", "everybody", "everyone", "everything", "everywhere", "ex", "exactly", "example", "except", "ey", "f", "f2", "fa", "far", "fc", "few", "ff", "fi", "fifteen", "fifth", "fify", "fill", "find", "fire", "first", "five", "fix", "fj", "fl", "fn", "fo", "followed", "following", "follows", "for", "former", "formerly", "forth", "forty", "found", "four", "fr", "from", "front", "fs", "ft", "fu", "full", "further", "furthermore", "fy", "g", "ga", "gave", "ge", "get", "gets", "getting", "gi", "give", "given", "gives", "giving", "gj", "gl", "go", "goes", "going", "gone", "got", "gotten", "gr", "greetings", "gs", "gy", "h", "h2", "h3", "had", "hadn", "hadn't", "happens", "hardly", "has", "hasn", "hasnt", "hasn't", "have", "haven", "haven't", "having", "he", "hed", "he'd", "he'll", "hello", "help", "hence", "her", "here", "hereafter", "hereby", "herein", "heres", "here's", "hereupon", "hers", "herself", "hes", "he's", "hh", "hi", "hid", "him", "himself", "his", "hither", "hj", "ho", "home", "hopefully", "how", "howbeit", "however", "how's", "hr", "hs", "http", "hu", "hundred", "hy", "i", "i2", "i3", "i4", "i6", "i7", "i8", "ia", "ib", "ibid", "ic", "id", "i'd", "ie", "if", "ig", "ignored", "ih", "ii", "ij", "il", "i'll", "im", "i'm", "immediate", "immediately", "importance", "important", "in", "inasmuch", "inc", "indeed", "index", "indicate", "indicated", "indicates", "information", "inner", "insofar", "instead", "interest", "into", "invention", "inward", "io", "ip", "iq", "ir", "is", "isn", "isn't", "it", "itd", "it'd", "it'll", "its", "it's", "itself", "iv", "i've", "ix", "iy", "iz", "j", "jj", "jr", "js", "jt", "ju", "just", "k", "ke", "keep", "keeps", "kept", "kg", "kj", "km", "know", "known", "knows", "ko", "l", "l2", "la", "largely", "last", "lately", "later", "latter", "latterly", "lb", "lc", "le", "least", "les", "less", "lest", "let", "lets", "let's", "lf", "like", "liked", "likely", "line", "little", "lj", "ll", "ll", "ln", "lo", "look", "looking", "looks", "los", "lr", "ls", "lt", "ltd", "m", "m2", "ma", "made", "mainly", "make", "makes", "many", "may", "maybe", "me", "mean", "means", "meantime", "meanwhile", "merely", "mg", "might", "mightn", "mightn't", "mill", "million", "mine", "miss", "ml", "mn", "mo", "more", "moreover", "most", "mostly", "move", "mr", "mrs", "ms", "mt", "mu", "much", "mug", "must", "mustn", "mustn't", "my", "myself", "n", "n2", "na", "name", "namely", "nay", "nc", "nd", "ne", "near", "nearly", "necessarily", "necessary", "need", "needn", "needn't", "needs", "neither", "never", "nevertheless", "new", "next", "ng", "ni", "nine", "ninety", "nj", "nl", "nn", "no", "nobody", "non", "none", "nonetheless", "noone", "nor", "normally", "nos", "not", "noted", "nothing", "novel", "now", "nowhere", "nr", "ns", "nt", "ny", "o", "oa", "ob", "obtain", "obtained", "obviously", "oc", "od", "of", "off", "often", "og", "oh", "oi", "oj", "ok", "okay", "ol", "old", "om", "omitted", "on", "once", "one", "ones", "only", "onto", "oo", "op", "oq", "or", "ord", "os", "ot", "other", "others", "otherwise", "ou", "ought", "our", "ours", "ourselves", "out", "outside", "over", "overall", "ow", "owing", "own", "ox", "oz", "p", "p1", "p2", "p3", "page", "pagecount", "pages", "par", "part", "particular", "particularly", "pas", "past", "pc", "pd", "pe", "per", "perhaps", "pf", "ph", "pi", "pj", "pk", "pl", "placed", "please", "plus", "pm", "pn", "po", "poorly", "possible", "possibly", "potentially", "pp", "pq", "pr", "predominantly", "present", "presumably", "previously", "primarily", "probably", "promptly", "proud", "provides", "ps", "pt", "pu", "put", "py", "q", "qj", "qu", "que", "quickly", "quite", "qv", "r", "r2", "ra", "ran", "rather", "rc", "rd", "re", "readily", "really", "reasonably", "recent", "recently", "ref", "refs", "regarding", "regardless", "regards", "related", "relatively", "research", "research-articl", "respectively", "resulted", "resulting", "results", "rf", "rh", "ri", "right", "rj", "rl", "rm", "rn", "ro", "rq", "rr", "rs", "rt", "ru", "run", "rv", "ry", "s", "s2", "sa", "said", "same", "saw", "say", "saying", "says", "sc", "sd", "se", "sec", "second", "secondly", "section", "see", "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sensible", "sent", "serious", "seriously", "seven", "several", "sf", "shall", "shan", "shan't", "she", "shed", "she'd", "she'll", "shes", "she's", "should", "shouldn", "shouldn't", "should've", "show", "showed", "shown", "showns", "shows", "si", "side", "significant", "significantly", "similar", "similarly", "since", "sincere", "six", "sixty", "sj", "sl", "slightly", "sm", "sn", "so", "some", "somebody", "somehow", "someone", "somethan", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry", "sp", "specifically", "specified", "specify", "specifying", "sq", "sr", "ss", "st", "still", "stop", "strongly", "sub", "substantially", "successfully", "such", "sufficiently", "suggest", "sup", "sure", "sy", "system", "sz", "t", "t1", "t2", "t3", "take", "taken", "taking", "tb", "tc", "td", "te", "tell", "ten", "tends", "tf", "th", "than", "thank", "thanks", "thanx", "that", "that'll", "thats", "that's", "that've", "the", "their", "theirs", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "thered", "therefore", "therein", "there'll", "thereof", "therere", "theres", "there's", "thereto", "thereupon", "there've", "these", "they", "theyd", "they'd", "they'll", "theyre", "they're", "they've", "thickv", "thin", "think", "third", "this", "thorough", "thoroughly", "those", "thou", "though", "thoughh", "thousand", "three", "throug", "through", "throughout", "thru", "thus", "ti", "til", "tip", "tj", "tl", "tm", "tn", "to", "together", "too", "took", "top", "toward", "towards", "tp", "tq", "tr", "tried", "tries", "truly", "try", "trying", "ts", "t's", "tt", "tv", "twelve", "twenty", "twice", "two", "tx", "u", "u201d", "ue", "ui", "uj", "uk", "um", "un", "under", "unfortunately", "unless", "unlike", "unlikely", "until", "unto", "uo", "up", "upon", "ups", "ur", "us", "use", "used", "useful", "usefully", "usefulness", "uses", "using", "usually", "ut", "v", "va", "value", "various", "vd", "ve", "ve", "very", "via", "viz", "vj", "vo", "vol", "vols", "volumtype", "vq", "vs", "vt", "vu", "w", "wa", "want", "wants", "was", "wasn", "wasnt", "wasn't", "way", "we", "wed", "we'd", "welcome", "well", "we'll", "well-b", "went", "were", "we're", "weren", "werent", "weren't", "we've", "what", "whatever", "what'll", "whats", "what's", "when", "whence", "whenever", "when's", "where", "whereafter", "whereas", "whereby", "wherein", "wheres", "where's", "whereupon", "wherever", "whether", "which", "while", "whim", "whither", "who", "whod", "whoever", "whole", "who'll", "whom", "whomever", "whos", "who's", "whose", "why", "why's", "wi", "widely", "will", "willing", "wish", "with", "within", "without", "wo", "won", "wonder", "wont", "won't", "words", "world", "would", "wouldn", "wouldnt", "wouldn't", "www", "x", "x1", "x2", "x3", "xf", "xi", "xj", "xk", "xl", "xn", "xo", "xs", "xt", "xv", "xx", "y", "y2", "yes", "yet", "yj", "yl", "you", "youd", "you'd", "you'll", "your", "youre", "you're", "yours", "yourself", "yourselves", "you've", "yr", "ys", "yt", "z", "zero", "zi", "zz"]
    words_used = Counter()
    emojis_used = Counter()
    for i in range(total_messages):
        row = messages.iloc[i]
        text = row['text']
        if(row['is_from_me'] == 1):
            emojis = re.findall(emoji_pattern, text)
            emojis_used.update(emojis)
            try:
                if(text not in game_pigeon_words):
                    words = re.findall(r'\b\w+\b', text.lower())
                    filtered = [w for w in words if not w.lower() in extra_stopwords]
                    words_used = words_used + Counter(filtered)
                else:
                    game_pigeon_freq[text]+=1
            except:
                pass
        else:
            if(text in game_pigeon_words):
                game_pigeon_freq[text]+=1
        
    #remove stop words
    most_common_emojis = emojis_used.most_common(5)
    print("Most Common Emojis:")
    for emoji, count in most_common_emojis:
        print(f"{emoji}: {count}")       

    for char in string.punctuation:
        if char in words_used:
            words_used.pop(char)      


    print(words_used.most_common(10))


    # Prints
    medals = ["🥇", "🥈", "🥉"]

    print(f"\nTotal Messages: {total_messages}")
    print(f"Total Sent: {total_sent}")
    print(f"Total Recieved: {total_received}")

    print("")

    sorted_game_pigeon_freq = {k: v for k, v in sorted(game_pigeon_freq.items(), key=lambda item: item[1], reverse=True) if v > 0}
    print(sorted_game_pigeon_freq)
    for game, frequency in sorted_game_pigeon_freq.items():
        print(f"You've played {frequency} games of {game}")

    for i in range(len(top_3_sentDM_with_freq)):
        print(f"{medals[i]} You sent {top_3_sentDM_with_freq[i][1]} messages to", top_3_sentDM_with_freq[i][0])
    
    print("")
    for i in range(len(top_3_receivedDM_with_freq)):
        print(f"{medals[i]} You received {top_3_receivedDM_with_freq[i][1]} messages from", top_3_receivedDM_with_freq[i][0])
    
    print("")
    for i in range(len(gc_max_list)):
        print(f"{medals[i]} #{i+1} most active group chat:", gc_max_list[i][0])
    
    print("")
    for i in range(len(gc_sent_max_list)):
        print(f"{medals[i]} #{i+1} group chat you were most active in:", gc_sent_max_list[i][0])
    

    # Convert the plot to HTML (or JSON) representation
##########just add it if it's available
    response = {
        "total_messages": int(total_messages),
        "total_sent": int(total_sent),
        "total_received": int(total_received),
        "top_3_sentDM_with_freq": [
            {"name": name, "frequency": freq} for name, freq in top_3_sentDM_with_freq
        ],
        "top_3_receivedDM_with_freq": [
            {"name": name, "frequency": freq} for name, freq in top_3_receivedDM_with_freq
        ],
        "top_3_groupChats_with_freq": [
            {"name": name, "frequency": freq} for name, freq in top_3_groupChats_with_freq.items()
        ],
        "top_3_groupChats_sent_with_freq": [
            {"name": name, "frequency": freq} for name, freq in top_3_groupChats_sent_with_freq.items()
        ],
        "averageResponse": average_response,
        "numbersSent": numbersSent,
        "numbersReceived": numbersReceived,
        "common_words": [{"word": word, "count": count} for word, count in words_used.most_common(5)],
        "common_emojis": [{"emoji": emoji, "count": count} for emoji, count in emojis_used.most_common(3)],
        
    }
    if(len(sorted_game_pigeon_freq) > 0):
        response["gamePigeonData"] = sorted_game_pigeon_freq
    
    return json.dumps(response)
    



def get_first_name_from_phone(phone_number, address_book):
    # Convert JSON-formatted address book to a list of dictionaries
    address_book_list = json.loads(address_book)
    # print(address_book_list)

    # print(phone_number)

    for contact in address_book_list:
        if "NUMBERCLEAN" in contact and contact["NUMBERCLEAN"] == phone_number:
            # print(phone_number)
            return contact.get("FIRSTNAME", "")

    return None

def get_chat_mapping(db_location, addressBookData):
    conn = sqlite3.connect(db_location)
    cursor = conn.cursor()

    cursor.execute("SELECT ROWID, room_name, display_name FROM chat")
    chat_result_set = cursor.fetchall()

    mapping = {}
    for row in chat_result_set:
        chat_id, room_name, display_name = row

        # Check if display_name is None or empty
        if display_name is None or display_name.strip() == '':
            # If display_name is not available or empty, try to gather participants' phone numbers
            cursor.execute("""
                SELECT handle.id FROM chat_handle_join
                JOIN handle ON chat_handle_join.handle_id = handle.ROWID
                WHERE chat_handle_join.chat_id = ?
            """, (chat_id,))
            participants_result = cursor.fetchall()
            participants_numbers = [str(participant[0]) for participant in participants_result]
            if participants_numbers:
                # If there are phone numbers, try to get first names from the address book
                first_names = []
                for participant in participants_numbers:
                    # Look up the first name from the address book based on the participant's phone number
                    # Assume get_first_name_from_phone is a function that extracts the first name based on phone number
                    if len(participant) == 10:
                        participant = "+1" + participant
                    elif len(participant) == 11:
                        participant = "+" + participant
                    # print(participant)
                    first_name = get_first_name_from_phone(participant, addressBookData)
                    # print("first name: ", first_name)
                    if first_name:
                        first_names.append(first_name)
                    else:
                        first_names.append(participant)

                # If there are any first names, create a combined name string, otherwise keep the phone numbers
                if first_names:
                    mapping[room_name] = ', '.join(first_names)
                else:
                    mapping[room_name] = ', '.join(participants_numbers)
        else:
            mapping[room_name] = display_name

    conn.close()

    return mapping

# Function to read messages from a sqlite database
def read_messages(db_location, addressBookData, self_number='Me', human_readable_date=True):
    # Connect to the database and execute a query to join message and handle tables
    conn = sqlite3.connect(db_location)
    cursor = conn.cursor()
    query = """
    SELECT message.ROWID, message.date, message.text, message.attributedBody, handle.id, message.is_from_me, message.cache_roomnames
    FROM message
    LEFT JOIN handle ON message.handle_id = handle.ROWID
    """
    
    query += f"  WHERE message.date >= 694224000000000000 ORDER BY message.date DESC"
    results = cursor.execute(query).fetchall()

    this_year = 0
    
    messages = []

    loop_count = 0

    for result in results:
        rowid, date, text, attributed_body, handle_id, is_from_me, cache_roomname = result

        unix=None

        # Use self_number or handle_id as phone_number depending on whether it's a self-message or not
        phone_number = self_number if handle_id is None else handle_id


        # Use text or attributed_body as body depending on whether it's a plain text or rich media message
        if text is not None:
            body = text
        
        elif attributed_body is None: 
            continue
        
        else: 
            # Decode and extract relevant information from attributed_body using string methods 
            attributed_body = attributed_body.decode('utf-8', errors='replace')
            if "NSNumber" in str(attributed_body):
                attributed_body = str(attributed_body).split("NSNumber")[0]
                if "NSString" in attributed_body:
                    attributed_body = str(attributed_body).split("NSString")[1]
                    if "NSDictionary" in attributed_body:
                        attributed_body = str(attributed_body).split("NSDictionary")[0]
                        attributed_body = attributed_body[6:-12]
                        body = attributed_body
        # Convert date from Apple epoch time to standard format using datetime module if human_readable_date is True  
        if human_readable_date:
            date_string = '2001-01-01'
            mod_date = datetime.datetime.strptime(date_string, '%Y-%m-%d')
            unix_timestamp = int(mod_date.timestamp())*1000000000
            new_date = int((date+unix_timestamp)/1000000000)
            unix = int(new_date)
            date = datetime.datetime.fromtimestamp(new_date).strftime("%Y-%m-%d %H:%M:%S")
            # if date[:4] != '2023':  # Check the year in the formatted date
            #     break
        
        this_year+=1

        loop_count +=1

        mapping = get_chat_mapping(db_location, addressBookData)  # Get chat mapping from database location

        try:
            mapped_name = mapping[cache_roomname]
        except:
            mapped_name = None
            
        messages.append(
            {"date": date, "text": body, "phone_number": phone_number, "is_from_me": is_from_me,
             "cache_roomname": cache_roomname, 'group_chat_name' : mapped_name, 'timestamp':unix})

    conn.close()
    return messages

def get_address_book(address_book_location):
    conn = sqlite3.connect(address_book_location)
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT ZABCDRECORD.ZFIRSTNAME [FIRST NAME], ZABCDRECORD.ZLASTNAME [LAST NAME], ZABCDPHONENUMBER.ZFULLNUMBER [FULL NUMBER] FROM ZABCDRECORD LEFT JOIN ZABCDPHONENUMBER ON ZABCDRECORD.Z_PK = ZABCDPHONENUMBER.ZOWNER ORDER BY ZABCDRECORD.ZLASTNAME, ZABCDRECORD.ZFIRSTNAME, ZABCDPHONENUMBER.ZORDERINGINDEX ASC")
    result_set = cursor.fetchall()

    #Convert tuples to json
    json_output = json.dumps([{"FIRSTNAME": t[0], "LASTNAME": t[1], "FULLNUMBER": t[2]} for t in result_set])
    json_list = json.loads(json_output)
    conn.close()

    for obj in json_list:
        # Get the phone number from the object
        phone = obj["FULLNUMBER"]
        if phone is None:
            continue
        # Remove all non-numeric characters from the phone number
        phone = "".join([c for c in phone if c.isnumeric()])
        #if the phone number is 10 digits, add "+1" to the beginning, if it's 11 digits, add "+"
        if len(phone) == 10:
            phone = "+1" + phone
        elif len(phone) == 11:
            phone = "+" + phone
        # Add the phone number to the object
        obj["NUMBERCLEAN"] = phone
        
    new_json_output = json.dumps(json_list)
    return new_json_output

#combine recent messages and address book data
def combine_data(recent_messages, addressBookData):
    #convert addressBookData to a list of dictionaries
    addressBookData = json.loads(addressBookData)
    #loop through each message
    for message in recent_messages:
        phone_number = message["phone_number"]
        for contact in addressBookData:
            # if contact does not have property NUMBERCLEAN, skip it
            if "NUMBERCLEAN" not in contact:
                continue
            else:
                contact_number = contact["NUMBERCLEAN"]
            #if the phone number from the message matches the phone number from the contact add the names to the message
            if phone_number == contact_number:
                first_name = contact["FIRSTNAME"]
                last_name = contact["LASTNAME"]

                if last_name:
                    full_name = f"{first_name} {last_name}"
                else:
                    full_name = first_name
                message["first_name"] = first_name
                message["last_name"] = last_name
                message["full_name"] = full_name
    return recent_messages

#on continue button click
def button_click():

    #location of the database
    db_location = "./uploads/chat.db"

    #location of the addressbook
    address_book_location = "./uploads/AddressBook-v22.abcddb"
    addressBookData = None
    recent_messages = None
    combined_data = None
    filtered_data = None
    try:
        addressBookData = get_address_book(address_book_location)
    except Exception as e:
        return jsonify({'error': f'Error fetching address book: {str(e)}'}), 500
    
    try:
        recent_messages = read_messages(db_location, addressBookData)
    except Exception as e:
        return jsonify({'error': f'Error fetching messages: {str(e)}'}), 500
    
    try:
         combined_data = combine_data(recent_messages, addressBookData)
    except Exception as e:
        return jsonify({'error': f'Error combining data: {str(e)}'}), 500
    
    try:
        filtered_data = [message for message in combined_data if message['date'][:4] == '2023']
    except Exception as e:
        return jsonify({'error': f'Error filtering data: {str(e)}'}), 500
    print("here")

    return create_graphs(pd.DataFrame(filtered_data))

   


@app.route('/upload', methods=['POST'])
def upload_file():
    deleteFolder = './uploads'
    if os.path.exists(deleteFolder):
        try:
            # Use shutil.rmtree to delete the folder and its contents recursively
            shutil.rmtree(deleteFolder)
            print('Folder deleted successfully')
        except OSError as e:
            # Handle any errors that occur during folder deletion
            print(f'Error: {e}')
    else:
        print('Folder does not exist')
    
    if 'fileOne' not in request.files or 'fileTwo' not in request.files:
        return 'No file uploaded', 400

    file_one = request.files['fileOne']
    file_two = request.files['fileTwo']

    if file_one.filename == '' or file_two.filename == '':
        return 'No selected file', 400

    # Ensure the 'uploads' directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Save fileOne and fileTwo to the 'uploads' directory
    file_one.save(os.path.join(app.config['UPLOAD_FOLDER'], file_one.filename))
    file_two.save(os.path.join(app.config['UPLOAD_FOLDER'], file_two.filename))

    return 'Files uploaded successfully'

@app.route('/analyze', methods=['GET'])
def analyze():
    return button_click()  # Call your function when this endpoint is hit

if __name__ == '__main__':
    app.run(debug=True)