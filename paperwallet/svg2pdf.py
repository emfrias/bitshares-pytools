import argparse
from PyPDF2 import PdfFileMerger, PdfFileReader
import cairosvg

def svg2pdf(data) :
    return cairosvg.svg2pdf(data)

def main() :
    parser = argparse.ArgumentParser(description='Convert and concatenate SVGs into PDF file')
    parser.add_argument('svg', nargs='+', help='list of svg files')
    parser.add_argument('--output', type=str, help='ouput PDF file (defaults to "output.pdf")')
    parser.set_defaults(output="output.pdf")
    args = parser.parse_args()

    merger = PdfFileMerger()
    print("Converting SVG into PDFs")
    for svg in args.svg :
        print(" - %s" % svg)
        pdffile = svg.replace('.svg','.pdf')
        cairosvg.svg2pdf(bytestring=open(svg).read(),write_to=pdffile)
        merger.append(PdfFileReader(open(pdffile, 'rb')))

    print("Concatenating into PDF")
    merger.write(args.output)

if __name__ == '__main__':
    main()
