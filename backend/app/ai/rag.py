# =============================================================================
# Digital Finance Tracker - RAG System
# PURPOSE: Retrieval-Augmented Generation for transaction categorization
# =============================================================================
"""
RAG (Retrieval-Augmented Generation) Module

This module provides RAG capabilities for improved transaction categorization:
1. RETRIEVE: Find similar past transactions for context
2. AUGMENT: Enrich prompts with historical patterns
3. GENERATE: More accurate, consistent predictions

Components:
    - SentenceTransformerEmbedder: Uses MiniLM for embeddings (reuses intent classifier model)
    - InMemoryVectorStore: Efficient cosine similarity search with numpy
    - RAGEngine: Main orchestrator for indexing and retrieval

How it works:
    1. When a transaction is created/updated, we index its merchant + category
    2. When categorizing a new transaction, we find similar past transactions
    3. Context from similar transactions augments the AI prompt
    4. Results in more consistent categorization for repeat merchants

Usage:
    from app.ai.rag import get_rag_engine

    engine = get_rag_engine()

    # Index a transaction after creation/categorization
    engine.index_transaction(user_id, tx_id, "Starbucks", "Food & Dining", 5.50)

    # Find similar transactions for a new merchant
    similar = engine.find_similar(user_id, "Starbucks Coffee #123")
    # Returns: [{"merchant": "Starbucks", "category": "Food & Dining", "similarity": 0.95}]

    # Augment a prompt with context
    augmented = engine.augment_prompt("Categorize: Starbucks Coffee", similar)
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID
import threading
from datetime import datetime, timezone

import numpy as np

from app.core.extensions import db

logger = logging.getLogger(__name__)


# =============================================================================
# CONFIGURATION
# =============================================================================

# Default number of similar transactions to retrieve
DEFAULT_TOP_K = 5

# Minimum similarity score to consider relevant (0-1 scale)
SIMILARITY_THRESHOLD = 0.70

# Maximum vectors per user (prevent memory bloat)
MAX_VECTORS_PER_USER = 1000

# Embedding dimension (MiniLM produces 384-dim vectors)
EMBEDDING_DIMENSION = 384


# =============================================================================
# EMBEDDER - Uses shared MiniLM model from utils.py
# =============================================================================


class SentenceTransformerEmbedder:
    """
    Text embedder using sentence-transformers MiniLM model.

    Reuses the shared model from app.ai.utils for efficiency.
    No additional model loading - shares with intent classifier.

    Attributes:
        dimension: Embedding vector dimension (384 for MiniLM)
    """

    def __init__(self):
        """Initialize the embedder."""
        self.dimension = EMBEDDING_DIMENSION
        self._model_loaded = False

    def embed(self, text: str) -> np.ndarray:
        """
        Convert text to embedding vector.

        Args:
            text: Input text (merchant name, description, etc.)

        Returns:
            Numpy array of shape (384,)

        Example:
            >>> embedder = SentenceTransformerEmbedder()
            >>> vec = embedder.embed("Starbucks Coffee")
            >>> vec.shape
            (384,)
        """
        try:
            from app.ai.utils import embed as utils_embed

            return utils_embed(text)
        except Exception as e:
            logger.error(f"Embedding failed for '{text}': {e}")
            # Return zeros on error (won't match anything)
            return np.zeros(self.dimension)

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Convert multiple texts to embeddings efficiently.

        Args:
            texts: List of texts to embed

        Returns:
            Numpy array of shape (n, 384)
        """
        if not texts:
            return np.array([])

        try:
            from app.ai.utils import embed_batch as utils_embed_batch

            return utils_embed_batch(texts)
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            return np.zeros((len(texts), self.dimension))


# =============================================================================
# VECTOR STORE - Efficient in-memory cosine similarity search
# =============================================================================


