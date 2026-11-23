import os
import glob
import math
import re

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

class RAGEngine:
    def __init__(self, docs_dir=None, api_key: str = None):
        if docs_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.docs_dir = os.path.join(base_dir, "data", "documents")
        else:
            self.docs_dir = docs_dir

        self.api_key = api_key
        self.chunks = []
        self._load_and_chunk_documents()

    def _load_and_chunk_documents(self):
        """Loads all text and markdown files in the documents directory, splits into contextual chunks, and generates vector embeddings."""
        self.chunks = []
        if not os.path.exists(self.docs_dir):
            return

        doc_files = glob.glob(os.path.join(self.docs_dir, "*.txt")) + glob.glob(os.path.join(self.docs_dir, "*.md"))
        for file_path in doc_files:
            filename = os.path.basename(file_path)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Extract first non-empty header line as document title
                first_line = next((line.strip().replace("#", "").strip() for line in content.splitlines() if line.strip()), filename)
                
                # Split by sections or double newlines
                raw_sections = [s.strip() for s in content.split("\n\n") if len(s.strip()) > 30]
                for idx, section in enumerate(raw_sections):
                    # Prepend document title to every chunk for context inheritance
                    chunk_text = f"Document: {first_line} ({filename})\n\n{section}"
                    embedding = self._compute_dense_embedding(chunk_text)
                    self.chunks.append({
                        "id": f"{filename}_{idx}",
                        "source": filename,
                        "content": chunk_text,
                        "embedding": embedding
                    })
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

    def _compute_dense_embedding(self, text: str) -> list[float]:
        """
        Generates a normalized semantic dense vector embedding.
        Uses a 128-dimensional character n-gram hashing and subword frequency projection
        with L2-normalization for fast, deterministic, offline-resilient cosine similarity.
        """
        dim = 128
        vec = [0.0] * dim
        clean_text = text.lower()
        words = re.findall(r"\w+", clean_text)
        
        # Subword and term projections
        for w in words:
            h = hash(w) % dim
            vec[h] += 1.0
            # Also capture 3-gram subwords for morphological root matching
            for i in range(len(w) - 2):
                tri = w[i:i+3]
                h_tri = hash(tri) % dim
                vec[h_tri] += 0.5

        # L2 Normalization
        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 0:
            vec = [v / norm for v in vec]
        return vec

    def _cosine_similarity(self, vec_a: list[float], vec_b: list[float]) -> float:
        """Calculates cosine similarity between two normalized vectors."""
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        return sum(a * b for a, b in zip(vec_a, vec_b))

    def ingest_uploaded_file(self, filename: str, file_bytes: bytes) -> tuple[bool, str]:
        """Ingests an uploaded PDF, TXT, or MD file and dynamically updates the knowledge base with embeddings."""
        try:
            os.makedirs(self.docs_dir, exist_ok=True)
            content = ""
            
            if filename.lower().endswith(".pdf"):
                import io
                import pypdf
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                pages_text = []
                for p_idx, page in enumerate(reader.pages):
                    t = page.extract_text()
                    if t and t.strip():
                        pages_text.append(f"--- Page {p_idx+1} ---\n{t.strip()}")
                content = "\n\n".join(pages_text)
                target_filename = f"{os.path.splitext(filename)[0]}_extracted.txt"
            else:
                content = file_bytes.decode("utf-8", errors="ignore")
                target_filename = filename

            if not content.strip():
                return False, "Uploaded file appears to be empty or unreadable."

            save_path = os.path.join(self.docs_dir, target_filename)
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Reload knowledge chunks and regenerate embeddings immediately
            self._load_and_chunk_documents()
            return True, f"Successfully indexed '{filename}' ({len(self.chunks)} total knowledge chunks available)."
        except Exception as e:
            return False, str(e)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Advanced Hybrid Retrieval: Combines Dense Vector Semantic Cosine Similarity
        with BM25/TF-IDF Lexical Term Matching.
        """
        if not self.chunks:
            return []

        # 1. Compute Query Dense Embedding
        q_vec = self._compute_dense_embedding(query)

        # 2. Extract Query Lexical Tokens (minus stop-words)
        stop_words = {"what", "is", "are", "the", "a", "an", "of", "in", "to", "for", "and", "about", "how", "tell", "me", "does"}
        raw_tokens = set(re.findall(r"\w+", query.lower()))
        query_tokens = raw_tokens - stop_words

        scored_chunks = []
        for chunk in self.chunks:
            # Semantic Cosine Similarity
            chunk_vec = chunk.get("embedding")
            semantic_sim = self._cosine_similarity(q_vec, chunk_vec) if chunk_vec else 0.0

            # Lexical TF-IDF Keyword Overlap
            chunk_tokens = re.findall(r"\w+", chunk["content"].lower())
            chunk_token_set = set(chunk_tokens)
            matches = query_tokens.intersection(chunk_token_set) if query_tokens else set()
            
            lexical_score = 0.0
            if matches:
                for term in matches:
                    tf = chunk_tokens.count(term)
                    idf = math.log((len(self.chunks) + 1) / (1 + sum(1 for c in self.chunks if term in c["content"].lower())))
                    lexical_score += tf * idf

            # Normalize lexical score to [0, 1] range approximately
            norm_lexical = min(1.0, lexical_score / 15.0) if lexical_score > 0 else 0.0

            # Hybrid Score Fusion: 65% Semantic Similarity + 35% Lexical Overlap
            hybrid_score = (0.65 * semantic_sim) + (0.35 * norm_lexical)

            # Keep chunk if there is meaningful relevance
            if hybrid_score > 0.15:
                chunk_copy = dict(chunk)
                chunk_copy["hybrid_score"] = round(hybrid_score, 4)
                chunk_copy["semantic_similarity"] = round(semantic_sim, 4)
                chunk_copy["lexical_overlap"] = round(norm_lexical, 4)
                scored_chunks.append((hybrid_score, chunk_copy))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [chunk for score, chunk in scored_chunks[:top_k]]

    def answer_question(self, user_question: str, llm_engine=None, mode: str = "hybrid") -> dict:
        """
        Retrieves relevant context using hybrid semantic retrieval and generates
        a grounded, cited answer in either Strict Defense Mode or Hybrid Copilot Mode.
        """
        retrieved_docs = self.search(user_question, top_k=3)
        
        # Programmatic Zero-Hallucination Gate for Strict Mode:
        # If the highest hybrid retrieval score is below relevance threshold, refuse immediately.
        top_score = retrieved_docs[0].get("hybrid_score", 0.0) if retrieved_docs else 0.0
        
        if mode == "strict" and (not retrieved_docs or top_score < 0.28):
            return {
                "answer": "The available flight manuals do not contain information regarding this topic.",
                "citations": [],
                "retrieved_context": []
            }

        if not retrieved_docs:
            context = "No specific flight documents matched this query."
            citations = []
        else:
            context = "\n\n".join([f"--- Source: {doc['source']} (Relevance Score: {doc.get('hybrid_score', 'N/A')}) ---\n{doc['content']}" for doc in retrieved_docs])
            citations = list(set([doc['source'] for doc in retrieved_docs]))

        if llm_engine and getattr(llm_engine, 'client', None):
            if mode == "strict":
                prompt = f"""You are Spacepilot, an intelligent Space Mission Knowledge Copilot operating in STRICT DEFENSE GROUNDING MODE.
