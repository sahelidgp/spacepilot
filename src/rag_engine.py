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
        """Loads all text and markdown files in the documents directory and splits into contextual chunks."""
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
                    self.chunks.append({
                        "id": f"{filename}_{idx}",
                        "source": filename,
                        "content": chunk_text
                    })
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

    def ingest_uploaded_file(self, filename: str, file_bytes: bytes) -> tuple[bool, str]:
        """Ingests an uploaded PDF, TXT, or MD file and dynamically updates the knowledge base."""
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

            # Reload knowledge chunks immediately
            self._load_and_chunk_documents()
            return True, f"Successfully indexed '{filename}' ({len(self.chunks)} total knowledge chunks available)."
        except Exception as e:
            return False, str(e)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Performs lexical and keyword-relevance matching across document chunks."""
        if not self.chunks:
            return []

        stop_words = {"what", "is", "are", "the", "a", "an", "of", "in", "to", "for", "and", "about", "how", "tell", "me", "does"}
        raw_tokens = set(re.findall(r"\w+", query.lower()))
        query_tokens = raw_tokens - stop_words
        
        if not query_tokens:
            return []

        scored_chunks = []
        for chunk in self.chunks:
            chunk_tokens = re.findall(r"\w+", chunk["content"].lower())
            chunk_token_set = set(chunk_tokens)
            
            # Match score with token frequency
            matches = query_tokens.intersection(chunk_token_set)
            score = 0.0
            for term in matches:
                tf = chunk_tokens.count(term)
                score += tf * (1.0 + math.log(len(self.chunks) / (1 + sum(1 for c in self.chunks if term in c["content"].lower()))))

            if score > 0:
                scored_chunks.append((score, chunk))

        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [chunk for score, chunk in scored_chunks[:top_k]]

    def answer_question(self, user_question: str, llm_engine=None, mode: str = "hybrid") -> dict:
        """Retrieves relevant context and generates a grounded, cited answer in either Strict or Hybrid mode."""
        retrieved_docs = self.search(user_question, top_k=3)
        if not retrieved_docs:
            context = "No specific flight documents matched this query."
            citations = []
        else:
            context = "\n\n".join([f"--- Source: {doc['source']} ---\n{doc['content']}" for doc in retrieved_docs])
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
                answer = f"**From {top_hit['source']}:**\n\n{top_hit['content']}\n\n*(Note: Configure your GEMINI_API_KEY in .env for full conversational synthesis)*"
            else:
                answer = "I could not find relevant documentation in the mission knowledge base for your query."

        return {
            "answer": answer,
            "citations": citations,
            "retrieved_context": retrieved_docs
        }
