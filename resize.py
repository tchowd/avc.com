import PyPDF2

# Open the PDF file
with open('output/posts.pdf', 'rb') as pdf_file:
    # Read the PDF content
    pdf_reader = PyPDF2.PdfReader(pdf_file)

    # Create a PDF writer object
    pdf_writer = PyPDF2.PdfWriter()

    # Set the new page size to A4
    page_width, page_height = 210, 297

    # Loop through each page in the PDF file
    for page_index in range(len(pdf_reader.pages)):
        # Get the current page
        page = pdf_reader.pages[page_index]

        # Resize the page
        page.mediabox.upper_right = (page_width, page_height)

        # Add the resized page to the PDF writer object
        pdf_writer.add_page(page)

    # Write the new PDF file
    with open('eth_resized.pdf', 'wb') as new_file:
        pdf_writer.write(new_file)
