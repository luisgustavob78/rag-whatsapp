from processing_functions import get_pdf_content
from utils import save_txt_file
import argparse


def main():
    parser = argparse.ArgumentParser(description="Extract text from PDF documents.")
    parser.add_argument("--pdf_file", type=str, help="Path of PDF file to process.")
    parser.add_argument(
        "--output_file", type=str, help="File to save the extracted text."
    )
    args = parser.parse_args()

    print("Processing PDF files:", args.pdf_file)
    raw_text = get_pdf_content(args.pdf_file)

    save_txt_file(args.output_file, raw_text)

    print(f"Extracted text saved to {args.output_file}")


if __name__ == "__main__":
    main()
