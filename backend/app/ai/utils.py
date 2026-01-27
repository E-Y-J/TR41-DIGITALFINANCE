# =============================================================================
# Digital Finance Tracker - AI Utilities
# PURPOSE: Centralized embedding and similarity functions for AI modules
# =============================================================================
"""
AI Utilities Module

This module centralizes embedding and similarity utilities:
- embed(): Get embedding for a single text
- embed_batch(): Get embeddings for multiple texts
- cos_sim(): Compute cosine similarity using sentence_transformers

Uses sentence_transformers' built-in util.cos_sim() for efficiency.

Usage:
    from app.ai.utils import embed, embed_batch, cos_sim, get_embedding_model

    # Get embeddings
    embedding = embed("Add $50 for lunch")
    embeddings = embed_batch(["text1", "text2", "text3"])

    # Compute similarity
    similarity = cos_sim(embedding1, embedding2)

Notes:
    - Model is loaded lazily on first use
    - Uses MiniLM for fast, accurate embeddings
    - Thread-safe singleton pattern
"""

import logging
from typing import List, Optional, Union
import threading

import numpy as np

logger = logging.getLogger(__name__)


# =============================================================================
# GLOBALS
# =============================================================================

_model = None
_model_lock = threading.Lock()
_model_name = "sentence-transformers/multi-qa-MiniLM-L6-cos-v1"


# =============================================================================
# MODEL LOADING
# =============================================================================


def get_embedding_model():
    """
    Get the sentence transformer model (lazy loading).

    Returns:
        SentenceTransformer model instance

    Raises:
        ImportError: If sentence_transformers not installed
    """
    global _model

    if _model is not None:
        return _model

    with _model_lock:
        if _model is not None:
            return _model

        try:
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading embedding model: {_model_name}")
            _model = SentenceTransformer(_model_name)
            logger.info("Embedding model loaded successfully")
            return _model

        except ImportError as e:
            logger.error(
                "sentence_transformers not installed. "
                "Run: pip install sentence-transformers"
            )
            raise ImportError(
                "sentence_transformers required for embeddings"
            ) from e

        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}", exc_info=True)
            raise


# =============================================================================
# EMBEDDING FUNCTIONS
# =============================================================================


def embed(text: str) -> np.ndarray:
    """
    Get embedding vector for a single text.

    Args:
        text: Input text to embed

    Returns:
        Numpy array of embedding values

    Example:
        >>> embedding = embed("Add $50 for lunch at Subway")
        >>> embedding.shape
        (384,)
    """
    model = get_embedding_model()
    return model.encode(text, convert_to_numpy=True)


def embed_batch(texts: List[str], batch_size: int = 32) -> np.ndarray:
    """
    Get embeddings for multiple texts efficiently.

    Args:
        texts: List of texts to embed
        batch_size: Batch size for encoding

    Returns:
        Numpy array of shape (n_texts, embedding_dim)

    Example:
        >>> embeddings = embed_batch(["text1", "text2", "text3"])
        >>> embeddings.shape
        (3, 384)
    """
    if not texts:
        return np.array([])

    model = get_embedding_model()
    return model.encode(texts, batch_size=batch_size, convert_to_numpy=True)


# =============================================================================
# SIMILARITY FUNCTIONS
# =============================================================================


