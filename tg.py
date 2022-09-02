from email.policy import default
from sqlalchemy.orm import sessionmaker, Session, declarative_base, relationship
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean, inspect
from database_settings import engine, Sheet_Instance
import os
import telebot

from binance.client import Client
import time
import datetime
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting import *

scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("googleEnv/google.json", scope)
googleClient = gspread.authorize(creds)

# sh = googleClient.create('Binance Trades - DONT CHANGE NAME')
# print(sh.id)

spreadsheet = googleClient.open("Binance Trades - DONT CHANGE NAME")

# spreadsheet.share('haynesx10@gmail.com', perm_type='anyone', role='writer')

TELEGRAM_BINANCE_API_KEY = os.getenv('TELEGRAM_BINANCE_API_KEY')

API_KEY = TELEGRAM_BINANCE_API_KEY
bot = telebot.TeleBot(API_KEY)



main_chat_id = "-1001768606486"







def check_for_sheet_updates(session):
    worksheet_list = spreadsheet.worksheets()



    worksheetIDs = []

    for eachWorksheet in worksheet_list:
        sheetInDatabase = session.query(Sheet_Instance).filter(Sheet_Instance.gid == eachWorksheet.id).first()
        if sheetInDatabase:
            if sheetInDatabase.sheet_name_lower != eachWorksheet.title.lower():
                sheetInDatabase.sheet_name_lower = eachWorksheet.title.lower()
            
            if sheetInDatabase.sheet_name != eachWorksheet.title:
                bot.send_message(main_chat_id, f"Sheet Name: '{sheetInDatabase.sheet_name}' Changed to '{eachWorksheet.title}'")
                sheetInDatabase.sheet_name = eachWorksheet.title
                
            
            
            # session.commit()
        worksheetIDs.append(eachWorksheet.id)
    

    
    allSheetsNotOnGoogleQuery = session.query(Sheet_Instance).filter(Sheet_Instance.gid.not_in(worksheetIDs))
    allSheetsNotOnGoogle = allSheetsNotOnGoogleQuery.all()
    allSheetsNotOnGoogleQuery.delete()
    # session.commit()

    for eachSheetNotOnGoogle in allSheetsNotOnGoogle:
        bot.send_message(main_chat_id, f"{eachSheetNotOnGoogle.sheet_name} Removed.")
        time.sleep(2)



# mysql_conn_str = "mysql+pymysql://root:Thebear1952!@localhost:3306/instances"

# engine = create_engine(mysql_conn_str)
# connection = engine.connect()
# q = connection.execute('SHOW DATABASES')
# available_tables = q.fetchall()

# Base = declarative_base()

# sessionMade = sessionmaker(bind=engine)
# session = Session(bind=engine)

# print(available_tables)



# class Sheet_Instance(Base):
#     __tablename__ = "sheet_instance"

#     id = Column(Integer, primary_key = True)
#     api_key = Column(String(128))
#     api_secret = Column(String(128))
#     gid = Column(String(128))
#     sheet_name = Column(String(128))
#     sheet_name_lower = Column(String(128))
#     active = Column(Boolean(), default=False)
#     notification_chat_id = Column(String(128))


# Base.metadata.create_all(engine)

# insp = inspect(engine)
# print(insp.get_table_names())








# sheetInDatabase = session.query(Sheet_Instance).filter(Sheet_Instance.sheet_name=="First Test Sheet").first()
# sheetInDatabase.active = True
# session.commit()
# print(sheetInDatabase)








@bot.message_handler(commands=['poll'])
def start_instance(message):
    with Session(bind=engine, expire_on_commit=True) as session:
        with session.begin():
            try:

                check_for_sheet_updates(session)



                try:
                    sheetName = message.text.split("/poll ")[1].lower()
                except Exception:
                    bot.reply_to(message, "Invalid Command. Invalid Format.")
                    return
                
                sheetByName = session.query(Sheet_Instance).filter(Sheet_Instance.sheet_name_lower == sheetName).first()
                if sheetByName:
                    sheetByName.active = True
                    # session.commit()
                    bot.reply_to(message, f"Now Polling for Sheet: '{sheetByName.sheet_name}'")
                    time.sleep(1)
                else:
                    time.sleep(1)
                    bot.reply_to(message, "No such sheets exists. Please try again.")
            except Exception as e:
                time.sleep(5)
                bot.send_message(main_chat_id, f"ERROR on poll: {e}")
                time.sleep(5)
        





