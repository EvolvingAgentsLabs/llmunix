#!/usr/bin/env python3
"""
Memory Indexer - Indexed Markdown Architecture for LLMunix

This script creates and maintains:
1. SQLite database for structured metadata queries
2. Vector database (ChromaDB) for semantic similarity search
3. Keeps Markdown files as the source of truth

The indexer runs after MemoryConsolidationAgent creates/updates memory files.
"""

import os
import sqlite3
import yaml
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Configuration
BASE_DIR = Path(__file__).parent.parent.parent
SYSTEM_DIR = BASE_DIR / "system"
PROJECTS_DIR = BASE_DIR / "projects"
SQLITE_PATH = SYSTEM_DIR / "memory_index.sqlite"
CHROMA_PATH = SYSTEM_DIR / "chroma_db"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast, lightweight sentence transformer


class MemoryIndexer:
    """Manages the Indexed Markdown Architecture for LLMunix memory."""

    def __init__(self):
        """Initialize the indexer with SQLite and ChromaDB connections."""
        self.db_conn = self._init_sqlite()
        self.chroma_client = self._init_chromadb()
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.collection = self.chroma_client.get_or_create_collection(
            name="memory_embeddings",
            metadata={"hnsw:space": "cosine"}
        )

    def _init_sqlite(self) -> sqlite3.Connection:
        """Initialize SQLite database with schema."""
        conn = sqlite3.connect(str(SQLITE_PATH))
        cursor = conn.cursor()

        # Create experiences table (maps to memory_log.md entries)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiences (
                experience_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                project_name TEXT,
                goal_description TEXT,
                outcome TEXT,  -- success, failure, success_with_recovery
                task_type TEXT,
                user_sentiment TEXT,  -- neutral, positive, frustrated, pleased, impressed
                execution_cost REAL,
                execution_time_secs REAL,
                error_count INTEGER,
                components_used TEXT,  -- JSON array
                tags TEXT,  -- JSON array
                confidence_score REAL,  -- 0-1
                file_path TEXT NOT NULL,
                content_hash TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create execution traces table (for Learner-Follower pattern)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_traces (
                trace_id TEXT PRIMARY KEY,
                experience_id TEXT,
                goal_signature TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                estimated_cost REAL,
                estimated_time_secs REAL,
                step_count INTEGER,
                success_rate REAL DEFAULT 0.0,
                usage_count INTEGER DEFAULT 0,
                last_used TEXT,
                file_path TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (experience_id) REFERENCES experiences(experience_id)
            )
        """)

        # Create memory relationships table (hierarchical memory)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id TEXT NOT NULL,
                child_id TEXT NOT NULL,
                relationship_type TEXT,  -- causal, temporal, conceptual, contextual
                strength REAL DEFAULT 0.5,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES experiences(experience_id),
                FOREIGN KEY (child_id) REFERENCES experiences(experience_id)
            )
        """)

        # Create indexes for fast queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_outcome ON experiences(outcome)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_task_type ON experiences(task_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentiment ON experiences(user_sentiment)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON experiences(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_confidence ON experiences(confidence_score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trace_goal ON execution_traces(goal_signature)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trace_confidence ON execution_traces(confidence)")

        conn.commit()
        return conn

    def _init_chromadb(self) -> chromadb.Client:
        """Initialize ChromaDB for vector embeddings."""
        CHROMA_PATH.mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(
            path=str(CHROMA_PATH),
            settings=Settings(anonymized_telemetry=False)
        )
        return client

    def _extract_yaml_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        """Extract YAML frontmatter from markdown file."""
        lines = content.split('\n')
        if not lines or lines[0].strip() != '---':
            return None

        yaml_lines = []
        in_frontmatter = False
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                in_frontmatter = False
                break
            yaml_lines.append(line)
            in_frontmatter = True

        if not yaml_lines:
            return None

        try:
            return yaml.safe_load('\n'.join(yaml_lines))
        except yaml.YAMLError:
            return None

    def _calculate_content_hash(self, content: str) -> str:
        """Calculate SHA256 hash of content for change detection."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def index_memory_file(self, file_path: Path, project_name: Optional[str] = None) -> bool:
        """
        Index a single memory markdown file.

        Args:
            file_path: Path to the markdown memory file
            project_name: Optional project name (auto-detected if not provided)

        Returns:
            True if indexed successfully, False otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract YAML frontmatter
            metadata = self._extract_yaml_frontmatter(content)
            if not metadata:
                print(f"Warning: No YAML frontmatter found in {file_path}")
                return False

            # Extract experience ID
            experience_id = metadata.get('experience_id')
            if not experience_id:
                print(f"Warning: No experience_id in {file_path}")
                return False

            # Calculate content hash
            content_hash = self._calculate_content_hash(content)

            # Check if already indexed and unchanged
            cursor = self.db_conn.cursor()
            cursor.execute(
                "SELECT content_hash FROM experiences WHERE experience_id = ?",
                (experience_id,)
            )
            existing = cursor.fetchone()
            if existing and existing[0] == content_hash:
                print(f"Skipping {experience_id}: already indexed and unchanged")
                return True

            # Auto-detect project name from path if not provided
            if not project_name:
                if 'Project_' in str(file_path):
                    project_name = str(file_path).split('Project_')[1].split('/')[0]
                    project_name = f"Project_{project_name}"

            # Insert/update in SQLite
            cursor.execute("""
                INSERT OR REPLACE INTO experiences (
                    experience_id, timestamp, project_name, goal_description,
                    outcome, task_type, user_sentiment, execution_cost,
                    execution_time_secs, error_count, components_used, tags,
                    confidence_score, file_path, content_hash, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                experience_id,
                metadata.get('timestamp', datetime.now().isoformat()),
                project_name or 'system',
                metadata.get('goal', ''),
                metadata.get('outcome', 'unknown'),
                metadata.get('task_type', ''),
                metadata.get('user_sentiment', 'neutral'),
                metadata.get('cost', 0.0),
                metadata.get('execution_time', 0.0),
                metadata.get('error_count', 0),
                json.dumps(metadata.get('components_used', [])),
                json.dumps(metadata.get('tags', [])),
                metadata.get('confidence_score', 0.5),
                str(file_path),
                content_hash,
                datetime.now().isoformat()
            ))

            # Create embedding for semantic search
            # Extract main content (without frontmatter)
            main_content = content.split('---', 2)[-1].strip()
            embedding = self.embedding_model.encode(main_content).tolist()

            # Store in ChromaDB
            self.collection.upsert(
                ids=[experience_id],
                embeddings=[embedding],
                documents=[main_content],
                metadatas=[{
                    'experience_id': experience_id,
                    'project_name': project_name or 'system',
                    'outcome': metadata.get('outcome', 'unknown'),
                    'task_type': metadata.get('task_type', ''),
                    'file_path': str(file_path)
                }]
            )

            self.db_conn.commit()
            print(f"Indexed: {experience_id}")
            return True

        except Exception as e:
            print(f"Error indexing {file_path}: {e}")
            return False

    def index_execution_trace(self, trace_file_path: Path, experience_id: Optional[str] = None) -> bool:
        """
        Index an execution trace YAML file for Learner-Follower pattern.

        Args:
            trace_file_path: Path to execution_trace.yaml
            experience_id: Optional link to source experience

        Returns:
            True if indexed successfully
        """
        try:
            with open(trace_file_path, 'r', encoding='utf-8') as f:
                trace_data = yaml.safe_load(f)

            trace_id = trace_data.get('trace_id')
            if not trace_id:
                print(f"Warning: No trace_id in {trace_file_path}")
                return False

            cursor = self.db_conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO execution_traces (
                    trace_id, experience_id, goal_signature, confidence,
                    estimated_cost, estimated_time_secs, step_count,
                    success_rate, file_path, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                trace_id,
                experience_id,
                trace_data.get('goal_signature', ''),
                trace_data.get('confidence', 0.5),
                trace_data.get('estimated_cost', 0.0),
                trace_data.get('estimated_time_secs', 0.0),
                len(trace_data.get('steps', [])),
                trace_data.get('success_rate', 0.0),
                str(trace_file_path),
                datetime.now().isoformat()
            ))

            self.db_conn.commit()
            print(f"Indexed execution trace: {trace_id}")
            return True

        except Exception as e:
            print(f"Error indexing trace {trace_file_path}: {e}")
            return False

    def query_metadata(self, filters: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Query experiences by structured metadata (SQLite).

        Args:
            filters: Dictionary of filters (outcome, task_type, sentiment, etc.)
            limit: Maximum number of results

        Returns:
            List of matching experience metadata
        """
        cursor = self.db_conn.cursor()

        where_clauses = []
        params = []

        if 'outcome' in filters:
            where_clauses.append("outcome = ?")
            params.append(filters['outcome'])

        if 'task_type' in filters:
            where_clauses.append("task_type = ?")
            params.append(filters['task_type'])

        if 'user_sentiment' in filters:
            where_clauses.append("user_sentiment = ?")
            params.append(filters['user_sentiment'])

        if 'min_confidence' in filters:
            where_clauses.append("confidence_score >= ?")
            params.append(filters['min_confidence'])

        if 'project_name' in filters:
            where_clauses.append("project_name = ?")
            params.append(filters['project_name'])

        where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

        query = f"""
            SELECT experience_id, timestamp, project_name, goal_description,
                   outcome, task_type, user_sentiment, execution_cost,
                   confidence_score, file_path
            FROM experiences
            WHERE {where_sql}
            ORDER BY timestamp DESC
            LIMIT ?
        """

        params.append(limit)
        cursor.execute(query, params)

        results = []
        for row in cursor.fetchall():
            results.append({
                'experience_id': row[0],
                'timestamp': row[1],
                'project_name': row[2],
                'goal_description': row[3],
                'outcome': row[4],
                'task_type': row[5],
                'user_sentiment': row[6],
                'execution_cost': row[7],
                'confidence_score': row[8],
                'file_path': row[9]
            })

        return results

    def query_semantic(self, query_text: str, n_results: int = 5, filters: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        Query experiences by semantic similarity (ChromaDB).

        Args:
            query_text: Natural language query
            n_results: Number of results to return
            filters: Optional metadata filters

        Returns:
            List of semantically similar experiences
        """
        # Create embedding for query
        query_embedding = self.embedding_model.encode(query_text).tolist()

        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filters if filters else None
        )

        # Format results
        formatted_results = []
        if results['ids'] and results['ids'][0]:
            for i, exp_id in enumerate(results['ids'][0]):
                formatted_results.append({
                    'experience_id': exp_id,
                    'distance': results['distances'][0][i],
                    'document': results['documents'][0][i][:200] + '...',  # Preview
                    'metadata': results['metadatas'][0][i]
                })

        return formatted_results

    def query_hybrid(self, query_text: str, filters: Dict[str, Any] = None, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Hybrid query combining SQLite metadata filtering and ChromaDB semantic search.

        This is the recommended query method for the QueryMemoryTool.

        Args:
            query_text: Natural language query for semantic search
            filters: Structured metadata filters
            n_results: Number of results to return

        Returns:
            Ranked list of experiences combining both query types
        """
        # Step 1: Get candidates from metadata filtering
        metadata_results = self.query_metadata(filters or {}, limit=50)
        candidate_ids = {r['experience_id'] for r in metadata_results}

        # Step 2: Get semantic matches
        semantic_results = self.query_semantic(query_text, n_results=20)

        # Step 3: Combine and rank results
        # Priority: experiences that match both metadata AND semantics
        combined = {}

        for result in metadata_results:
            exp_id = result['experience_id']
            combined[exp_id] = {
                **result,
                'metadata_match': True,
                'semantic_match': False,
                'semantic_distance': 1.0,
                'combined_score': 0.5  # Base score for metadata match
            }

        for result in semantic_results:
            exp_id = result['experience_id']
            semantic_score = 1.0 - result['distance']  # Convert distance to similarity

            if exp_id in combined:
                # Both matches - boost score
                combined[exp_id]['semantic_match'] = True
                combined[exp_id]['semantic_distance'] = result['distance']
                combined[exp_id]['combined_score'] = 0.4 * 1.0 + 0.6 * semantic_score
            else:
                # Semantic match only
                combined[exp_id] = {
                    'experience_id': exp_id,
                    'metadata': result['metadata'],
                    'metadata_match': False,
                    'semantic_match': True,
                    'semantic_distance': result['distance'],
                    'combined_score': 0.6 * semantic_score
                }

        # Sort by combined score
        ranked_results = sorted(
            combined.values(),
            key=lambda x: x['combined_score'],
            reverse=True
        )[:n_results]

        return ranked_results

    def find_execution_trace(self, goal_signature: str, min_confidence: float = 0.9) -> Optional[Dict[str, Any]]:
        """
        Find a high-confidence execution trace for a given goal.

        Used by SystemAgent to decide between Learner vs Follower mode.

        Args:
            goal_signature: Description of the goal
            min_confidence: Minimum confidence threshold

        Returns:
            Trace metadata if found, None otherwise
        """
        cursor = self.db_conn.cursor()
        cursor.execute("""
            SELECT trace_id, goal_signature, confidence, estimated_cost,
                   estimated_time_secs, step_count, success_rate, file_path
            FROM execution_traces
            WHERE confidence >= ?
            ORDER BY success_rate DESC, confidence DESC
            LIMIT 1
        """, (min_confidence,))

        row = cursor.fetchone()
        if row:
            return {
                'trace_id': row[0],
                'goal_signature': row[1],
                'confidence': row[2],
                'estimated_cost': row[3],
                'estimated_time_secs': row[4],
                'step_count': row[5],
                'success_rate': row[6],
                'file_path': row[7]
            }

        return None

    def index_all(self):
        """Index all memory files in the system and projects directories."""
        print("Starting full memory indexing...")

        # Index system memory
        system_memory = SYSTEM_DIR / "memory_log.md"
        if system_memory.exists():
            self.index_memory_file(system_memory)

        # Index project memories
        if PROJECTS_DIR.exists():
            for project_dir in PROJECTS_DIR.iterdir():
                if not project_dir.is_dir():
                    continue

                project_name = project_dir.name

                # Index long-term memory
                memory_dir = project_dir / "memory" / "long_term"
                if memory_dir.exists():
                    for memory_file in memory_dir.glob("*.md"):
                        self.index_memory_file(memory_file, project_name)

                # Index execution traces
                trace_dir = project_dir / "memory" / "long_term"
                if trace_dir.exists():
                    for trace_file in trace_dir.glob("execution_trace_*.yaml"):
                        self.index_execution_trace(trace_file)

        print("Indexing complete!")

    def close(self):
        """Close database connections."""
        self.db_conn.close()


def main():
    """CLI entry point for memory indexer."""
    import argparse

    parser = argparse.ArgumentParser(description="LLMunix Memory Indexer")
    parser.add_argument('--index-all', action='store_true', help="Index all memory files")
    parser.add_argument('--file', type=str, help="Index a specific file")
    parser.add_argument('--query', type=str, help="Test semantic query")

    args = parser.parse_args()

    indexer = MemoryIndexer()

    try:
        if args.index_all:
            indexer.index_all()
        elif args.file:
            indexer.index_memory_file(Path(args.file))
        elif args.query:
            results = indexer.query_hybrid(args.query)
            print("\nQuery Results:")
            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result.get('experience_id')}")
                print(f"   Score: {result.get('combined_score', 0):.2f}")
                print(f"   Goal: {result.get('goal_description', 'N/A')}")
        else:
            print("Use --index-all to index all memory files")
            print("Use --file <path> to index a specific file")
            print("Use --query <text> to test semantic search")
    finally:
        indexer.close()


if __name__ == "__main__":
    main()
