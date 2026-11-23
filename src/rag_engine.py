import os
import glob
import math
import re

class RAGEngine:
    def __init__(self, docs_dir=None):
        if docs_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.docs_dir = os.path.join(base_dir, "data", "documents")
        else:
            self.docs_dir = docs_dir

        self.chunks = []
        self._load_and_chunk_documents()

    def _load_and_chunk_documents(self):
        """Loads all text and markdown files in the documents directory and splits into chunks."""
        self.chunks = []
        if not os.path.exists(self.docs_dir):
            return

        doc_files = glob.glob(os.path.join(self.docs_dir, "*.txt")) + glob.glob(os.path.join(self.docs_dir, "*.md"))
        for file_path in doc_files:
            filename = os.path.basename(file_path)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Split by sections or double newlines
                raw_sections = [s.strip() for s in content.split("\n\n") if len(s.strip()) > 40]
                for idx, section in enumerate(raw_sections):
                    self.chunks.append({
                        "id": f"{filename}_{idx}",
                        "source": filename,
                        "content": section
                    })
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

    def search(self, query: str, top_k: int = 3) -> list[dict]:
        """Performs lexical and keyword-relevance matching across document chunks."""
        if not self.chunks:
            return []

        query_tokens = set(re.findall(r"\w+", query.lower()))
        if not query_tokens:
            return self.chunks[:top_k]

        scored_chunks = []
        for chunk in self.chunks:
            chunk_tokens = re.findall(r"\w+", chunk["content"].lower())
            chunk_token_set = set(chunk_tokens)
            
            # Simple TF-IDF inspired score
            matches = query_tokens.intersection(chunk_token_set)
            score = 0.0
            for term in matches:
                # Frequency in chunk
                tf = chunk_tokens.count(term) / (len(chunk_tokens) + 1)
                score += tf * (1.0 + math.log(len(self.chunks) / (1 + sum(1 for c in self.chunks if term in c["content"].lower()))))

            if score > 0:
                scored_chunks.append((score, chunk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [chunk for score, chunk in scored_chunks[:top_k]]

    def answer_question(self, user_question: str, llm_engine=None) -> dict:
        """Retrieves relevant context and generates a grounded, cited answer."""
        retrieved_docs = self.search(user_question, top_k=3)
        if not retrieved_docs:
            context = "No specific flight documents matched this query."
            citations = []
        else:
            context = "\n\n".join([f"--- Source: {doc['source']} ---\n{doc['content']}" for doc in retrieved_docs])
            citations = list(set([doc['source'] for doc in retrieved_docs]))

        if llm_engine and getattr(llm_engine, 'client', None):
            prompt = f"""You are AstraOps, an intelligent Space Mission Knowledge Copilot.
Answer the user's question using ONLY the provided mission documentation.

GROUND RULES:
1. Always ground your answer in the provided context.
2. Explicitly cite the document source (e.g. [Document-Name.txt]).
3. If the context does not contain the answer, truthfully say: "The available flight manuals do not contain information regarding this topic." Never hallucinate technical specs.

CONTEXT:
{context}

USER QUESTION:
{user_question}
"""
            answer = llm_engine._generate_llm_response(prompt).strip()
        else:
            # Fallback answer synthesis
            if retrieved_docs:
                top_hit = retrieved_docs[0]
                answer = f"**From {top_hit['source']}:**\n\n{top_hit['content']}\n\n*(Note: Configure your GEMINI_API_KEY in .env for full conversational synthesis)*"
            else:
                answer = "I could not find relevant documentation in the mission knowledge base for your query."

        return {
            "answer": answer,
            "citations": citations,
            "retrieved_context": retrieved_docs
        }
