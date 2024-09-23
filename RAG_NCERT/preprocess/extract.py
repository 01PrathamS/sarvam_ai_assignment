import fitz  # PyMuPDF
from helper import (extract_text_from_full_page,
                    save_extracted_text_to_file,
                    reformat_questions,
                    reformat_figures, 
                    save_to_json)

def extract_text_with_font_info(pdf_path):
    # Open the PDF file
    doc = fitz.open(pdf_path)
    data_dict = {}  # {heading: text}
    activity = {}  # {activity: content}

    extracted_questions_list = []
    figure_desc = []
    curr_heading = None
    curr_activity = None

    # TO DO : ## extracting figure with tesseract or any other OCR tool(figure out)

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

                            
                            # Content for heading
                            elif curr_heading is not None and font_name == "Bookman" and font_size == 10.5 and font_color == 2236191:
                                data_dict[curr_heading].append(text)


                            # Content without heading (Sound)
                            elif curr_heading is None and font_name == "Bookman" and font_size == 10.5 and font_color == 2236191:
                                if 'Sound' not in data_dict:
                                    data_dict['Sound'] = []
                                data_dict['Sound'].append(text)

                            # Activity detection
                            elif font_name == 'Goudy-BoldItalic' and abs(font_size - 16.0) < 0.1 and font_color == 3027090:
                                curr_activity = text
                                if curr_activity not in activity:
                                    activity[curr_activity] = []

                            # Content for activity
                            elif curr_activity is not None and font_name == 'Bookman' and abs(font_size - 9.5) < 0.1 and font_color == 2236191:
                                activity[curr_activity].append(text)

                            # content for questions in between paragraph specification  Color: 44527
                            elif font_color == 44527:
                                extracted_questions_list.append(text)

                            # figure and figure description --> if Specifications are Font: Bookman,BoldItalic, Size: 9.0, Color: 2236191 or Font: Bookman,BoldItalic, Size: 9.0, Color: 2236191 add it to figure_desc list
                            elif font_name in ['Bookman,BoldItalic', 'Bookman,Italic'] and abs(font_size - 9.0) < 0.1 and font_color == 2236191:
                                figure_desc.append(text)

                            # final conlusion and questions would be in the last 3 pages of the pdf file

    conclusions, final_questions = extract_text_from_full_page(pdf_path, [12,13,14])


    # Reformat the extracted information
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

    # save this to json file 
    save_to_json(data_dict, activity, questions, figure_desc, conclusions, final_questions, filename="data/extracted_information.json")
    return 

# how the output is looking like with data type 
# data_dict = {'heading': 'text'}
# activity = {'activity': 'content'}
# questions = {'question': ['question1', 'question2']}
# figure_desc = {'figure_descriptions': ['figure1', 'figure2']}
# conclusions = {'conclusion': ['conclusion1', 'conclusion2']}
# final_questions = {'final_questions': ['final_question1', 'final_question2']}



if __name__ == "__main__":
    from pathlib import Path
    base_dir = Path(__file__).resolve().parent.parent
    pdf_path = base_dir / "data" / "iesc111_textbook.pdf"
    txt_file_path = base_dir / "data" / "extracted_text.txt"
    json_file_path = base_dir / "data" / "extracted_information.json"
    extract_text_with_font_info(pdf_path)
    save_extracted_text_to_file(json_file_path, txt_file_path)

