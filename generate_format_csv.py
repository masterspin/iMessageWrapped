import sqlite3
import pandas as pd

conn = sqlite3.connect('./chat.db')

cur = conn.cursor()

cur.execute(" select name from sqlite_master where type = 'table' ")
for name in cur.fetchall():
    print(name)

messages = pd.read_sql_query("select * from message", conn)

messages = pd.read_sql_query('''select *, datetime(date/1000000000 + strftime("%s", "2001-01-01") ,"unixepoch","localtime")  as date_utc from message''', conn) 

handles = pd.read_sql_query("select * from handle", conn)
chat_message_joins = pd.read_sql_query("select * from chat_message_join", conn)

messages['message_date'] = messages['date']
messages['timestamp'] = messages['date_utc'].apply(lambda x: pd.Timestamp(x))
messages['date'] = messages['timestamp'].apply(lambda x: x.date())
messages['month'] = messages['timestamp'].apply(lambda x: int(x.month))
messages['year'] = messages['timestamp'].apply(lambda x: int(x.year))

messages.rename(columns={'ROWID' : 'message_id'}, inplace = True)

handles.rename(columns={'id' : 'phone_number', 'ROWID': 'handle_id'}, inplace = True)


merge_level_1 = pd.merge(messages[['text', 'handle_id', 'date','message_date' ,'timestamp', 'month','year','is_sent', 'message_id']],  handles[['handle_id', 'phone_number']], on ='handle_id', how='left')

df_messages = pd.merge(merge_level_1, chat_message_joins[['chat_id', 'message_id']], on = 'message_id', how='left')

df_messages.to_csv('./imessages.csv', index = False, encoding='utf-8')

chats = pd.read_sql_query("select * from chat", conn)
df_combined = pd.merge(df_messages, chats[['chat_id', 'chat_name', 'chat_identifier']], on='chat_id', how='left')



df_combined.to_csv('./combined.csv', index = False, encoding='utf-8')
