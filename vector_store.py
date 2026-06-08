import chromadb
import os
import shutil
# Add this crucial import line for the embedding engine
from chromadb.utils import embedding_functions
from ingest import ingest_documents

def setup_chromadb():
    """Initialize ChromaDB with BAAI/bge-large-en-v1.5 embeddings."""
    # Clean up old database to force re-indexing with new embedding model
    if os.path.exists("./chroma_db_bge"):
        print("Removing old ChromaDB_BGE directory...")
        shutil.rmtree("./chroma_db_bge")

    # Initialize persistent ChromaDB client with new path
    client = chromadb.PersistentClient(path="./chroma_db_bge")

    # Use stronger BGE embedding model for better semantic understanding
    bge_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="BAAI/bge-large-en-v1.5"
    )

    # Create collection with new name
    collection = client.get_or_create_collection(
        name="ncat_professors_bge",
        embedding_function=bge_ef,
        metadata={"hnsw:space": "cosine"}
    )

    return collection


def populate_vector_store(collection, chunks):
    """Add all chunks to ChromaDB with IDs and metadata."""
    ids = []
    documents = []
    metadatas = []

    for idx, chunk_dict in enumerate(chunks, 1):
        ids.append(f"id_{idx}")
        documents.append(chunk_dict["text"])
        metadatas.append({
            "professor": chunk_dict["metadata"]["professor"],
            "source": chunk_dict["metadata"]["source"]
        })

    # Add to collection
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )

    print(f"+ Stored {len(chunks)} chunks in ChromaDB collection 'ncat_professors_bge'\n")


def debug_professor_chunks(chunks, professor_name):
    """Show all chunks for a specific professor to verify data exists."""
    matching_chunks = [c for c in chunks if professor_name.lower() in c["metadata"]["professor"].lower()]
    print(f"\n{'='*80}")
    print(f"DEBUG: Chunks for {professor_name} ({len(matching_chunks)} total)")
    print(f"{'='*80}\n")

    for i, chunk in enumerate(matching_chunks[:3], 1):  # Show first 3
        print(f"--- CHUNK {i} ---")
        print(f"Text (first 300 chars): {chunk['text'][:300]}...\n")


def query_database(collection, query_text, n_results=3):
    """Search ChromaDB and print results with metadata and distance scores."""
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )

    print(f"\n{'='*80}")
    print(f"QUERY: {query_text}")
    print(f"{'='*80}\n")

    if not results["documents"] or len(results["documents"][0]) == 0:
        print("No results found.\n")
        return

    for i, (doc, metadata, distance) in enumerate(
        zip(results["documents"][0], results["metadatas"][0], results["distances"][0]), 1
    ):
        print(f"--- RESULT {i} ---")
        print(f"Professor: {metadata['professor']}")
        print(f"Source: {metadata['source']}")
        print(f"Distance Score: {distance:.4f}")
        print(f"Retrieved Text:\n{doc}\n")


if __name__ == "__main__":
    print("Loading documents from ingest.py...")
    chunks = ingest_documents()
    print(f"\nLoaded {len(chunks)} chunks.\n")

    print("Initializing ChromaDB with BAAI/bge-large-en-v1.5...")
    collection = setup_chromadb()

    print("Populating vector store...")
    populate_vector_store(collection, chunks)

    # Debug: Check if Huiming Yu data exists
    print(f"{'='*80}")
    print("PHASE 1: Checking Data Integrity")
    print(f"{'='*80}")
    debug_professor_chunks(chunks, "Huiming Yu")

    # Run verification queries with more specific language
    test_queries = [
        "What did Dr. Xiaohong Yuan publish in 2024 regarding network security education?",
        "Dr. Tony Gwyn Primary Office Location",
        "What percentage of students would take professor huiming yu again?"
    ]

    print(f"\n{'='*80}")
    print("PHASE 2: Running 3 Test Queries with BGE Embedding Model")
    print(f"{'='*80}")

    for query in test_queries:
        query_database(collection, query, n_results=3)
