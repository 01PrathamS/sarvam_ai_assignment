import re

def reformat_conclusions_questions(text):

    """
    Input: A list of strings extracted from a PDF file

    Output: A tuple containing two lists:
        - A list of conclusions
        - A list of questions

    The function reformats the extracted text into a list of conclusions and a list of questions.
    """
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
