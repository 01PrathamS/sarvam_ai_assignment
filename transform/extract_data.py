import fitz 
from utils import reformat_questions, reformat_figures, reformat_conclusions_questions

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



def extract_text_with_font_info(pdf_path, target_font=None, target_font_size=None, target_font_color=None):

    """
    Input: Path to a PDF file and optional target font, size, and color 

    Output: A dictionary containing the extracted text with font information

    Ouput Type: {heading: text}, {activity: content}, {question: text}, {figure_description: text}, {conclusion: text}, {final_questions: text}

    The function extracts text from a PDF file and returns a dictionary containing the text with font information.
    The text is grouped by headings and activities.
    The function also extracts activity and content  
    The function also extracts figure and figure_description (beta) 
    The function extracts questions group wise
    The function also extracts questions of full chapter and conclusions
    """
    # Open the PDF file
    doc = fitz.open(pdf_path)
    data_dict = {}  # {heading: text}
    activity = {}  # {activity: content}

    extracted_questions_list = []
    figure_desc = []
    curr_heading = None
    curr_activity = None

    # Loop through all the pages
    for page_num in range(len(doc)):
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

                            # Check if the font matches the target font, size, and color (if specified)
                            font_match = (target_font is None or target_font in font_name)
                            size_match = (target_font_size is None or abs(target_font_size - font_size) < 0.1)
                            color_match = (target_font_color is None or target_font_color == font_color)

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
                            elif curr_heading is not None and font_match and size_match and color_match:
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
                            elif curr_heading is None and font_match and size_match and color_match:
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


# Usage
pdf_path = r'data\iesc111_textbook.pdf'  # Replace with the actual PDF file path
target_font = 'Bookman'  # Set the desired font type or keep it None to get all fonts
target_font_size = 10.5  # Specify the target font size
target_font_color = 2236191  # Specify the target font color

# Extract the filtered text
extracted_text, extracted_activities, list_of_extracted_quesions, extracted_figure_description, conclusions, questions = extract_text_with_font_info(pdf_path, target_font, target_font_size, target_font_color)

# Save the extracted text to a file
with open('data/extracted_text.txt', 'w', encoding='utf-8') as f:
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


