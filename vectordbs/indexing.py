from utils import load_txt_file
from processing_functions import get_chunks, get_embeddings
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Process text files for vector storage."
    )
    parser.add_argument("--input_file", type=str, help="Path of the input text file.")
    parser.add_argument(
        "--output_file", type=str, help="File to save the vector storage."
    )
    args = parser.parse_args()

    print("Processing text file:", args.input_file)

    # Load the text from the input file
    raw_text = load_txt_file(args.input_file)

    # Get chunks from the raw text
    text_chunks = get_chunks(raw_text)

    print(f"Total number of text chunks: {len(text_chunks)}")
    print(f"Here is a small sample of the text chunks: {text_chunks[10:20]}")

    # Get embeddings for the chunks
    vector_storage = get_embeddings(text_chunks)

    # Save the vector storage to the output file
    vector_storage.save_local(args.output_file)

    print(f"Vector storage saved to {args.output_file}")


if __name__ == "__main__":
    main()
