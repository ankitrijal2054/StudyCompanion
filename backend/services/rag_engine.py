import os
import json
import chromadb
from chromadb.config import Settings
from pathlib import Path
from openai import OpenAI
from typing import List, Dict, Optional
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable must be set in .env file")
openai_client = OpenAI(api_key=api_key)

# ChromaDB configuration
CHROMA_DB_PATH = Path(__file__).parent.parent / "chroma_db"
CHROMA_DB_PATH.mkdir(exist_ok=True)

# Initialize ChromaDB with persistent storage
chroma_client = chromadb.PersistentClient(
    path=str(CHROMA_DB_PATH),
    settings=Settings(anonymized_telemetry=False)
)

# Collection name
COLLECTION_NAME = "session_transcripts"


def get_collection():
    """Get or create the session_transcripts collection"""
    try:
        collection = chroma_client.get_collection(name=COLLECTION_NAME)
        print(f"✅ Found existing collection: {COLLECTION_NAME}")
    except:
        collection = chroma_client.create_collection(
            name=COLLECTION_NAME,
            metadata={"description": "Tutoring session transcripts for RAG retrieval"}
        )
        print(f"✅ Created new collection: {COLLECTION_NAME}")
    return collection


def generate_embedding(text: str) -> List[float]:
    """Generate embedding using OpenAI's text-embedding-3-small model"""
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def load_transcripts_from_directory(transcripts_dir: Path) -> List[Dict]:
    """Load all transcript JSON files from directory"""
    transcripts = []
    for transcript_file in transcripts_dir.glob("*.json"):
        with open(transcript_file, 'r') as f:
            transcript_data = json.load(f)
            transcripts.append(transcript_data)
    return transcripts


def create_transcript_text(transcript: Dict) -> str:
    """Create searchable text from transcript"""
    # Combine key fields for embedding
    parts = [
        f"Subject: {transcript.get('subject', '')}",
        f"Topic: {transcript.get('topic', '')}",
    ]
    
    # Add tutor notes (very important for context)
    if 'tutor_notes' in transcript:
        parts.append(f"Tutor Notes: {transcript['tutor_notes']}")
    
    # Add key concepts
    if 'key_concepts' in transcript:
        parts.append(f"Key Concepts: {', '.join(transcript['key_concepts'])}")
    
    # Add dialogue (condensed)
    if 'dialogue' in transcript:
        dialogue_text = " ".join([
            f"{msg.get('speaker', '').title()}: {msg.get('message', '')}"
            for msg in transcript['dialogue']
        ])
        parts.append(f"Discussion: {dialogue_text}")
    
    return "\n".join(parts)


def embed_and_store_transcripts(transcripts_dir: Optional[Path] = None):
    """Embed all transcripts and store in ChromaDB"""
    if transcripts_dir is None:
        transcripts_dir = Path(__file__).parent.parent.parent / "data" / "transcripts"
    
    print(f"📚 Loading transcripts from: {transcripts_dir}")
    transcripts = load_transcripts_from_directory(transcripts_dir)
    print(f"✅ Loaded {len(transcripts)} transcripts")
    
    collection = get_collection()
    
    # Check if collection already has documents
    existing_count = collection.count()
    if existing_count > 0:
        print(f"⚠️  Collection already has {existing_count} documents. Skipping embedding.")
        return
    
    print(f"🔮 Generating embeddings for {len(transcripts)} transcripts...")
    
    ids = []
    embeddings = []
    metadatas = []
    documents = []
    
    for i, transcript in enumerate(transcripts):
        # Create unique ID from transcript_id
        transcript_id = transcript.get('transcript_id', f"transcript_{i}")
        transcript_id_clean = transcript_id.replace(' ', '_').lower()
        
        # Create searchable text
        text = create_transcript_text(transcript)
        
        # Generate embedding
        embedding = generate_embedding(text)
        
        # Prepare metadata
        metadata = {
            "student_id": transcript.get('student_id', ''),
            "subject": transcript.get('subject', ''),
            "topic": transcript.get('topic', ''),
            "session_date": str(transcript.get('session_date', '')),
            "transcript_id": transcript_id_clean,
            "tutor_name": transcript.get('tutor_name', ''),
            "difficulty": transcript.get('difficulty', 'intermediate'),
        }
        
        ids.append(transcript_id_clean)
        embeddings.append(embedding)
        metadatas.append(metadata)
        documents.append(text)
        
        print(f"  ✅ Embedded: {transcript_id_clean} ({i+1}/{len(transcripts)})")
    
    # Batch add to ChromaDB
    print(f"\n💾 Storing {len(ids)} embeddings in ChromaDB...")
    collection.add(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=documents
    )
    
    print(f"✅ Successfully stored {len(ids)} transcript embeddings!")
    print(f"📊 Collection now contains {collection.count()} documents")


