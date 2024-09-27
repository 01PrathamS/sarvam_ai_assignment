
import fitz 
import re 
import json 

def extract_text_from_full_page(pdf_path, page_num: list):
  doc = fitz.open(pdf_path)

  text = []

  for page_num in range(len(doc)):
    page = doc.load_page(page_num)

    text_blocks = page.get_text("dict")['blocks']

    for block in text_blocks:
      if 'lines' in block:
        for line in block['lines']:
          for span in line['spans']:
            font_name = span['font']
            font_size = span['size']
            font_color = span['color']

            # check this specifications Font: Symbol, Size: 10.5, Color: 16225053 or Font: Bookman, Size: 11.0, Color: 2236191 then add it to text list
            if (font_name == 'Symbol' and font_size == 10.5 and font_color == 16225053) or (font_name == 'Bookman' and font_size == 11.0 and font_color == 2236191):
              text.append(span['text'])

  conclusions, final_questions = reformat_conclusions_questions(text)

  return conclusions, final_questions


def reformat_conclusions_questions(text):

    conclusions = []
    questions = []

    # Flags for parsing
    is_question = False
    current_conclusion = ""

    # Loop through the extracted text
    for line in text:
        line = line.strip()  # Remove extra spaces

        if line.startswith('•'):  # If it starts with a bullet point, process as conclusion
            is_question = False
            if current_conclusion:  # Append the previous conclusion to the list
                conclusions.append(current_conclusion.strip())
            current_conclusion = line.replace('•', '').strip()  # Start a new conclusion
        elif re.match(r'^\d+\.', line):  # If it starts with a number followed by a period, it's a question
            is_question = True
            if current_conclusion:  # Append the last conclusion to the list
                conclusions.append(current_conclusion.strip())
                current_conclusion = ""
            questions.append(line.strip())  # Start a new question
        elif is_question:  # Append to the current question
            questions[-1] += " " + line.strip()
        else:  # Append to the current conclusion
            current_conclusion += " " + line.strip()

    # Append the last conclusion if any
    if current_conclusion:
        conclusions.append(current_conclusion.strip())

    final_que = [q[3:].strip() for q in questions]
    return conclusions, final_que


def reformat_questions(extracted_list):
    formatted_questions = []
    current_question = ""

    for item in extracted_list:
        # Check if the item is a question number
        if item[:-1].isdigit() and item.endswith('.'):
            if current_question:  # Add the previous question if it exists
                formatted_questions.append(current_question.strip())
            current_question = item + " "  # Start a new question
        else:
            current_question += item + " "  # Append to the current question

    if current_question:  # Add the last question if it exists
        formatted_questions.append(current_question.strip())

    return formatted_questions

def reformat_figures(extracted_list):
    formatted_figures = []
    current_figure = ""

    for item in extracted_list:
        # Check if the item starts with "Fig"
        if item.startswith("Fig") or item.startswith("fig"):
            if current_figure:  # Add the previous figure if it exists
                formatted_figures.append(current_figure.strip())
            current_figure = item + " "  # Start a new figure entry
        else:
            current_figure += item.strip() + " "  # Append to the current figure description

    if current_figure:  # Add the last figure if it exists
        formatted_figures.append(current_figure.strip())

    return formatted_figures

# To save in JSON
def save_to_json(data_dict, activity, questions, figure_desc, conclusions, final_questions, filename="output_data.json"):
    with open(filename, 'w') as f:
        json.dump({
            "data_dict": data_dict,
            "activity": activity,
            "questions": questions,
            "figure_desc": figure_desc,
            "conclusions": conclusions,
            "final_questions": final_questions
        }, f)
    print(f"Data Saved as JSON file at {filename}")


# To load from JSON
def load_from_json(filename="output_data.json"):
    with open(filename, 'r') as f:
        data = json.load(f)
    return (data['data_dict'], data['activity'], data['questions'], data['figure_desc'], data['conclusions'], data['final_questions'])


# To save the extracted text to a file
def save_extracted_text_to_file(json_file_path, txt_file_path):

    # Open the JSON file and load its contents
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    # Unpack the extracted data
    extracted_text = data['data_dict']
    extracted_activities = data['activity']
    list_of_extracted_questions = data['questions']
    extracted_figure_description = data['figure_desc']
    conclusion = data['conclusions']
    final_questions = data['final_questions']

    # Save the extracted text to a file
    with open(txt_file_path, 'w', encoding='utf-8') as f:
        f.write("HEADINGS AND CONTENT:\n\n")
        for heading, text in extracted_text.items():
            f.write(f"Heading: {heading}\n")
            f.write(f"Content: {text}\n\n")

        f.write("\nACTIVITIES:\n\n")
        for activity, content in extracted_activities.items():
            f.write(f"Activity: {activity}\n")
            f.write(f"Content: {content}\n\n")

        f.write("\nQUESTIONS:\n\n")
        for question in list_of_extracted_questions['question']:
            f.write(f"Question: {question}\n")

        f.write("\nFIGURES:\n\n")
        for figure in extracted_figure_description['figure_descriptions']:
            f.write(f"Figure: {figure}\n")

        f.write("\nCONCLUSIONS:\n\n")
        for con in conclusion['conclusion']:
            f.write(f"Conclusion: {con}\n")

        f.write("\nFINAL QUESTIONS:\n\n")
        for final_question in final_questions['final_questions']:
            f.write(f"Final Question: {final_question}\n")

    print(f"Extracted text saved to {txt_file_path}")