def cos_sim(
    a: Union[np.ndarray, "np.ndarray"],
    b: Union[np.ndarray, "np.ndarray"],
) -> float:
    """
    Compute cosine similarity between two embeddings.

    Uses sentence_transformers.util.cos_sim for efficiency.

    Args:
        a: First embedding vector or batch
        b: Second embedding vector or batch

    Returns:
        Cosine similarity score(s)

    Example:
        >>> emb1 = embed("add expense")
        >>> emb2 = embed("log purchase")
        >>> similarity = cos_sim(emb1, emb2)
        >>> print(f"Similarity: {similarity:.2f}")
        Similarity: 0.85
    """
    try:
        from sentence_transformers import util

        # Use sentence_transformers built-in cos_sim
        similarity = util.cos_sim(a, b)

        # Handle different return shapes
        if hasattr(similarity, "item"):
            return float(similarity.item())
        elif hasattr(similarity, "numpy"):
            arr = similarity.numpy()
            if arr.ndim == 0:
                return float(arr)
            return float(arr[0][0]) if arr.ndim == 2 else float(arr[0])
        else:
            return float(similarity)

    except ImportError:
        # Fallback to numpy implementation
        logger.warning("Using numpy fallback for cos_sim")
        return _numpy_cos_sim(a, b)


def _numpy_cos_sim(a: np.ndarray, b: np.ndarray) -> float:
    """
    Numpy fallback for cosine similarity.

    Args:
        a: First embedding vector
        b: Second embedding vector

    Returns:
        Cosine similarity score
    """
    a = np.asarray(a).flatten()
    b = np.asarray(b).flatten()

    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot / (norm_a * norm_b))


def batch_cos_sim(
    query: np.ndarray,
    corpus: np.ndarray,
) -> np.ndarray:
    """
    Compute cosine similarity between query and all corpus embeddings.

    Args:
        query: Single query embedding (1D array)
        corpus: Matrix of corpus embeddings (2D array)

    Returns:
        Array of similarity scores

    Example:
        >>> query = embed("add expense")
        >>> corpus = embed_batch(["log purchase", "delete item", "hello"])
        >>> scores = batch_cos_sim(query, corpus)
        >>> best_idx = np.argmax(scores)
    """
    try:
        from sentence_transformers import util

        similarities = util.cos_sim(query, corpus)
        return similarities.numpy().flatten()

    except ImportError:
        # Fallback to numpy
        query = np.asarray(query).reshape(1, -1)
        corpus = np.asarray(corpus)

        # Normalize
        query_norm = query / np.linalg.norm(query, axis=1, keepdims=True)
        corpus_norm = corpus / np.linalg.norm(corpus, axis=1, keepdims=True)

        # Dot product
        return np.dot(query_norm, corpus_norm.T).flatten()


# =============================================================================
# TEXT PREPROCESSING
# =============================================================================


def preprocess_text(text: str) -> str:
    """
    Basic text preprocessing for embeddings.

    Args:
        text: Raw input text

    Returns:
        Cleaned text
    """
    import re

    # Lowercase
    text = text.lower().strip()

    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove special characters but keep $ and numbers
    text = re.sub(r"[^\w\s$.,!?-]", "", text)

    return text


def extract_key_terms(text: str) -> List[str]:
    """
    Extract key financial terms from text.

    Useful for keyword matching before AI inference.

    Args:
        text: Input text

    Returns:
        List of key terms found
    """
    import re

    text_lower = text.lower()

    # Financial keywords to look for
    financial_terms = [
        r"\$[\d,]+(?:\.\d{2})?",  # Dollar amounts
        r"(?:add|spent|paid|bought|purchased|received)",  # Action verbs
        r"(?:expense|income|transaction|payment|deposit)",  # Nouns
        r"(?:food|shopping|transport|bills|entertainment)",  # Categories
    ]

    found_terms = []
    for pattern in financial_terms:
        matches = re.findall(pattern, text_lower)
        found_terms.extend(matches)

    return found_terms


def truncate_for_embedding(text: str, max_tokens: int = 256) -> str:
    """
    Truncate text to approximate token limit.

    MiniLM has a 256 token limit. This does rough approximation.

    Args:
        text: Input text
        max_tokens: Maximum tokens (approx 4 chars per token)

    Returns:
        Truncated text
    """
    # Rough estimate: 4 characters per token
    max_chars = max_tokens * 4

    if len(text) <= max_chars:
        return text

    # Truncate and add ellipsis
    return text[: max_chars - 3] + "..."
