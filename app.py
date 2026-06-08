import os
from dotenv import load_dotenv
import gradio as gr
import chromadb
from chromadb.utils import embedding_functions
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Initialize Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set. Please add it to your .env file.")

groq_client = Groq(api_key=GROQ_API_KEY)

# System prompt for the NCAT CS Advisor
SYSTEM_PROMPT = """You are a helpful and friendly NCAT Computer Science Advisor. Your role is to help students learn about Computer Science professors at North Carolina A&T State University.

IMPORTANT RULES:
1. Answer ONLY using the provided context blocks below.
2. If the context does not contain the answer, state clearly: "I don't have information about this in my knowledge base."
3. Never guess, assume, or hallucinate professor data - stick to what's provided.
4. Always cite which professor the information came from when relevant.
5. Be conversational and friendly, but accurate and concise.

You have access to professor information including:
- Teaching history and courses taught
- Research interests and publications
- Student reviews and feedback
- Office locations and contact information
- Active research areas

Use this information to help students make informed decisions about their classes and research advisors."""


def setup_chromadb():
    """Initialize ChromaDB with BAAI/bge-large-en-v1.5 embeddings."""
    # Initialize persistent ChromaDB client
    client = chromadb.PersistentClient(path="./chroma_db_bge")

    # Use stronger BGE embedding model
    bge_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="BAAI/bge-large-en-v1.5"
    )

    # Get collection
    collection = client.get_or_create_collection(
        name="ncat_professors_bge",
        embedding_function=bge_ef,
        metadata={"hnsw:space": "cosine"}
    )

    return collection


def format_context(results):
    """Format retrieved chunks into a clean context block for the prompt."""
    if not results["documents"] or len(results["documents"][0]) == 0:
        return "No relevant information found in the knowledge base."

    context_parts = []
    for i, (doc, metadata) in enumerate(
        zip(results["documents"][0], results["metadatas"][0]), 1
    ):
        professor = metadata.get("professor", "Unknown")
        context_parts.append(f"[Source {i} - {professor}]\n{doc}")

    return "\n\n---\n\n".join(context_parts)


def generate_answer(user_query, collection):
    """Query the vector store and generate an answer using Groq with streaming."""
    # Retrieve top-3 relevant chunks
    results = collection.query(
        query_texts=[user_query],
        n_results=3
    )

    # Format context for the prompt
    context = format_context(results)

    # Build the messages for Groq
    messages = [
        {
            "role": "user",
            "content": f"""Based on the following context about NCAT Computer Science professors, answer the user's question.

CONTEXT:
{context}

USER QUESTION:
{user_query}"""
        }
    ]

    # Stream response from Groq
    full_response = ""
    try:
        stream = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *messages
            ],
            max_tokens=1024,
            temperature=0.7,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                full_response += chunk.choices[0].delta.content
                yield full_response
    except Exception as e:
        error_msg = f"Error querying Groq API: {str(e)}"
        print(error_msg)
        yield error_msg


def chat_with_advisor(message, history, collection):
    """Gradio callback function for chat interface."""
    # Generate response with streaming
    response = ""
    for partial_response in generate_answer(message, collection):
        response = partial_response

    return response


def launch_interface():
    """Launch the Gradio chat interface."""
    # Initialize ChromaDB collection
    collection = setup_chromadb()

    # Create the chat interface
    demo = gr.ChatInterface(
        fn=lambda message, history: chat_with_advisor(message, history, collection),
        examples=[
            "What did Dr. Xiaohong Yuan publish in 2024 regarding network security?",
            "Where is Dr. Tony Gwyn's office located?",
            "What courses does Dr. Letu Qingge teach?",
            "Tell me about Dr. Kelvin Bryant's research interests.",
            "What do students think about Professor Huiming Yu?",
        ],
        title="NCAT Computer Science Professor Advisor",
        description="Ask questions about Computer Science professors at NC A&T State University. This AI advisor has access to professor information including teaching history, research, student reviews, and contact details."
    )

    # Launch the interface
    demo.launch(share=False, server_name="127.0.0.1", server_port=7860)


if __name__ == "__main__":
    print("Initializing NCAT CS Professor Advisor...")
    print("ChromaDB will load from: ./chroma_db_bge")
    print("Using embedding model: BAAI/bge-large-en-v1.5")
    print("\nLaunching Gradio interface on http://127.0.0.1:7860")
    print("Press Ctrl+C to stop the server.\n")

    launch_interface()
