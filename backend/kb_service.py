import numpy as np
import os
import json
from nova_client import NovaClient
from typing import List, Dict, Any

class KnowledgeBaseService:
    def __init__(self, nova: NovaClient):
        self.nova = nova
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.kb_file = os.path.join(base_dir, "data", "knowledge_base.json")
        self.embeddings_file = os.path.join(base_dir, "data", "embeddings.npy")
        self._load_kb()

    def _load_kb(self):
        if not os.path.exists(os.path.dirname(self.kb_file)):
            os.makedirs(os.path.dirname(self.kb_file))
            
        if os.path.exists(self.kb_file):
            with open(self.kb_file, "r") as f:
                self.documents = json.load(f)
        else:
            # Default mock documents for production showcase
            self.documents = [
                {"text": "NovaAssist CX refund policy: 30 days money-back guarantee for all damaged products.", "source": "Policy Manual"},
                {"text": "To reset your CX-5566 device, hold the power button for 10 seconds until the light turns red.", "source": "Manual"},
                {"text": "Our support hours are 24/7. Live chat is the fastest way to get help.", "source": "Contact Info"}
            ]
            with open(self.kb_file, "w") as f:
                json.dump(self.documents, f)
        
        self._index_kb()

    def _index_kb(self):
        """
        Builds a simple vector index. Correct way in production: OpenSearch or Pinecone.
        """
        if os.path.exists(self.embeddings_file):
            self.vectors = np.load(self.embeddings_file)
        else:
            print("Indexing Knowledge Base...")
            self.vectors = []
            for doc in self.documents:
                self.vectors.append(self.nova.get_embeddings(doc["text"]))
            self.vectors = np.array(self.vectors)
            np.save(self.embeddings_file, self.vectors)

    def search(self, query: str, top_k: int = 2) -> List[str]:
        query_vec = np.array(self.nova.get_embeddings(query))
        
        # Calculate cosine similarity with small epsilon to avoid division by zero
        norms = np.linalg.norm(self.vectors, axis=1) * np.linalg.norm(query_vec)
        norms[norms == 0] = 1e-10
        
        similarities = np.dot(self.vectors, query_vec) / norms
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = [self.documents[i]["text"] for i in top_indices if similarities[i] > 0.4]
        return results if results else ["No specific information found in the knowledge base."]
