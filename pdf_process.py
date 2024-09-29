# open a pdf file and remove 4th page from last  

from PyPDF2 import PdfReader, PdfWriter

def remove_nth_page_from_last(input_pdf, output_pdf, n=4):
    # Open the PDF file
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # Calculate the index of the page to be removed (0-based index)
    page_to_remove = len(reader.pages) - n

    # Loop through all pages except the one to be removed
    for i in range(len(reader.pages)):
        if i != page_to_remove:
            writer.add_page(reader.pages[i])

    # Write the modified PDF to a new file
    with open(output_pdf, "wb") as output_file:
        writer.write(output_file)

# pdf path  = C:\Users\saval\Desktop\sarvam_ai\sarvam_ai_assignment\data\iesc111_textbook.pdf

if __name__ == "__main__":
    import pathlib 
    base_dir = pathlib.Path(__file__).resolve().parent
    input_pdf = base_dir / "data" / "iesc111_textbook.pdf"
    output_pdf = base_dir / "data" / "iesc111_textbook_modified.pdf"
    remove_nth_page_from_last(input_pdf, output_pdf, n=4)