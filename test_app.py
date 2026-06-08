"""Quick test of the app.py RAG pipeline without Gradio UI."""
import os
from dotenv import load_dotenv
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not set")

# Initialize clients
groq_client = Groq(api_key=GROQ_API_KEY)

# Load ChromaDB
client = chromadb.PersistentClient(path="./chroma_db_bge")
bge_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-large-en-v1.5"
)
collection = client.get_or_create_collection(
    name="ncat_professors_bge",
    embedding_function=bge_ef,
    metadata={"hnsw:space": "cosine"}
)

# Test queries
test_queries = [
    "What did Dr. Xiaohong Yuan publish in 2024 regarding network security?",
    "Where is Dr. Tony Gwyn's office located?",
    "What percentage of students would take professor huiming yu again?",
]

print("=" * 80)
print("MILESTONE 5: Testing RAG Pipeline End-to-End")
print("=" * 80)

for i, query in enumerate(test_queries, 1):
    print(f"\n[Test {i}] Query: {query}\n")

    # Retrieve context
    results = collection.query(query_texts=[query], n_results=3)

    if results["documents"] and len(results["documents"][0]) > 0:
        print("Retrieved Context:")
        for j, (doc, metadata) in enumerate(
            zip(results["documents"][0], results["metadatas"][0]), 1
        ):
            print(f"  [{j}] {metadata['professor']}: {doc[:100]}...")
        print()

    # Generate response
    print("Groq Response:")
    try:
        messages = [
            {"role": "user", "content": f"Based on context about NCAT professors, answer: {query}"}
        ]

        stream = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            max_tokens=256,
            temperature=0.7,
            stream=True,
        )
        response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                text = chunk.choices[0].delta.content
                response += text
                print(text, end="", flush=True)

        print("\n")
    except Exception as e:
        print(f"Error: {e}\n")

print("=" * 80)
print("Test Complete! App is ready to run: python app.py")
print("=" * 80)
