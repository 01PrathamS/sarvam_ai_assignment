from helper import load_from_json
import pandas as pd
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')


def process_content(data_dict, window_size=2):
    headings = []
    contents = []
    embeddings = []

    for heading, content in data_dict.items():
        # Split content into individual sentences
        content = content.split('.')
        content = [s.strip() for s in content if s.strip()]  # Remove empty strings and extra spaces

        # Dynamically concatenate sentences based on the window size
        for i in range(len(content) - window_size + 1):
            text = ".".join(content[i:i + window_size])  # Concatenate sentences within the window
            embedding = model.encode(text)
            contents.append(text)
            embeddings.append(embedding)
            headings.append(heading)

    return pd.DataFrame({'heading': headings, 'content': contents, 'embedding': embeddings})


def preprocess_to_csv(json_file, output_csv='data/json_data_4.csv', window_size=2):
    data_dict, activity, questions, figure_desc, conclusions, final_questions = load_from_json(json_file)

    df = process_content(data_dict, window_size)
    df['embedding'] = df['embedding'].apply(lambda x: ','.join(map(str, x)))  # Convert embedding to string for CSV
    df.to_csv(output_csv, index=False)
    print(f'Data saved to {output_csv} as a CSV file...')


if __name__ == '__main__':
    json_file = "data/extracted_information.json"
    preprocess_to_csv(json_file, window_size=4)
