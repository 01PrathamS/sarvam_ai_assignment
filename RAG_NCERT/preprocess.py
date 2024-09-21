from extract import extract_text_with_font_info
import pandas as pd 
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')


def preprocess_to_csv(pdf_path):

    data_dict, activity, questions, figure_desc, conclusions, final_questions = extract_text_with_font_info(pdf_path)

    data = {}

    data['headings_and_content'] = {}
    data['activities'] = {}
    data['questions'] = {}
    data['conclusions'] = {}
    data['final_questions'] = {}

    for heading in data_dict:
        data['headings_and_content'][heading] = data_dict[heading]

    for activity_name in activity:
        data['activities'][activity_name] = activity[activity_name]

    for i in range(len(questions['question'])):
        data['questions'][f'Question-{i}'] = questions['question'][i][3:]


    for i in range(len(conclusions['conclusion'])):
        data['conclusions'][f'Conclusion-{i}'] = conclusions['conclusion'][i]

    for i in range(len(final_questions['final_questions'])):
        data['final_questions'][f'Final Question-{i}'] = final_questions['final_questions'][i]

    def process_content(data, window_size=2):

        headings = []
        contents = []
        embeddings = []

        for heading, content in data['headings_and_content'].items():
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

        df = pd.DataFrame({'heading': headings, f'content': contents, f'embedding': embeddings})

        return df
    
    df = process_content(data)
    df['embedding'] =  df['embedding'].apply(lambda x: ','.join(map(str, x))) # Convert embedding to string for CSV
    df.to_csv('data.csv', index=False)

    return 


if __name__ == '__main__':
    preprocess_to_csv(r'data\iesc111_textbook.pdf')