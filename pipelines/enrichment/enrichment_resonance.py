"""Resonance detection enrichment - Find repeating patterns/concepts.

THE PATTERN:
- HOLD₁: entity_unified entities with sentence_embedding
- AGENT: Resonance detection (embedding similarity grouping)
- HOLD₂: resonance_group_id, resonance_score columns

Purpose: Detect repeating patterns/concepts across entities for resonance analysis.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

from pipelines.enrichment.base_enrichment import BaseEnrichment


logger = logging.getLogger(__name__)


class ResonanceEnrichment(BaseEnrichment):
    """Resonance detection enrichment."""

    ENRICHMENT_NAME = "resonance"
    COLUMNS_OWNED = [
        "resonance_group_id",
        "resonance_score",
        "resonance_version",
    ]
    REQUIRES_EMBEDDING = True

    def __init__(self) -> None:
        """Initialize resonance enrichment."""
        super().__init__()
        # Resonance groups will be computed from existing embeddings
        self.resonance_groups: dict[str, list[float]] = {}
        self.similarity_threshold = 0.85  # Cosine similarity threshold

    def compute_enrichment(
        self, text: str, existing_embedding: list[float] | None = None
    ) -> dict[str, Any]:
        """Compute resonance group assignment for text.

        Args:
            text: Text content (not used if embedding provided)
            existing_embedding: Sentence embedding vector

        Returns:
            Dictionary with resonance_group_id, resonance_score
        """
        if existing_embedding is None or not self.resonance_groups:
            return {
                "resonance_group_id": None,
                "resonance_score": None,
                "resonance_version": "1.0.0",
            }

        try:
            # Find closest resonance group
            embedding_array = np.array(existing_embedding)

            best_group = None
            best_score = 0.0

            for group_id, centroid in self.resonance_groups.items():
                centroid_array = np.array(centroid)
                # Cosine similarity
                similarity = np.dot(embedding_array, centroid_array) / (
                    np.linalg.norm(embedding_array) * np.linalg.norm(centroid_array)
                )

                if similarity > best_score and similarity >= self.similarity_threshold:
                    best_score = similarity
                    best_group = group_id

            return {
                "resonance_group_id": best_group,
                "resonance_score": round(float(best_score), 4) if best_group else None,
                "resonance_version": "1.0.0",
            }

        except Exception as e:
            logger.warning(f"Resonance detection failed: {e}")
            return {
                "resonance_group_id": None,
                "resonance_score": None,
                "resonance_version": "1.0.0",
            }

    def build_resonance_groups(self, sample_size: int = 100000) -> None:
        """Build resonance groups from existing embeddings.

        Args:
            sample_size: Number of entities to analyze for resonance groups
        """
        from pipelines.enrichment.config import BQ_DATASET_ID, BQ_PROJECT_ID, ENRICHMENTS_TABLE

        logger.info(f"Building resonance groups from {sample_size:,} entities...")

        # Get sample embeddings
        query = f"""
        SELECT entity_id, sentence_embedding
        FROM `{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{ENRICHMENTS_TABLE}`
        WHERE sentence_embedding IS NOT NULL
        ORDER BY RAND()
        LIMIT {sample_size}
        """

        query_job = self.client.query(query)
        results = list(query_job.result())

        embeddings = []
        entity_ids = []
        for row in results:
            if hasattr(row, "sentence_embedding") and row.sentence_embedding:
                embeddings.append(row.sentence_embedding)
                entity_ids.append(row.entity_id)

        if len(embeddings) < 100:
            logger.warning(f"Only {len(embeddings)} embeddings found")
            return

        logger.info(f"Analyzing {len(embeddings):,} embeddings for resonance...")

        # Use clustering to find resonance groups
        try:
            from sklearn.cluster import DBSCAN
            from sklearn.metrics.pairwise import cosine_similarity

            embeddings_array = np.array(embeddings)

            # Use DBSCAN with cosine similarity
            # eps = similarity threshold, min_samples = minimum entities per group
            clustering = DBSCAN(
                eps=1 - self.similarity_threshold,  # Convert similarity to distance
                min_samples=5,
                metric="cosine",
            )
            cluster_labels = clustering.fit_predict(embeddings_array)

            # Create resonance groups
            unique_clusters = set(cluster_labels)
            for cluster_id in unique_clusters:
                if cluster_id != -1:  # -1 is noise
                    cluster_mask = cluster_labels == cluster_id
                    cluster_embeddings = embeddings_array[cluster_mask]

                    # Compute centroid
                    centroid = np.mean(cluster_embeddings, axis=0)
                    group_id = f"resonance_{cluster_id}"

                    self.resonance_groups[group_id] = centroid.tolist()

            logger.info(
                f"Resonance groups built: {len(self.resonance_groups)} groups (excluding noise)"
            )

        except ImportError:
            logger.warning("sklearn not installed - using simple similarity search")
            # Fallback: use simple nearest neighbor
            self._build_groups_simple(embeddings, entity_ids)

    def _build_groups_simple(self, embeddings: list[list[float]], entity_ids: list[str]) -> None:
        """Simple resonance group building (fallback)."""
        embeddings_array = np.array(embeddings)
        groups: dict[str, Any] = {}
        group_counter = 0

        for i, embedding in enumerate(embeddings_array):
            # Find existing group with high similarity
            assigned = False
            for group_id, centroid in groups.items():
                similarity = np.dot(embedding, np.array(centroid)) / (
                    np.linalg.norm(embedding) * np.linalg.norm(np.array(centroid))
                )
                if similarity >= self.similarity_threshold:
                    # Update centroid with new member
                    groups[group_id] = (
                        (np.array(centroid) * len(groups[group_id]) + embedding)
                        / (len(groups[group_id]) + 1)
                    ).tolist()
                    assigned = True
                    break

            if not assigned:
                # Create new group
                group_id = f"resonance_{group_counter}"
                groups[group_id] = embedding.tolist()
                group_counter += 1

        self.resonance_groups = groups
        logger.info(f"Built {len(self.resonance_groups)} resonance groups (simple method)")


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    enrichment = ResonanceEnrichment()
    if "--build-groups" in sys.argv:
        sample_size = 100000
        if "--sample-size" in sys.argv:
            idx = sys.argv.index("--sample-size")
            if idx + 1 < len(sys.argv):
                sample_size = int(sys.argv[idx + 1])
        enrichment.build_resonance_groups(sample_size)
    else:
        enrichment.run()
