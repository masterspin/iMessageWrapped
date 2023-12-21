import sqlite3
import datetime
import subprocess
import os
import json
import pandas as pd

def get_first_name_from_phone(phone_number, address_book):
    # Convert JSON-formatted address book to a list of dictionaries
    address_book_list = json.loads(address_book)
    # print(address_book_list)

    # phone_number = "".join([c for c in phone_number if c.isnumeric()])
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
    
    query += f" ORDER BY message.date DESC"
    results = cursor.execute(query).fetchall()
    
    messages = []

    for result in results:
        rowid, date, text, attributed_body, handle_id, is_from_me, cache_roomname = result

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
            date = datetime.datetime.fromtimestamp(new_date).strftime("%Y-%m-%d %H:%M:%S")

        mapping = get_chat_mapping(db_location, addressBookData)  # Get chat mapping from database location

        try:
            mapped_name = mapping[cache_roomname]
        except:
            mapped_name = None
            
        messages.append(
            {"rowid": rowid, "date": date, "text": body, "phone_number": phone_number, "is_from_me": is_from_me,
             "cache_roomname": cache_roomname, 'group_chat_name' : mapped_name})

    conn.close()
    return messages




def save_messages_as_csv(messages, output_file):
    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(messages)
    
    # Drop the 'rowid' column
    df.drop(columns=['rowid'], inplace=True, errors='ignore')

    # Convert 'date' column to datetime format
    df['date'] = pd.to_datetime(df['date'])
    
    # Extract year, month, timestamp from 'date'
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['timestamp'] = df['date'].astype(int) / 10**9  # Convert to Unix timestamp
    
    df.to_csv(output_file, index=False)


def print_messages(messages):
    print(json.dumps(messages))


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


#file location preprocessing
def preprocessing(user):
    source_address = f"/Users/{user}/Library/Application Support/AddressBook/AddressBook-v22.abcddb"

    command_address = ["cp", source_address, "./"]
    try:
        subprocess.run(command_address, check=True)
        print("AddressBook database copied successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

    source_chats = f"/Users/{user}/Library/Messages/chat.db"

    command_chats = ["cp", source_chats, "./"]
    try:
        subprocess.run(command_chats, check=True)
        print("Chats database copied successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

#location of the database
db_location = "./chat.db"

#location of the addressbook
address_book_location = "./AddressBook-v22.abcddb"
addressBookData = get_address_book(address_book_location)

recent_messages = read_messages(db_location, addressBookData)
combined_data = combine_data(recent_messages, addressBookData)
filtered_data = [message for message in combined_data if message['date'][:4] == '2023']

save_messages_as_csv(filtered_data, "./output.csv")