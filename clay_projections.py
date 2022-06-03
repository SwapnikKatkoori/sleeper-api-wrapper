from pathlib import Path
import camelot

file_path = Path("data/projections/clay_projections.pdf")
clay_projections = camelot.read_pdf(file_path)