class InMemoryVectorStore:
    """
    In-memory vector store with cosine similarity search.

    Organizes vectors by user_id for efficient per-user retrieval.
    Uses numpy for fast similarity computation.

    Structure:
        _vectors = {
            "user_id_1": {
                "vec_id_1": {"embedding": np.array, "metadata": {...}},
                "vec_id_2": {...}
            }
        }

    Thread-safe operations using locks.
    """

    def __init__(self):
        """Initialize the vector store."""
        self._vectors: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._lock = threading.Lock()

    def add(
        self,
        user_id: str,
        vector_id: str,
        embedding: np.ndarray,
        metadata: Dict[str, Any],
    ) -> bool:
        """
        Add a vector to the store.

        Args:
            user_id: User who owns this vector
            vector_id: Unique ID for this vector (usually transaction_id)
            embedding: Numpy array of embedding values
            metadata: Additional data (merchant, category, amount, etc.)

        Returns:
            True if added successfully
        """
        with self._lock:
            if user_id not in self._vectors:
                self._vectors[user_id] = {}

            # Enforce per-user limit
            if len(self._vectors[user_id]) >= MAX_VECTORS_PER_USER:
                # Remove oldest entry
                oldest_key = next(iter(self._vectors[user_id]))
                del self._vectors[user_id][oldest_key]
                logger.debug(f"Evicted oldest vector for user {user_id}")

            self._vectors[user_id][vector_id] = {
                "embedding": embedding,
                "metadata": metadata,
                "indexed_at": datetime.now(timezone.utc).isoformat(),
            }
            return True

    def search(
        self,
        user_id: str,
        query_embedding: np.ndarray,
        top_k: int = DEFAULT_TOP_K,
        threshold: float = SIMILARITY_THRESHOLD,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors using cosine similarity.

        Args:
            user_id: User whose vectors to search
            query_embedding: Query vector
            top_k: Maximum number of results
            threshold: Minimum similarity score

        Returns:
            List of dicts with metadata and similarity scores, sorted by similarity
        """
        with self._lock:
            user_vectors = self._vectors.get(user_id, {})

            if not user_vectors:
                return []

            # Compute similarities for all user vectors
            results = []
            query_norm = np.linalg.norm(query_embedding)

            if query_norm == 0:
                return []

            for vec_id, vec_data in user_vectors.items():
                vec = vec_data["embedding"]
                vec_norm = np.linalg.norm(vec)

                if vec_norm == 0:
                    continue

                # Cosine similarity
                similarity = float(
                    np.dot(query_embedding, vec) / (query_norm * vec_norm)
                )

                if similarity >= threshold:
                    results.append(
                        {
                            "id": vec_id,
                            "similarity": round(similarity, 4),
                            **vec_data["metadata"],
                        }
                    )

            # Sort by similarity descending
            results.sort(key=lambda x: x["similarity"], reverse=True)

            return results[:top_k]

    def delete(self, user_id: str, vector_id: str) -> bool:
        """
        Delete a specific vector.

        Args:
            user_id: User who owns the vector
            vector_id: Vector ID to delete

        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if user_id in self._vectors and vector_id in self._vectors[user_id]:
                del self._vectors[user_id][vector_id]
                return True
            return False

    def delete_user_data(self, user_id: str) -> int:
        """
        Delete all vectors for a user (GDPR compliance).

        Args:
            user_id: User whose data to delete

        Returns:
            Number of vectors deleted
        """
        with self._lock:
            if user_id in self._vectors:
                count = len(self._vectors[user_id])
                del self._vectors[user_id]
                return count
            return 0

    def count(self, user_id: Optional[str] = None) -> int:
        """
        Get number of stored vectors.

        Args:
            user_id: Optional user to count for (None = all users)

        Returns:
            Number of vectors
        """
        with self._lock:
            if user_id:
                return len(self._vectors.get(user_id, {}))
            return sum(len(v) for v in self._vectors.values())

    def get_user_count(self) -> int:
        """Get number of users with indexed data."""
        with self._lock:
            return len(self._vectors)


# =============================================================================
# RAG ENGINE - Main orchestrator
# =============================================================================


class RAGEngine:
    """
    RAG Engine for transaction categorization.

    Provides:
    - index_transaction(): Index transactions for future retrieval
    - find_similar(): Find similar past transactions
    - augment_prompt(): Add context to categorization prompts
    - query_transactions(): Natural language transaction queries

    Thread-safe singleton pattern ensures single instance.

    Example:
        >>> engine = get_rag_engine()
        >>> engine.initialize()

        >>> # Index after transaction is categorized
        >>> engine.index_transaction(user_id, tx_id, "Starbucks", "Food & Dining", 5.50)

        >>> # Find similar when new transaction arrives
        >>> similar = engine.find_similar(user_id, "Starbucks Coffee #42")
        >>> [{"merchant": "Starbucks", "category": "Food & Dining", "similarity": 0.95}]
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the RAG engine."""
        if getattr(self, "_initialized", False):
            return

        self._embedder: Optional[SentenceTransformerEmbedder] = None
        self._vector_store: Optional[InMemoryVectorStore] = None
        self.is_initialized = False
        self.is_enabled = True  # RAG is now fully functional

        self._initialized = True

    def initialize(self) -> bool:
        """
        Initialize the RAG engine components.

        Returns:
            True if initialization successful
        """
        if self.is_initialized:
            return self.is_enabled

        try:
            self._embedder = SentenceTransformerEmbedder()
            self._vector_store = InMemoryVectorStore()

            self.is_initialized = True
            self.is_enabled = True

            logger.info("RAG Engine initialized successfully")
            return True

        except Exception as e:
            logger.error(f"RAG Engine initialization failed: {e}", exc_info=True)
            self.is_enabled = False
            return False

    def index_transaction(
        self,
        user_id: UUID,
        transaction_id: UUID,
        merchant_name: str,
        category_name: str,
        amount: float,
        description: Optional[str] = None,
    ) -> bool:
        """
        Index a transaction for future retrieval.

        Call this after a transaction is created or its category is updated.
        Creates embedding from merchant_name + description and stores with metadata.

        Args:
            user_id: Owner of the transaction
            transaction_id: Unique transaction ID
            merchant_name: Merchant name for embedding
            category_name: Assigned category
            amount: Transaction amount
            description: Optional additional text

        Returns:
            True if indexed successfully

        Example:
            >>> engine.index_transaction(
            ...     user_id, tx_id, "Starbucks Coffee", "Food & Dining", 5.50
            ... )
        """
        if not self.is_enabled or not self._embedder or not self._vector_store:
            return False

        if not merchant_name:
            return False

        try:
            # Create embedding text (merchant + optional description)
            embed_text = merchant_name
            if description:
                embed_text = f"{merchant_name} {description}"

            # Generate embedding
            embedding = self._embedder.embed(embed_text)

            # Store with metadata
            metadata = {
                "merchant_name": merchant_name,
                "category_name": category_name,
                "amount": amount,
                "description": description,
                "transaction_id": str(transaction_id),
            }

            success = self._vector_store.add(
                user_id=str(user_id),
                vector_id=str(transaction_id),
                embedding=embedding,
                metadata=metadata,
            )

            if success:
                logger.debug(
                    f"Indexed transaction {transaction_id}: "
                    f"{merchant_name} → {category_name}"
                )

            return success

        except Exception as e:
            logger.error(f"Failed to index transaction: {e}", exc_info=True)
            return False

    def find_similar(
        self,
        user_id: UUID,
        merchant_name: str,
        top_k: int = DEFAULT_TOP_K,
        threshold: float = SIMILARITY_THRESHOLD,
    ) -> List[Dict[str, Any]]:
        """
        Find similar past transactions.

        Use this when categorizing a new transaction to find patterns.

        Args:
            user_id: User whose transactions to search
            merchant_name: Merchant name to find similar for
            top_k: Maximum results to return
            threshold: Minimum similarity score (0-1)

        Returns:
            List of similar transactions with metadata and similarity scores

        Example:
            >>> similar = engine.find_similar(user_id, "STRBCKS Coffee #42")
            >>> similar
            [
                {
                    "merchant_name": "Starbucks Coffee",
                    "category_name": "Food & Dining",
                    "similarity": 0.92,
                    "amount": 5.50
                }
            ]
        """
        if not self.is_enabled or not self._embedder or not self._vector_store:
            return []

        if not merchant_name:
            return []

        try:
            # Generate query embedding
            query_embedding = self._embedder.embed(merchant_name)

            # Search vector store
            results = self._vector_store.search(
                user_id=str(user_id),
                query_embedding=query_embedding,
                top_k=top_k,
                threshold=threshold,
            )

            return results

        except Exception as e:
            logger.error(f"Failed to find similar transactions: {e}", exc_info=True)
            return []

    def get_category_suggestion(
        self,
        user_id: UUID,
        merchant_name: str,
    ) -> Optional[Tuple[str, float]]:
        """
        Get a category suggestion based on similar transactions.

        Convenience method that returns the most common category
        among similar transactions.

        Args:
            user_id: User ID
            merchant_name: Merchant to get suggestion for

        Returns:
            Tuple of (category_name, confidence) or None if no match

        Example:
            >>> suggestion = engine.get_category_suggestion(user_id, "AMZN Marketplace")
            >>> suggestion
            ("Shopping", 0.88)
        """
        similar = self.find_similar(user_id, merchant_name, top_k=3)

        if not similar:
            return None

        # Count category occurrences weighted by similarity
        category_scores: Dict[str, float] = {}
        for item in similar:
            cat = item.get("category_name", "Unknown")
            sim = item.get("similarity", 0)
            category_scores[cat] = category_scores.get(cat, 0) + sim

        if not category_scores:
            return None

        # Return highest scoring category
        best_category = max(category_scores, key=lambda k: category_scores[k])
        confidence = category_scores[best_category] / len(similar)

        return (best_category, round(confidence, 2))

    def augment_prompt(
        self,
        base_prompt: str,
        similar_transactions: List[Dict[str, Any]],
    ) -> str:
        """
        Augment a categorization prompt with similar transaction context.

        Adds historical context to help AI make consistent predictions.

        Args:
            base_prompt: Original categorization prompt
            similar_transactions: Results from find_similar()

        Returns:
            Augmented prompt with context

        Example:
            >>> augmented = engine.augment_prompt(
            ...     "Categorize: STRBCKS Coffee",
            ...     [{"merchant_name": "Starbucks", "category_name": "Food & Dining"}]
            ... )
            >>> # Returns prompt with "Previously, similar transactions were..."
        """
        if not similar_transactions:
            return base_prompt

        # Build context from similar transactions
        context_lines = ["Historical context from similar transactions:"]

        for i, tx in enumerate(similar_transactions[:3], 1):
            merchant = tx.get("merchant_name", "Unknown")
            category = tx.get("category_name", "Unknown")
            similarity = tx.get("similarity", 0)
            context_lines.append(
                f"  {i}. '{merchant}' was categorized as '{category}' "
                f"(similarity: {similarity:.0%})"
            )

        context = "\n".join(context_lines)

        return f"{context}\n\n{base_prompt}"

    def query_transactions(
        self,
        user_id: UUID,
        query: str,
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Query transactions using natural language.

        Enables questions like "Show me coffee purchases" or
        "Find transactions at restaurants".

        Args:
            user_id: User whose transactions to query
            query: Natural language query
            top_k: Maximum results

        Returns:
            List of matching transactions with metadata

        Example:
            >>> results = engine.query_transactions(user_id, "coffee shop purchases")
            >>> results
            [
                {"merchant_name": "Starbucks", "amount": 5.50, "similarity": 0.85},
                {"merchant_name": "Dunkin", "amount": 4.25, "similarity": 0.78}
            ]
        """
        # For natural language queries, use a lower threshold
        return self.find_similar(
            user_id=user_id,
            merchant_name=query,
            top_k=top_k,
            threshold=0.5,  # Lower threshold for NL queries
        )

    def delete_user_data(self, user_id: UUID) -> int:
        """
        Delete all indexed data for a user (GDPR compliance).

        Args:
            user_id: User whose data to delete

        Returns:
            Number of vectors deleted
        """
        if not self._vector_store:
            return 0

        count = self._vector_store.delete_user_data(str(user_id))
        logger.info(f"Deleted {count} RAG vectors for user {user_id}")
        return count

    def get_stats(self) -> Dict[str, Any]:
        """
        Get RAG engine statistics.

        Returns:
            Dictionary with status and counts
        """
        vector_count = self._vector_store.count() if self._vector_store else 0
        user_count = self._vector_store.get_user_count() if self._vector_store else 0

        return {
            "is_initialized": self.is_initialized,
            "is_enabled": self.is_enabled,
            "status": "active" if self.is_enabled else "disabled",
            "total_vectors": vector_count,
            "users_indexed": user_count,
            "embedding_dimension": EMBEDDING_DIMENSION,
            "similarity_threshold": SIMILARITY_THRESHOLD,
            "max_vectors_per_user": MAX_VECTORS_PER_USER,
        }

    def reindex_user_transactions(self, user_id: UUID, limit: int = 500) -> int:
        """
        Reindex a user's recent transactions from the database.

        Useful for initializing RAG for existing users or after clearing the index.

        Args:
            user_id: User whose transactions to reindex
            limit: Maximum transactions to index

        Returns:
            Number of transactions indexed
        """
        try:
            from app.models.transaction import Transaction
            from app.models.category import Category
            from app.models.enums import TransactionType
            from sqlalchemy import desc

            # Get recent expense transactions with categories
            transactions = (
                Transaction.query.filter(
                    Transaction.user_id == user_id,
                    Transaction.transaction_type == TransactionType.EXPENSE,
                    Transaction.merchant_name.isnot(None),
                    Transaction.category_id.isnot(None),
                )
                .order_by(desc(Transaction.created_at))
                .limit(limit)
                .all()
            )

            indexed = 0
            for tx in transactions:
                category = db.session.get(Category, tx.category_id)
                if category and tx.merchant_name:
                    success = self.index_transaction(
                        user_id=user_id,
                        transaction_id=tx.id,
                        merchant_name=tx.merchant_name,
                        category_name=category.name,
                        amount=float(tx.amount),
                    )
                    if success:
                        indexed += 1

            logger.info(f"Reindexed {indexed} transactions for user {user_id}")
            return indexed

        except Exception as e:
            logger.error(f"Reindex failed for user {user_id}: {e}", exc_info=True)
            return 0


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_rag_engine: Optional[RAGEngine] = None


def get_rag_engine() -> RAGEngine:
    """
    Get the singleton RAGEngine instance.

    Initializes the engine on first call.

    Returns:
        RAGEngine instance

    Example:
        >>> engine = get_rag_engine()
        >>> engine.find_similar(user_id, "Starbucks")
    """
    global _rag_engine

    if _rag_engine is None:
        _rag_engine = RAGEngine()
        _rag_engine.initialize()

    return _rag_engine


# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__ = [
    "RAGEngine",
    "get_rag_engine",
    "SentenceTransformerEmbedder",
    "InMemoryVectorStore",
    "DEFAULT_TOP_K",
    "SIMILARITY_THRESHOLD",
    "EMBEDDING_DIMENSION",
]
