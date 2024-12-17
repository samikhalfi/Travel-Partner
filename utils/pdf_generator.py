from fpdf import FPDF

def generate_pdf(travel_plan, destination):
    """
    Generate a PDF travel plan
    
    Args:
        travel_plan (str): Detailed travel plan text
        destination (str): Travel destination
    
    Returns:
        str: Path to generated PDF file
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Add a font that supports Unicode (DejaVuSans or other)
    pdf.add_font("DejaVuSans", "", "data/DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVuSans", size=12)
    
    pdf.cell(200, 10, txt=f"Travel Plan for {destination}", ln=True, align="C")
    pdf.ln(10)
    
    # Use multi_cell to handle long text and preserve line breaks
    pdf.multi_cell(0, 10, travel_plan)
    
    # Create PDF file path
    pdf_file_path = f"data/{destination}_travel_plan.pdf"
    
    # Output PDF to file
    pdf.output(pdf_file_path)
    
    return pdf_file_path