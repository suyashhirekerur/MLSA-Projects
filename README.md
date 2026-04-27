# MLSA Projects

A collection of useful web-based tools and applications built for the Microsoft Learn Student Ambassadors (MLSA) program.

## Projects Included

### 1. ASCII Art Generator (`ascii_art_generator.py`)
A Streamlit-based web application that converts text and images into ASCII art. Features include:
- Text-to-ASCII conversion using various fonts
- Image-to-ASCII conversion with customizable parameters
- Terminal-style UI with dark theme
- Download options for generated art
- Support for multiple image formats

**Technologies:** Python, Streamlit, PIL, PyFiglet

### 2. Invoice Generator (`invoice-generator.html`)
A professional invoice generation tool built with HTML, CSS, and JavaScript. Key features:
- Create and customize invoices with company and client details
- Add multiple line items with descriptions, quantities, and prices
- Automatic tax and total calculations
- Export to PDF format
- Dark/Light mode toggle
- Responsive design

**Technologies:** HTML, CSS, JavaScript, html2pdf.js, jsPDF

## Getting Started

### Prerequisites
- Python 3.7+ (for ASCII Art Generator)
- A modern web browser (for Invoice Generator)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/suyashhirekerur/MLSA-Projects.git
   cd MLSA-Projects
   ```

2. For ASCII Art Generator:
   ```bash
   pip install streamlit pillow pyfiglet
   streamlit run ascii_art_generator.py
   ```

3. For Invoice Generator:
   - Open `invoice-generator.html` in your web browser

## Usage

- **ASCII Art Generator:** Run the Streamlit app and use the web interface to generate ASCII art from text or images.
- **Invoice Generator:** Open the HTML file in a browser and fill in the invoice details to generate and download professional invoices.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the [MIT License](LICENSE).

