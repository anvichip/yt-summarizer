import re
import modal
from open_ai_api import process_columns, process_summaries
import os
from test_modal_api import make_api_request
import pandas as pd
# def get_transcript():
# def summary():
def get_vid(url):
    regExp = re.compile(r'^.*((youtu.be/)|(v/)|(u/\w/)|(embed/)|(watch\?))\??v?=?([^#&?]*).*')
    match = regExp.match(url)
    return match.group(7) if match and len(match.group(7)) == 11 else False

def loop_rows(df):
    # Start from the second row (row 1) and loop through all rows
    for index, row in df.iterrows():
        # Create a folder for each row based on the value in the 'PRODUCT' column
        folder_name = row['PRODUCT']
        os.makedirs(folder_name, exist_ok=True)
        
        # Loop through all columns (except 'PRODUCT') and call get_review function
        for column, url in row.items():
            if column != 'PRODUCT':
                filename = get_vid(url)
                if url == 'NULL':
                    continue
                else:
                    text_to_put = make_api_request(url)  # Assuming get_review is defined elsewhere
                    if text_to_put != None:
                        txt_file_path = os.path.join(folder_name, filename + '.txt')
                        with open(txt_file_path, 'w') as txt_file:
                            txt_file.write(text_to_put)
                    else:
                        continue



# #url1 = "https://anvichip--example-whisper-streaming-main-dev.modal.run"
# # data = {"url": "https://www.youtube.com/watch?v=Jqoasg8HJsk"
# url = "https://www.youtube.com/watch?v=Jqoasg8HJsk"
# result = make_api_request(url)
# # if result is not None:
# print(result)


df = pd.read_excel('phones.xlsx')
loop_rows(df)