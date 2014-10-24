import markdown
import weasyprint
import codecs
import argparse
import os
from bs4 import BeautifulSoup
from datetime import date

CSS_PATH = 'static/pdf_styles/Quilted.css'

# Parse command line arguments.
# parser = argparse.ArgumentParser(description='Take a markdown file and convert it to a Quilted-styled PDF.')
# today = date.today().strftime('%b %d, %Y')

# parser.add_argument('inpath', help='Path of input markdown file')
# parser.add_argument('-o', '--outpath', default='', help='Path to write output pdf')
# parser.add_argument('-d', '--date', default=today,
#   help='Date for PDF header. Must be surrounded by quotes.')
# parser.add_argument('-t', '--type', default='',
#   help='Document type for PDF header. Must be surrounded by quotes. Ex. "Statement of Work"')
# parser.add_argument('-hd', '--header_depth', default=3,
#   help='If generating a table of contents, the maximum header level to include. \
#   Ex. 3 will include H2s and H3s.')

# args = parser.parse_args()
# if args.outpath == '':
#   args.outpath = os.path.splitext(args.inpath)[0] + '.pdf'

def gather(current, current_level, max_depth):
  """Recursive function to build an ordered, nested table of contents based on section headers"""
  if (not current) or (current.name == "h" + str(current_level-1)) or (current_level > max_depth):
    # Reached maximum depth or the next parent header. Return empty string.
    return ""
  elif current.name == "h" + str(current_level) and current_level == max_depth:
    # Reached the next header to gather. Add it and keep looking for more headers at this level.
    # We're at max depth, so don't look any deeper.
    return "<li>" + current.find(text=True) + "</li>" + \
      gather(current.next_sibling, current_level, max_depth)
  elif current.name == "h" + str(current_level):
    # Reached the next header to gather. Add it and look for subheaders below this one.
    # Then keep looking for more headers at this level.
    return "<li>" + current.find(text=True) + \
      "<ol>" + gather(current.next_sibling, current_level + 1, max_depth) + "</ol></li>" + \
      gather(current.next_sibling, current_level, max_depth)
  else:
    # Not a relevant tag. Carry on with the next element.
    return gather(current.next_sibling, current_level, max_depth)

def convert(markdown_input, outpath, header_depth, date, type):
  html = markdown.markdown(markdown_input, extensions = ['tables'])

  # Insert table of contents
  soup = BeautifulSoup(html)
  toc = "<ol>" + gather(soup.find("h2"), 2, int(header_depth)) + "</ol>"
  html = html.replace("<TOC>", toc)

  # Load CSS.
  css_directory = os.path.dirname(CSS_PATH)
  css_file = open(CSS_PATH)
  css = css_file.read().replace('$date', date).replace('$type', type)
  styles = weasyprint.CSS(string=css, base_url=css_directory)

  # Convert HTML and CSS to PDF using weasyprint.
  weasyprint.HTML(string=html).write_pdf(outpath,
    stylesheets = [styles])
