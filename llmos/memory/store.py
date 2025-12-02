"""
Memory Store - L4 Storage (Semantic Memory)
Vector database for unstructured knowledge
"""

import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class MemoryEntry:
    """A memory entry in semantic storage"""
    id: str
    text: str
    embedding: List[float]
    metadata: Dict[str, Any]
    created_at: str

    def __post_init__(self):
        if isinstance(self.embedding, np.ndarray):
            self.embedding = self.embedding.tolist()


class MemoryStore:
    """
    Semantic memory store (L4 Storage)
    Simple vector database using cosine similarity
    """

    def __init__(self, storage_path: Path):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        self.memories: List[MemoryEntry] = []
        self._load_memories()

    def _load_memories(self):
        """Load memories from disk"""
        memory_file = self.storage_path / "semantic_memory.json"

        if memory_file.exists():
            with open(memory_file, 'r') as f:
                data = json.load(f)
                self.memories = [MemoryEntry(**entry) for entry in data]

    def _save_memories(self):
        """Save memories to disk"""
        memory_file = self.storage_path / "semantic_memory.json"

        with open(memory_file, 'w') as f:
            data = [asdict(entry) for entry in self.memories]
            json.dump(data, f, indent=2)

    def _simple_embedding(self, text: str) -> np.ndarray:
        """
        Create a simple text embedding
        TODO: Replace with actual embedding model (e.g., sentence-transformers)
        """
        # Very simple word-based embedding for now
        # In production, use proper embedding models
        words = text.lower().split()
        # Create a 384-dimensional vector (common embedding size)
        embedding = np.zeros(384)

        for i, word in enumerate(words[:384]):
            # Simple hash-based embedding
            hash_val = hash(word)
            embedding[i % 384] += (hash_val % 1000) / 1000.0

        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm

        return embedding

    def add_memory(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MemoryEntry:
        """
        Add a memory entry

        Args:
            text: Text to store
            metadata: Additional metadata

        Returns:
            Created MemoryEntry
        """
        embedding = self._simple_embedding(text)

        entry = MemoryEntry(
            id=f"mem_{len(self.memories)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            text=text,
            embedding=embedding.tolist(),
            metadata=metadata or {},
            created_at=datetime.now().isoformat()
        )

        self.memories.append(entry)
        self._save_memories()

        return entry

    def search(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.5
    ) -> List[tuple[MemoryEntry, float]]:
        """
        Search for similar memories

        Args:
            query: Search query
            top_k: Number of results to return
            threshold: Minimum similarity threshold

        Returns:
            List of (MemoryEntry, similarity_score) tuples
        """
        if not self.memories:
            return []

        query_embedding = self._simple_embedding(query)

        # Calculate cosine similarities
        similarities = []
        for memory in self.memories:
            memory_embedding = np.array(memory.embedding)
            similarity = np.dot(query_embedding, memory_embedding)
            if similarity >= threshold:
                similarities.append((memory, float(similarity)))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    def clear(self):
        """Clear all memories"""
        self.memories = []
        self._save_memories()
