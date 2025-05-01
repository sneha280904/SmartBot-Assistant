# Import necessary modules
import json  # for working with JSON data
import ollama  # for interacting with the Ollama API to generate question-answer pairs

# Function to generate Question-Answer pairs from input content
def generate_qa_pairs(input_file, output_file):
    # Open the input file containing JSON data and load it
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    # Initialize an empty list to hold the generated Q&A pairs
    qa_pairs = []

    # Loop through each item in the loaded data
    for item in data:
        # Retrieve the 'content' field, which is expected to be a list of text
        content = item.get("content", [])
        
        # Join the content list into a single string of text
        text = " ".join(content)
        
        # Define the prompt to send to the Ollama model for generating Q&A pairs
        prompt = f"""
        Create questions for the content in the file webscraping.json
        and also form the answers 
        Extract meaningful Question-Answer pairs from the following text
        {text}
        Format the output as a JSON array of objects with 'question' and 'answer' keys.
        """

        # Make a request to the Ollama model to generate Q&A pairs based on the provided text
        response = ollama.chat(model='mistral:7b-instruct', messages=[{"role": "user", "content": prompt}])

        # ✅ FIX: Extract only the actual response text from the Ollama API's response
        raw_content = response.message.content.strip()

        try:
            # Attempt to parse the raw content as JSON
            qa_data = json.loads(raw_content)  # Convert to JSON
            
            # Print the parsed Q&A data for debugging
            print("qa_data: ", qa_data)
            
            # If the parsed data is a list, extend the qa_pairs list with the new pairs
            if isinstance(qa_data, list):  
                qa_pairs.extend(qa_data)
            else:
                # If the format is unexpected, log and skip this entry
                print("Unexpected format, skipping this entry:", raw_content)
        except json.JSONDecodeError:
            # If parsing fails, log an error and skip this entry
            print("Failed to parse AI-generated response:", raw_content)

    # Open the output file and save the generated Q&A pairs in JSON format
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(qa_pairs, file, indent=4, ensure_ascii=False)

    # Print a message indicating where the generated Q&A pairs have been saved
    print(f"Q&A pairs saved to {output_file}")

# Example usage: generate Q&A pairs from 'webscrapin.json' and save them in 'conversion.json'
generate_qa_pairs('webscraping.json', 'conversion.json')