@bot.message_handler(commands=['set_notifications'])
def set_notifications(message):
    with Session(bind=engine, expire_on_commit=True) as session:
        with session.begin():
            try:


                check_for_sheet_updates(session)



                try:
                    commandText = message.text.split("/set_notifications ")[1]

                    if "id=" not in commandText:
                        bot.reply_to(message, "Please provide a telegram chat id. \nExample: 'id=-000434323'")
                        return
                    
                    sheetName = commandText.split(" id=")[0]

                    telegramChatID = commandText.split(" id=")[1]
                    telegramChatID = telegramChatID.replace(" ", "").strip()

                    if len(telegramChatID) < 10:
                        bot.reply_to(message, "Please provide a valid telegram chat id.")
                        return
                    

                except:
                    bot.reply_to(message, "Invalid Command. Invalid Format.")
                    return
                

                sheetByName = session.query(Sheet_Instance).filter(Sheet_Instance.sheet_name_lower == sheetName.lower()).first()
                sheetByName.notification_chat_id = telegramChatID
                # session.commit()

                bot.send_message(main_chat_id, f"Notfication Chat Group Changed Successfully.")
            except Exception as e:
                time.sleep(5)
                bot.send_message(main_chat_id, f"ERROR on set_notif: {e}")
                time.sleep(5)





@bot.message_handler(commands=['end'])
def end_polling(message):
    with Session(bind=engine, expire_on_commit=True) as session:
        with session.begin():
            try:

                check_for_sheet_updates(session)
                time.sleep(1)



                try:
                    sheetName = message.text.split("/end ")[1].lower()
                except Exception:
                    bot.reply_to(message, "Invalid Command. Invalid Format.")
                    return
                
                sheetByName = session.query(Sheet_Instance).filter(Sheet_Instance.sheet_name_lower == sheetName).first()
                if sheetByName:
                    sheetByName.active = False
                    # session.commit()
                    bot.reply_to(message, f"Polling Ended for Sheet: '{sheetByName.sheet_name}'")
                    time.sleep(1)
                else:
                    time.sleep(1)
                    bot.reply_to(message, "No such sheets exists. Please try again.")
            except Exception as e:
                time.sleep(5)
                bot.send_message(main_chat_id, f"ERROR on end: {e}")
                time.sleep(5)



@bot.message_handler(commands=['changekeys'])
def change_keys(message):
    with Session(bind=engine, expire_on_commit=True) as session:
        with session.begin():
            try:
                check_for_sheet_updates(session)
                time.sleep(1)
                try:
                    commandText = message.text.split("/changekeys ")[1]

                    sheetName = commandText.split(" key=")[0].replace("\n", "").replace("\t", "")
                    if "secret=" in sheetName:
                        sheetName = commandText.split(" secret=")[0].replace("\n", "").replace("\t", "")
                        if "key=" in sheetName:
                            bot.reply_to(message, "Invalid Command. Invalid Format.")
                            return
                    
                    sheetNameLower = sheetName.lower()
                    
            
            
                except:
                    bot.reply_to(message, "Invalid Command. Please Try Again.")
                    return
                

                if sheetNameLower.strip() == "" or sheetNameLower == " " or sheetNameLower.strip() == " " or len(sheetNameLower) < 2 or len(sheetNameLower.strip()) < 2:
                    bot.reply_to(message, "Invalid Command. Sheet Name must be include characters and have a length more than 2.")
                    return

                if len(sheetNameLower) > 50:
                    bot.reply_to(message, "Invalid Command. Sheet Name must be less than 50 characters.")
                    return


                if " symbol=" not in commandText:
                    bot.reply_to(message, "Invalid Command. Please specifiy Binance Symbol like so: 'symbol=BTCBUSD' without quotation marks.")
                    return
                    
                binance_api_key = commandText.split(" key=")[1].split(" ")[0]

                binance_api_secret = commandText.split(" secret=")[1].split(" ")[0]

                binance_symbol = commandText.split(" symbol=")[1].split(" ")[0]

                binance_symbol = binance_symbol.replace(" ", "").strip()
                binance_symbol = binance_symbol.upper()

                binance_api_secret = binance_api_secret.replace(" ", "").strip()
                binance_api_key = binance_api_key.replace(" ", "").strip()

                if len(binance_api_key) != 64:
                    bot.reply_to(message, "Invalid API Key.")
                    return
                    
                if len(binance_api_secret) != 64:
                    bot.reply_to(message, "Invalid Secret Key.")
                    return
                    
                if len(binance_symbol) < 3:
                    bot.reply_to(message, "Invalid Symbol Key.")
                    return
                

                sheetByName = session.query(Sheet_Instance).filter(Sheet_Instance.sheet_name_lower == sheetNameLower).first()
                if not sheetByName:
                    bot.reply_to(message, "Invalid Command. Sheet does not exist. Please Try Again.")
                    return
                
                try:
                    time.sleep(0.5)
                    client = Client(api_key=binance_api_key, api_secret=binance_api_secret, testnet=False)
                    trades = client.get_my_trades(symbol=binance_symbol, startTime=1661992588000)
                    time.sleep(0.5)
                except Exception as e:
                    time.sleep(3)
                    bot.send_message(main_chat_id, f"Error!: {e}\n\nThis seems to relate to your Binance API Keys. They are incorrect in some way. Please try again with working keys. Make sure permissions are correct!", disable_web_page_preview=True, parse_mode="HTML")
                    time.sleep(3)
                    return


                sheetByName.api_key = binance_api_key
                sheetByName.api_secret = binance_api_secret
                sheetByName.symbol = binance_symbol
                # session.commit()

                bot.reply_to(message, "Successfully Changed Binance API Details!")




            except:
                bot.reply_to(message, "Invalid Command. Please Try Again.")
                return
            









