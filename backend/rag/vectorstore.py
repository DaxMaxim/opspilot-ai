"""ChromaDB vector store setup and policy retrieval."""
import os
from pathlib import Path
import chromadb
from config import CHROMA_PATH, POLICIES_DIR, OPENAI_API_KEY, EMBEDDING_MODEL


def get_chroma_client():
    """Get or create a persistent ChromaDB client."""
    Path(CHROMA_PATH).mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=CHROMA_PATH)


def get_collection():
    """Get the policy documents collection."""
    client = get_chroma_client()
    return client.get_or_create_collection(
        name="policy_documents",
        metadata={"hnsw:space": "cosine"},
    )


def load_and_chunk_policies() -> list[dict]:
    """Load policy markdown files and chunk them by section."""
    chunks = []
    policies_dir = Path(POLICIES_DIR)
    
    if not policies_dir.exists():
        return chunks
    
    for md_file in sorted(policies_dir.glob("*.md")):
        content = md_file.read_text()
        filename = md_file.stem
        
        # Extract policy metadata from header
        lines = content.split("\n")
        policy_name = lines[0].replace("# Policy: ", "").strip() if lines else filename
        policy_id = ""
        category = ""
        for line in lines[:10]:
            if "Policy ID:" in line:
                policy_id = line.split("**Policy ID:**")[-1].strip()
            if "Category:" in line:
                category = line.split("**Category:**")[-1].strip()
        
        # Chunk by sections (## headers)
        current_section = ""
        current_content = []
        section_num = 0
        
        for line in lines:
            if line.startswith("## "):
                # Save previous section
                if current_content:
                    chunk_text = "\n".join(current_content).strip()
                    if chunk_text and len(chunk_text) > 50:
                        chunks.append({
                            "id": f"{filename}_s{section_num}",
                            "content": chunk_text,
                            "metadata": {
                                "policy_id": policy_id,
                                "policy_name": policy_name,
                                "section": current_section,
                                "category": category,
                                "source_file": md_file.name,
                            },
                        })
                section_num += 1
                current_section = line.replace("## ", "").strip()
                current_content = [line]
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            chunk_text = "\n".join(current_content).strip()
            if chunk_text and len(chunk_text) > 50:
                chunks.append({
                    "id": f"{filename}_s{section_num}",
                    "content": chunk_text,
                    "metadata": {
                        "policy_id": policy_id,
                        "policy_name": policy_name,
                        "section": current_section,
                        "category": category,
                        "source_file": md_file.name,
                    },
                })
    
    return chunks


def seed_vector_store():
    """Seed the ChromaDB collection with policy document chunks."""
    collection = get_collection()
    
    # Check if already seeded
    if collection.count() > 0:
        print(f"Vector store already contains {collection.count()} documents. Skipping seed.")
        return collection.count()
    
    chunks = load_and_chunk_policies()
    if not chunks:
        print("No policy documents found to seed.")
        return 0
    
    # Add chunks to ChromaDB (ChromaDB handles embedding via default model)
    collection.add(
        ids=[c["id"] for c in chunks],
        documents=[c["content"] for c in chunks],
        metadatas=[c["metadata"] for c in chunks],
    )
    
    print(f"Seeded {len(chunks)} policy chunks into vector store.")
    return len(chunks)


def retrieve_policies(query: str, n_results: int = 5) -> list[dict]:
    """Retrieve relevant policy chunks for a given query and group by policy ID."""
    collection = get_collection()
    
    if collection.count() == 0:
        return []
    
    # Fetch slightly more to account for grouping duplicates
    fetch_k = min(n_results + 3, collection.count())
    results = collection.query(
        query_texts=[query],
        n_results=fetch_k,
    )
    
    policy_dict = {}
    if results and results["documents"]:
        for i, doc in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i] if results["metadatas"] else {}
            distance = results["distances"][0][i] if results["distances"] else 1.0
            relevance = max(0, 1 - distance)
            
            p_id = metadata.get("policy_id", "UNKNOWN")
            p_name = metadata.get("policy_name", "Unknown Policy")
            section = metadata.get("section", "")
            
            if p_id not in policy_dict:
                # First time seeing this policy
                policy_dict[p_id] = {
                    "policy_id": p_id,
                    "policy_name": p_name,
                    "sections": [section] if section else [],
                    "content": f"## {section}\n{doc}" if section else doc,
                    "relevance_score": round(relevance, 3)
                }
            else:
                # We already have a chunk from this policy, merge them
                if section and section not in policy_dict[p_id]["sections"]:
                    policy_dict[p_id]["sections"].append(section)
                    policy_dict[p_id]["content"] += f"\n\n## {section}\n{doc}"
            
            if len(policy_dict) >= n_results:
                break
                
    # Format for backwards compatibility
    policies = []
    for p in policy_dict.values():
        p["section"] = ", ".join(p.pop("sections"))
        policies.append(p)
        
    return policies
