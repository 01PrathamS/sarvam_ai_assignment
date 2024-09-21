import fitz  # PyMuPDF
import re

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

  return text

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


def extract_text_with_font_info(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    data_dict = {}  # {heading: text}
    activity = {}  # {activity: content}

    extracted_questions_list = []
    figure_desc = []
    curr_heading = None
    curr_activity = None

    # Loop through all the pages
    for page_num in range(len(doc)-3):
        page = doc.load_page(page_num)

        # Define clipping rectangles for left and right columns
        left_rect = fitz.Rect(0, 0, page.rect.width / 2, page.rect.height)
        right_rect = fitz.Rect(page.rect.width / 2, 0, page.rect.width, page.rect.height)

        # Extract text blocks for both columns (with font info)
        left_blocks = page.get_text("dict", clip=left_rect)['blocks']
        right_blocks = page.get_text("dict", clip=right_rect)['blocks']

        # Process each column (left and right)
        for blocks in [left_blocks, right_blocks]:
            for block in blocks:
                if 'lines' in block:
                    for line in block['lines']:
                        for span in line['spans']:
                            font_name = span['font']
                            font_size = span['size']
                            font_color = span['color']
                            text = span['text']

                            # Heading detection
                            if font_name == 'Garamond,Bold' and abs(font_size - 16.0) < 0.1 and font_color == 2236191:
                                curr_heading = text
                                if curr_heading not in data_dict:
                                    data_dict[curr_heading] = []

                            # Activity detection
                            elif font_name == 'Goudy-BoldItalic' and abs(font_size - 16.0) < 0.1 and font_color == 3027090:
                                curr_activity = text
                                if curr_activity not in activity:
                                    activity[curr_activity] = []

                            # Content for heading
                            elif curr_heading is not None and font_name == "Bookman" and font_size == 10.5 and font_color == 2236191:
                                data_dict[curr_heading].append(text)

                            # Content for activity
                            elif curr_activity is not None and font_name == 'Bookman' and abs(font_size - 9.5) < 0.1 and font_color == 2236191:
                                activity[curr_activity].append(text)

                            # content for questions specification  Color: 44527
                            elif font_color == 44527:
                                extracted_questions_list.append(text)

                            # figure and figure description --> if Specifications are Font: Bookman,BoldItalic, Size: 9.0, Color: 2236191 or Font: Bookman,BoldItalic, Size: 9.0, Color: 2236191 add it to figure_desc list
                            elif font_name in ['Bookman,BoldItalic', 'Bookman,Italic'] and abs(font_size - 9.0) < 0.1 and font_color == 2236191:
                                figure_desc.append(text)

                            # Content without heading (Sound)
                            elif curr_heading is None and font_name == "Bookman" and font_size == 10.5 and font_color == 2236191:
                                if 'Sound' not in data_dict:
                                    data_dict['Sound'] = []
                                data_dict['Sound'].append(text)


    conclusion_questions_text = extract_text_from_full_page(pdf_path, [12,13,14])

    conclusions, final_questions = reformat_conclusions_questions(conclusion_questions_text)

    formatted_questions = reformat_questions(extracted_questions_list)
    formatted_figures = reformat_figures(figure_desc)
    questions = {"question": formatted_questions}
    figure_desc = {"figure_descriptions": formatted_figures}
    conclusions = {"conclusion": conclusions}
    final_questions = {"final_questions": final_questions}
    # Close the PDF file
    doc.close()

    # Join the text for each heading and activity
    for heading in data_dict:
        data_dict[heading] = ' '.join(data_dict[heading])
    for act in activity:
        activity[act] = ' '.join(activity[act])

    return data_dict, activity, questions, figure_desc, conclusions, final_questions

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

if __name__ == "__main__":

    # Usage
    pdf_path = r"data\iesc111_textbook.pdf"  # Replace with the actual PDF file path

    # Extract the filtered text
    extracted_text, extracted_activities, list_of_extracted_quesions, extracted_figure_description, conclusions, questions = extract_text_with_font_info(pdf_path)

    # Save the extracted text to a file
    with open('final_text.txt', 'w', encoding='utf-8') as f:
        f.write("HEADINGS AND CONTENT:\n\n")
        for heading, text in extracted_text.items():
            f.write(f"Heading: {heading}\n")
            f.write(f"Content: {text}\n\n")

        f.write("\nACTIVITIES:\n\n")
        for activity, content in extracted_activities.items():
            f.write(f"Activity: {activity}\n")
            f.write(f"Content: {content}\n\n")

        f.write("\nQUESTIONS:\n\n")
        for question in list_of_extracted_quesions['question']:
            f.write(f"Question: {question}\n")

        f.write("\nFIGURES:\n\n")
        for figure in extracted_figure_description['figure_descriptions']:
            f.write(f"Figure: {figure}\n")

        f.write("\nCONCLUSIONS:\n\n")
        for conclusion in conclusions['conclusion']:
            f.write(f"Conclusion: {conclusion}\n")

        f.write("\nFINAL QUESTIONS:\n\n")
        for final_question in questions['final_questions']:
            f.write(f"Final Question: {final_question}\n")

    print("Text extraction based on font type complete!")
