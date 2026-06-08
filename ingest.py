import os
import re
import random
from langchain_text_splitters import RecursiveCharacterTextSplitter


def clean_text(raw_text):
    """Strip trailing whitespace, duplicate headers, and HTML entities."""
    # Strip leading/trailing whitespace
    text = raw_text.strip()

    # Remove HTML entities
    text = text.replace("&nbsp;", " ")
    text = text.replace("&amp;", "&")
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")

    # Remove duplicate consecutive newlines (normalize to max 2)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text


def extract_professor_name(filename):
    """Extract professor name from filename using split."""
    # Remove .txt extension
    name_part = filename[:-4]
    # Remove prof_ prefix
    name_part = name_part[5:]
    # Split by underscore and capitalize each word
    professor_name = " ".join(word.capitalize() for word in name_part.split("_"))
    return professor_name


def ingest_documents():
    """Ingest all faculty profiles, clean, chunk, and attach metadata."""
    documents_dir = "documents"

    # Discover all .txt files
    txt_files = [f for f in os.listdir(documents_dir) if f.endswith(".txt")]
    txt_files.sort()

    print(f"Found {len(txt_files)} documents to ingest.\n")

    # Initialize chunker
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )

    all_chunks = []

    # Process each file
    for filename in txt_files:
        filepath = os.path.join(documents_dir, filename)

        # Read file
        with open(filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()

        # Clean text
        cleaned_text = clean_text(raw_text)

        # Extract professor name
        professor_name = extract_professor_name(filename)

        # Create metadata
        metadata = {
            "professor": professor_name,
            "source": filename
        }

        # Chunk the text
        chunks = splitter.split_text(cleaned_text)

        # Attach metadata to each chunk
        for chunk_text in chunks:
            all_chunks.append({
                "text": chunk_text,
                "metadata": metadata
            })

        print(f"+ {professor_name}: {len(chunks)} chunks")

    return all_chunks


def verify_chunks(all_chunks):
    """Print 5 random chunks and their metadata to console."""
    print(f"\n{'='*80}")
    print(f"VERIFICATION: 5 Random Chunks")
    print(f"{'='*80}\n")

    if len(all_chunks) < 5:
        sample = all_chunks
    else:
        sample = random.sample(all_chunks, 5)

    for i, chunk_dict in enumerate(sample, 1):
        print(f"--- CHUNK {i} ---")
        print(f"Professor: {chunk_dict['metadata']['professor']}")
        print(f"Source: {chunk_dict['metadata']['source']}")
        print(f"Full Text Chunk:\n{chunk_dict['text']}\n")


if __name__ == "__main__":
    all_chunks = ingest_documents()
    print(f"\nTotal chunks created: {len(all_chunks)}\n")
    verify_chunks(all_chunks)