Answer the user's question using ONLY the provided mission documentation.

GROUND RULES:
1. Always ground your answer strictly in the provided context.
2. Explicitly cite the document source (e.g. [Document-Name.txt]).
3. If the context does not contain the answer, truthfully say: "The available flight manuals do not contain information regarding this topic." Never hallucinate technical specs.

CONTEXT:
{context}

USER QUESTION:
{user_question}
"""
            else:
                prompt = f"""You are Spacepilot, an intelligent Space Mission Knowledge Copilot operating in HYBRID INTELLIGENCE MODE.
Answer the user's question with high technical accuracy.

GROUND RULES (HYBRID INTELLIGENCE MODE):
1. PRIMARY SOURCE: If the question relates to the provided mission documentation context below, ground your response in the text and explicitly cite the source file (e.g. [Document-Name.txt]).
2. GENERAL KNOWLEDGE FALLBACK: If the question asks about general astronomy, space exploration, astrophysics, or planetary science NOT covered in the provided flight manuals, start by stating:
   "*(Note: This topic is outside your current spacecraft flight manuals, but here is the general scientific explanation:)*"
   and then provide a comprehensive, clear, and professional explanation using your general knowledge.

CONTEXT:
{context}

USER QUESTION:
{user_question}
"""
            answer = llm_engine._generate_llm_response(prompt).strip()
            if not answer:
                err_hint = f"\n\n*(Notice: LLM API issue detected: {getattr(llm_engine, 'last_error', 'No response')})*" if getattr(llm_engine, 'last_error', None) else ""
                if retrieved_docs:
                    top_hit = retrieved_docs[0]
                    answer = f"**From {top_hit['source']}:**\n\n{top_hit['content']}{err_hint}"
                else:
                    answer = f"The available flight manuals do not contain information regarding this topic.{err_hint}"
        else:
            # Fallback answer synthesis
            if retrieved_docs:
                top_hit = retrieved_docs[0]
                answer = f"**From {top_hit['source']} (Score: {top_hit.get('hybrid_score', 'N/A')}):**\n\n{top_hit['content']}\n\n*(Note: Configure your GEMINI_API_KEY for conversational multi-sentence synthesis)*"
            else:
                answer = "I could not find relevant documentation in the mission knowledge base for your query."

        return {
            "answer": answer,
            "citations": citations,
            "retrieved_context": retrieved_docs
        }