def retrieve_context(query: str, student_id: str, top_k: int = 3) -> List[Dict]:
    """
    Retrieve relevant context using semantic search
    
    Args:
        query: Search query string
        student_id: Student ID to filter results (prevents cross-student data leakage)
        top_k: Number of results to return
    
    Returns:
        List of dictionaries with retrieved context including metadata and distance scores
    """
    collection = get_collection()
    
    # Generate embedding for query
    query_embedding = generate_embedding(query)
    
    # Query ChromaDB with student_id filter
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"student_id": student_id}  # Filter by student_id
    )
    
    # Format results
    retrieved_contexts = []
    if results['ids'] and len(results['ids'][0]) > 0:
        for i in range(len(results['ids'][0])):
            context = {
                "transcript_id": results['ids'][0][i],
                "document": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i] if 'distances' in results else None
            }
            retrieved_contexts.append(context)
    
    return retrieved_contexts


def test_retrieval():
    """Test RAG retrieval with sample queries"""
    print("\n🧪 Testing RAG Retrieval Quality...\n")
    
    test_queries = [
        {
            "query": "What did we learn about ionic bonds?",
            "student_id": "S001",
            "expected": "Should return Ava's chemistry transcripts about ionic bonding"
        },
        {
            "query": "How do I solve quadratic equations?",
            "student_id": "S002",
            "expected": "Should return Marcus's algebra transcripts"
        },
        {
            "query": "Thermodynamics concepts",
            "student_id": "S003",
            "expected": "Should return Priya's physics transcripts"
        },
        {
            "query": "What about covalent bonding?",
            "student_id": "S001",
            "expected": "Should return Ava's chemistry transcripts (student-specific)"
        }
    ]
    
    for i, test in enumerate(test_queries, 1):
        print(f"Test {i}: {test['query']}")
        print(f"  Student: {test['student_id']}")
        print(f"  Expected: {test['expected']}")
        
        results = retrieve_context(test['query'], test['student_id'], top_k=3)
        
        if results:
            print(f"  ✅ Retrieved {len(results)} results:")
            for j, result in enumerate(results, 1):
                print(f"    {j}. {result['metadata'].get('subject')} - {result['metadata'].get('topic')}")
                print(f"       Distance: {result['distance']:.4f}" if result['distance'] else "")
        else:
            print(f"  ⚠️  No results found")
        
        print()
    
    print("✅ Retrieval testing complete!")


if __name__ == "__main__":
    print("🚀 Initializing RAG Pipeline...\n")
    
    # Step 1: Initialize collection
    print("Step 1: Initializing ChromaDB collection...")
    collection = get_collection()
    
    # Step 2: Embed and store transcripts
    print("\nStep 2: Embedding and storing transcripts...")
    embed_and_store_transcripts()
    
    # Step 3: Test retrieval
    print("\nStep 3: Testing semantic search...")
    test_retrieval()
    
    print("\n✅ RAG Pipeline setup complete!")
