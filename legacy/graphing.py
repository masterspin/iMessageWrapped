import pandas as pd
import string
import re
from collections import defaultdict, Counter
from stop_words import get_stop_words
import nltk
from nltk.corpus import stopwords
nltk.download('stopwords')

def create_graphs():
    messages =  pd.read_csv('output.csv',lineterminator='\n')
    # print(messages.head())

    # Total Messages
    total_messages = messages.shape[0]

    # Message Sent/Rec
    total_sent = messages['is_from_me'].sum()
    total_recieved = total_messages - total_sent

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

    for i in range(total_messages):
        row = messages.iloc[i]
        if(pd.isna(row["full_name"])):
            numbers[row['phone_number']][row['is_from_me']] += 1
        else:
            numbers[row["full_name"]][row['is_from_me']] += 1

    for n in numbers.keys():
        print(f"{n} : {numbers[n]}")

    game_pigeon_words = ["Word Hunt", "Anagrams", "Four in a Row", "8 Ball", "9 Ball", "Darts", "Chess", "Shuffleboard", "Word Bites", "Basketball", "Cup Pong", "Checkers", "Archery", "Miniature Golf", "Dots & Boxes"]
    game_pigeon_freq = {game: 0 for game in game_pigeon_words}

    #find most common words
    stop_words = set(stopwords.words('english'))
    words_used = Counter()
    for i in range(total_messages):
        row = messages.iloc[i]
        text = row['text']
        try:
            if(text not in game_pigeon_words):
                words = re.findall(r'\b\w+\b', text.lower())
                filtered = [w for w in words if not w.lower() in stop_words]
                words_used = words_used + Counter(filtered)
            else:
                game_pigeon_freq[text]+=1
        except:
            pass
        
    #remove stop words
    stop_words = list(get_stop_words('en'))
    
    for word in stop_words:
        if word in words_used:
            words_used.pop(word)        
    
    extra_stopwords = ["https","good","http","ok","yes","yea","it's","its",' ',"�","0","1","2","3","4","5","6","7","8","9","0o", "0s", "3a", "3b", "3d", "6b", "6o", "a", "a1", "a2", "a3", "a4", "ab", "able", "about", "above", "abst", "ac", "accordance", "according", "accordingly", "across", "act", "actually", "ad", "added", "adj", "ae", "af", "affected", "affecting", "affects", "after", "afterwards", "ag", "again", "against", "ah", "ain", "ain't", "aj", "al", "all", "allow", "allows", "almost", "alone", "along", "already", "also", "although", "always", "am", "among", "amongst", "amoungst", "amount", "an", "and", "announce", "another", "any", "anybody", "anyhow", "anymore", "anyone", "anything", "anyway", "anyways", "anywhere", "ao", "ap", "apart", "apparently", "appear", "appreciate", "appropriate", "approximately", "ar", "are", "aren", "arent", "aren't", "arise", "around", "as", "a's", "aside", "ask", "asking", "associated", "at", "au", "auth", "av", "available", "aw", "away", "awfully", "ax", "ay", "az", "b", "b1", "b2", "b3", "ba", "back", "bc", "bd", "be", "became", "because", "become", "becomes", "becoming", "been", "before", "beforehand", "begin", "beginning", "beginnings", "begins", "behind", "being", "believe", "below", "beside", "besides", "best", "better", "between", "beyond", "bi", "bill", "biol", "bj", "bk", "bl", "bn", "both", "bottom", "bp", "br", "brief", "briefly", "bs", "bt", "bu", "but", "bx", "by", "c", "c1", "c2", "c3", "ca", "call", "came", "can", "cannot", "cant", "can't", "cause", "causes", "cc", "cd", "ce", "certain", "certainly", "cf", "cg", "ch", "changes", "ci", "cit", "cj", "cl", "clearly", "cm", "c'mon", "cn", "co", "com", "come", "comes", "con", "concerning", "consequently", "consider", "considering", "contain", "containing", "contains", "corresponding", "could", "couldn", "couldnt", "couldn't", "course", "cp", "cq", "cr", "cry", "cs", "c's", "ct", "cu", "currently", "cv", "cx", "cy", "cz", "d", "d2", "da", "date", "dc", "dd", "de", "definitely", "describe", "described", "despite", "detail", "df", "di", "did", "didn", "didn't", "different", "dj", "dk", "dl", "do", "does", "doesn", "doesn't", "doing", "don", "done", "don't", "down", "downwards", "dp", "dr", "ds", "dt", "du", "due", "during", "dx", "dy", "e", "e2", "e3", "ea", "each", "ec", "ed", "edu", "ee", "ef", "effect", "eg", "ei", "eight", "eighty", "either", "ej", "el", "eleven", "else", "elsewhere", "em", "empty", "en", "end", "ending", "enough", "entirely", "eo", "ep", "eq", "er", "es", "especially", "est", "et", "et-al", "etc", "eu", "ev", "even", "ever", "every", "everybody", "everyone", "everything", "everywhere", "ex", "exactly", "example", "except", "ey", "f", "f2", "fa", "far", "fc", "few", "ff", "fi", "fifteen", "fifth", "fify", "fill", "find", "fire", "first", "five", "fix", "fj", "fl", "fn", "fo", "followed", "following", "follows", "for", "former", "formerly", "forth", "forty", "found", "four", "fr", "from", "front", "fs", "ft", "fu", "full", "further", "furthermore", "fy", "g", "ga", "gave", "ge", "get", "gets", "getting", "gi", "give", "given", "gives", "giving", "gj", "gl", "go", "goes", "going", "gone", "got", "gotten", "gr", "greetings", "gs", "gy", "h", "h2", "h3", "had", "hadn", "hadn't", "happens", "hardly", "has", "hasn", "hasnt", "hasn't", "have", "haven", "haven't", "having", "he", "hed", "he'd", "he'll", "hello", "help", "hence", "her", "here", "hereafter", "hereby", "herein", "heres", "here's", "hereupon", "hers", "herself", "hes", "he's", "hh", "hi", "hid", "him", "himself", "his", "hither", "hj", "ho", "home", "hopefully", "how", "howbeit", "however", "how's", "hr", "hs", "http", "hu", "hundred", "hy", "i", "i2", "i3", "i4", "i6", "i7", "i8", "ia", "ib", "ibid", "ic", "id", "i'd", "ie", "if", "ig", "ignored", "ih", "ii", "ij", "il", "i'll", "im", "i'm", "immediate", "immediately", "importance", "important", "in", "inasmuch", "inc", "indeed", "index", "indicate", "indicated", "indicates", "information", "inner", "insofar", "instead", "interest", "into", "invention", "inward", "io", "ip", "iq", "ir", "is", "isn", "isn't", "it", "itd", "it'd", "it'll", "its", "it's", "itself", "iv", "i've", "ix", "iy", "iz", "j", "jj", "jr", "js", "jt", "ju", "just", "k", "ke", "keep", "keeps", "kept", "kg", "kj", "km", "know", "known", "knows", "ko", "l", "l2", "la", "largely", "last", "lately", "later", "latter", "latterly", "lb", "lc", "le", "least", "les", "less", "lest", "let", "lets", "let's", "lf", "like", "liked", "likely", "line", "little", "lj", "ll", "ll", "ln", "lo", "look", "looking", "looks", "los", "lr", "ls", "lt", "ltd", "m", "m2", "ma", "made", "mainly", "make", "makes", "many", "may", "maybe", "me", "mean", "means", "meantime", "meanwhile", "merely", "mg", "might", "mightn", "mightn't", "mill", "million", "mine", "miss", "ml", "mn", "mo", "more", "moreover", "most", "mostly", "move", "mr", "mrs", "ms", "mt", "mu", "much", "mug", "must", "mustn", "mustn't", "my", "myself", "n", "n2", "na", "name", "namely", "nay", "nc", "nd", "ne", "near", "nearly", "necessarily", "necessary", "need", "needn", "needn't", "needs", "neither", "never", "nevertheless", "new", "next", "ng", "ni", "nine", "ninety", "nj", "nl", "nn", "no", "nobody", "non", "none", "nonetheless", "noone", "nor", "normally", "nos", "not", "noted", "nothing", "novel", "now", "nowhere", "nr", "ns", "nt", "ny", "o", "oa", "ob", "obtain", "obtained", "obviously", "oc", "od", "of", "off", "often", "og", "oh", "oi", "oj", "ok", "okay", "ol", "old", "om", "omitted", "on", "once", "one", "ones", "only", "onto", "oo", "op", "oq", "or", "ord", "os", "ot", "other", "others", "otherwise", "ou", "ought", "our", "ours", "ourselves", "out", "outside", "over", "overall", "ow", "owing", "own", "ox", "oz", "p", "p1", "p2", "p3", "page", "pagecount", "pages", "par", "part", "particular", "particularly", "pas", "past", "pc", "pd", "pe", "per", "perhaps", "pf", "ph", "pi", "pj", "pk", "pl", "placed", "please", "plus", "pm", "pn", "po", "poorly", "possible", "possibly", "potentially", "pp", "pq", "pr", "predominantly", "present", "presumably", "previously", "primarily", "probably", "promptly", "proud", "provides", "ps", "pt", "pu", "put", "py", "q", "qj", "qu", "que", "quickly", "quite", "qv", "r", "r2", "ra", "ran", "rather", "rc", "rd", "re", "readily", "really", "reasonably", "recent", "recently", "ref", "refs", "regarding", "regardless", "regards", "related", "relatively", "research", "research-articl", "respectively", "resulted", "resulting", "results", "rf", "rh", "ri", "right", "rj", "rl", "rm", "rn", "ro", "rq", "rr", "rs", "rt", "ru", "run", "rv", "ry", "s", "s2", "sa", "said", "same", "saw", "say", "saying", "says", "sc", "sd", "se", "sec", "second", "secondly", "section", "see", "seeing", "seem", "seemed", "seeming", "seems", "seen", "self", "selves", "sensible", "sent", "serious", "seriously", "seven", "several", "sf", "shall", "shan", "shan't", "she", "shed", "she'd", "she'll", "shes", "she's", "should", "shouldn", "shouldn't", "should've", "show", "showed", "shown", "showns", "shows", "si", "side", "significant", "significantly", "similar", "similarly", "since", "sincere", "six", "sixty", "sj", "sl", "slightly", "sm", "sn", "so", "some", "somebody", "somehow", "someone", "somethan", "something", "sometime", "sometimes", "somewhat", "somewhere", "soon", "sorry", "sp", "specifically", "specified", "specify", "specifying", "sq", "sr", "ss", "st", "still", "stop", "strongly", "sub", "substantially", "successfully", "such", "sufficiently", "suggest", "sup", "sure", "sy", "system", "sz", "t", "t1", "t2", "t3", "take", "taken", "taking", "tb", "tc", "td", "te", "tell", "ten", "tends", "tf", "th", "than", "thank", "thanks", "thanx", "that", "that'll", "thats", "that's", "that've", "the", "their", "theirs", "them", "themselves", "then", "thence", "there", "thereafter", "thereby", "thered", "therefore", "therein", "there'll", "thereof", "therere", "theres", "there's", "thereto", "thereupon", "there've", "these", "they", "theyd", "they'd", "they'll", "theyre", "they're", "they've", "thickv", "thin", "think", "third", "this", "thorough", "thoroughly", "those", "thou", "though", "thoughh", "thousand", "three", "throug", "through", "throughout", "thru", "thus", "ti", "til", "tip", "tj", "tl", "tm", "tn", "to", "together", "too", "took", "top", "toward", "towards", "tp", "tq", "tr", "tried", "tries", "truly", "try", "trying", "ts", "t's", "tt", "tv", "twelve", "twenty", "twice", "two", "tx", "u", "u201d", "ue", "ui", "uj", "uk", "um", "un", "under", "unfortunately", "unless", "unlike", "unlikely", "until", "unto", "uo", "up", "upon", "ups", "ur", "us", "use", "used", "useful", "usefully", "usefulness", "uses", "using", "usually", "ut", "v", "va", "value", "various", "vd", "ve", "ve", "very", "via", "viz", "vj", "vo", "vol", "vols", "volumtype", "vq", "vs", "vt", "vu", "w", "wa", "want", "wants", "was", "wasn", "wasnt", "wasn't", "way", "we", "wed", "we'd", "welcome", "well", "we'll", "well-b", "went", "were", "we're", "weren", "werent", "weren't", "we've", "what", "whatever", "what'll", "whats", "what's", "when", "whence", "whenever", "when's", "where", "whereafter", "whereas", "whereby", "wherein", "wheres", "where's", "whereupon", "wherever", "whether", "which", "while", "whim", "whither", "who", "whod", "whoever", "whole", "who'll", "whom", "whomever", "whos", "who's", "whose", "why", "why's", "wi", "widely", "will", "willing", "wish", "with", "within", "without", "wo", "won", "wonder", "wont", "won't", "words", "world", "would", "wouldn", "wouldnt", "wouldn't", "www", "x", "x1", "x2", "x3", "xf", "xi", "xj", "xk", "xl", "xn", "xo", "xs", "xt", "xv", "xx", "y", "y2", "yes", "yet", "yj", "yl", "you", "youd", "you'd", "you'll", "your", "youre", "you're", "yours", "yourself", "yourselves", "you've", "yr", "ys", "yt", "z", "zero", "zi", "zz"]
    
    for word in extra_stopwords:
        if word in words_used:
            words_used.pop(word)  

    for char in string.punctuation:
        if char in words_used:
            words_used.pop(char)      

    # for word in game_pigeon_words:
    #     if word in words_used:
    #         words_used.pop(word)

    print(words_used.most_common(10))


    #Word Hunt Counter
    # total_word_hunts = 0
    # total_anagrams = 0
    # for i in range(total_messages):
    #     row = messages.iloc[i]
    #     text = row['text']
    #     if(text == "Word Hunt"):
    #         total_word_hunts+=1
    #     if(text == "Anagrams"):
    #         total_anagrams+=1


    # Prints
    medals = ["🥇", "🥈", "🥉"]

    print(f"\nTotal Messages: {total_messages}")
    print(f"Total Sent: {total_sent}")
    print(f"Total Recieved: {total_recieved}")
    # print(f"Total Word Hunts: {total_word_hunts}\n")
    # print(f"Total Anagrams: {total_anagrams}\n")

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


if __name__ == "__main__":
    create_graphs()