@bot.message_handler(commands=['new'])
def new_sheet(message):
    with Session(bind=engine, expire_on_commit=True) as session:
        with session.begin():
            try:

                try:
                    commandText = message.text.split("/new ")[1]

                    sheetName = commandText.split(" key=")[0].replace("\n", "").replace("\t", "")
                    if "secret=" in sheetName:
                        sheetName = commandText.split(" secret=")[0].replace("\n", "").replace("\t", "")
                        if "key=" in sheetName:
                            bot.reply_to(message, "Invalid Command. Invalid Format.")
                            return
                    

                    sheetNameLower = sheetName.lower()

                    if sheetNameLower.strip() == "" or sheetNameLower == " " or sheetNameLower.strip() == " " or len(sheetNameLower) < 2 or len(sheetNameLower.strip()) < 2:
                        bot.reply_to(message, "Invalid Command. Sheet Name must be include characters and have a length more than 2.")
                        return

                    if len(sheetNameLower) > 50:
                        bot.reply_to(message, "Invalid Command. Sheet Name must be less than 50 characters.")
                        return


                    if " key=" not in commandText:
                        bot.reply_to(message, "Invalid Command. Please specifiy Binance API Key like so: 'key=iNpUtKeYhErE' without quotation marks.")
                        return
                    
                    if " secret=" not in commandText:
                        bot.reply_to(message, "Invalid Command. Please specifiy Binance Secret Key like so: 'secret=iNpUtSeCretHErE' without quotation marks.")
                        return
                    
                    if " symbol=" not in commandText:
                        bot.reply_to(message, "Invalid Command. Please specifiy Binance Symbol like so: 'symbol=BTCBUSD' without quotation marks.")
                        return
                    
                    binance_api_key = commandText.split(" key=")[1].split(" ")[0]

                    binance_api_secret = commandText.split(" secret=")[1].split(" ")[0]

                    binance_symbol = commandText.split(" symbol=")[1].split(" ")[0]

                    binance_symbol = binance_symbol.replace(" ", "").strip()
                    binance_symbol = binance_symbol.upper()

                    binance_api_secret = binance_api_secret.replace(" ", "").strip()
                    binance_api_key = binance_api_key.replace(" ", "").strip()

                    if len(binance_api_key) != 64:
                        bot.reply_to(message, "Invalid API Key.")
                        return
                    
                    if len(binance_api_secret) != 64:
                        bot.reply_to(message, "Invalid Secret Key.")
                        return
                    
                    if len(binance_symbol) < 3:
                        bot.reply_to(message, "Invalid Symbol Key.")
                        return

                        
                    

                except:
                    bot.reply_to(message, "Invalid Command. Invalid Format.")
                


                check_for_sheet_updates(session)
                time.sleep(1)

                worksheet_list = spreadsheet.worksheets()

                


                worksheetNames = []

                for eachWorksheet in worksheet_list:
                    worksheetNames.append(eachWorksheet.title.lower())
                



                


                








                if sheetNameLower in worksheetNames:
                    bot.reply_to(message, "Sheet Already Exists with this name. Please try again with a new name.")
                    return


                

                sheetByName = session.query(Sheet_Instance).filter(Sheet_Instance.sheet_name_lower == sheetNameLower).first()
                if sheetByName:
                    bot.reply_to(message, "Sheet Already Exists with this name. Please try again with a new name.")
                    return
                
                sheetByApiKey = session.query(Sheet_Instance).filter(Sheet_Instance.api_key == binance_api_key).first()
                if sheetByApiKey:
                    bot.reply_to(message, "Sheet Already Exists with this API Key. Please try again with a new API Key.")
                    return
                
                sheetBySecretKey = session.query(Sheet_Instance).filter(Sheet_Instance.api_secret == binance_api_secret).first()
                if sheetBySecretKey:
                    bot.reply_to(message, "Sheet Already Exists with this Secret Key. Please try again with a new Secret Key.")
                    return
                

                try:
                    client = Client(api_key=binance_api_key, api_secret=binance_api_secret, testnet=False)
                    trades = client.get_my_trades(symbol=binance_symbol, startTime=1661992588000)
                except Exception as e:
                    time.sleep(3)
                    bot.send_message(main_chat_id, f"Error!: {e}\n\nThis seems to relate to your Binance API Details. They are incorrect in some way. Please try again with working keys and make sure the right symbol is used. Make sure permissions are correct!", disable_web_page_preview=True, parse_mode="HTML")
                    time.sleep(3)
                    return
                

                worksheet = spreadsheet.add_worksheet(title=sheetName, rows=1000, cols=40)
                time.sleep(0.5)
                set_row_height(worksheet, '1:1000', 20)
                time.sleep(0.5)
                set_column_width(worksheet, 'A:AN', 115)
                time.sleep(0.5)
                set_column_width(worksheet, 'G:AN', 155)


                rows = [
                    [sheetName, "", "", "", "", "", "", "Starting Time", "", "", "", "", "", "", "", "", "", "", "", ""],
                    ["", "", "", "", "", "", "", datetime.datetime.fromtimestamp(int(str(time.time()).split(".")[0]) * 1000 / 1000).strftime("%d/%m/%Y %H:%M:%S"), "", "", "", "", "", "", "", "", "", "", "", ""],
                    ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
                    ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
                    ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
                    ["", "", "", "", "", "", '"=CUSTOM EQUATION1"', '"=CUSTOM EQUATION2"', '"=CUSTOM EQUATION2"', '"=etc"', '"=etc"', "", "", "", "", "", "", "", "", ""],
                    ["Date Time", "Timestamp", "Trade Direction", "Qty", "QuoteQty", "Execution Price", "CUSTOM COLUMN1", "CUSTOM COLUMN2", "CUSTOM COLUMN3", "etc", "etc", "", "", "", "", "", "", "", "", ""]
                ]

                worksheet.append_rows(rows, value_input_option='USER_ENTERED')

                



                newSheetInstance = Sheet_Instance(api_key=binance_api_key, api_secret=binance_api_secret, symbol=binance_symbol, gid=worksheet.id, sheet_name=sheetName, sheet_name_lower=sheetNameLower, active=False)

                session.add(newSheetInstance)
                session.flush()
                # session.commit()

                bot.reply_to(message, f"Sheet has been created! ✅\nTo start polling binance for trades, type:\n`/poll {sheetName}`", parse_mode="Markdown")
            except Exception as e:
                time.sleep(6)
                bot.send_message(main_chat_id, f"ERROR on NEWSHEET: {e}")


    

    

        

        
        
        

while True:
    try:
        bot.polling()
    except Exception as e:
        print(e)
        print("ERROR ON TG BOT HERE tg.py")
        time.sleep(40)





