import json
import ollama

def generate_qa_pairs(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    qa_pairs = []

    for item in data:
        content = item.get("content", [])
        text = " ".join(content)
        
        prompt = f"""
        Create questions for the content in the file webscraping.json
        and also form the answers 
        Extract meaningful Question-Answer pairs from the following text
        {text}
        Format the output as a JSON array of objects with 'question' and 'answer' keys.
        """

        response = ollama.chat(model='mistral:7b-instruct', messages=[{"role": "user", "content": prompt}])

        # ✅ FIX: Extract only the actual response text
        raw_content = response.message.content.strip()

        try:
            qa_data = json.loads(raw_content)  # Convert to JSON
            print("qa_data: ", qa_data)
            if isinstance(qa_data, list):  
                qa_pairs.extend(qa_data)
            else:
                print("Unexpected format, skipping this entry:", raw_content)
        except json.JSONDecodeError:
            print("Failed to parse AI-generated response:", raw_content)

    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(qa_pairs, file, indent=4, ensure_ascii=False)

    print(f"Q&A pairs saved to {output_file}")

# Example usage
generate_qa_pairs('webscrapingTS.json', 'conversionTS.json')
