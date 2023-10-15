import os
import openai
from api_key import api_key
openai.api_key = api_key

# Use OpenAI API to process the text content
prompt1 = """I will give you a review of a phone. I want you to summarize the review. 
The summary should contain every unique fact said about each of the feature of the phone. Here is the review - """

prompt2 = """Now I want you to use the summaries of the individual reviews which you gave me and give me 1 review for the product.
The review should give me a complete idea of the features of the phone, so that I can weight the pros and cons of the phone. 
The review should be very crisp and short and should only contain facts about the features of the product. 
In case the reviews say conflicting thing then you should consider the fact which is stated in majority of the reviews. 
Include all the unique facts from the summaries in the final review. Also list out the pros and cons of the product"""

def promptizer(prompt, content):
  message = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": prompt + content}
  ]
  return message

def process_columns(column_names):
    # Create a 'temp' folder if it doesn't exist
    temp_folder = 'temp'
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)

    for column_name in column_names:
        folder_name = column_name
        # Check if the folder exists
        if not os.path.exists(folder_name):
            print(f"Folder for column '{column_name}' does not exist.")
            continue

        # Loop through the text files inside the folder
        for filename in os.listdir(folder_name):
            text_content = []
            if filename.endswith('.txt'):
                file_path = os.path.join(folder_name, filename)
                with open(file_path, 'r') as file:
                    content = file.read()
                    text_content.append(content)

            # Combine the text content into a single string
            text_to_prompt = "\n".join(text_content)
            message1 = promptizer(prompt1,text_to_prompt)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",  # Use "gpt-3.5-turbo-0613" as the model
                messages=message1,
                #functions=functions,
                # function_call="auto",  # auto is default, but we'll be explicit
            )

          # Store the output in a file in the 'temp' folder
            temp_filename = os.path.join(temp_folder, f"temp_{filename}_summary.txt")
            with open(temp_filename, 'w') as temp_file:
                temp_file.write(response.choices[0].message["content"])



def process_summaries(temp_folder):
  # Process the files in the 'temp' folder
  text_content = []
  for filename in os.listdir(temp_folder):
      if filename.endswith('.txt'):
          file_path = os.path.join(temp_folder, filename)
          with open(file_path, 'r') as file:
              content = file.read()
              text_content.append(content)
  text_to_prompt = "\n".join(text_content)
  message2 = promptizer(prompt2,text_to_prompt)
  response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo-16k",  # Use "gpt-3.5-turbo-0613" as the model
      messages=message2,
  
  )

  # Store the final output in a file named after the column name
  final_filename = f"final_review_with pros and cons.txt"
  with open(final_filename, 'w') as final_file:
      final_file.write(response.choices[0].message["content"])

