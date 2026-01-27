"""Clustering enrichment - HDBSCAN clustering on embeddings.

THE PATTERN:
- HOLD₁: entity_unified entities with sentence_embedding
- AGENT: HDBSCAN clustering
- HOLD₂: cluster_id, cluster_label, cluster_confidence columns

Purpose: Group similar entities into clusters for cluster-level analysis.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

from pipelines.enrichment.base_enrichment import BaseEnrichment


logger = logging.getLogger(__name__)


class ClusteringEnrichment(BaseEnrichment):
    """HDBSCAN clustering enrichment."""

    ENRICHMENT_NAME = "clustering"
    COLUMNS_OWNED = [
        "cluster_id",
        "cluster_label",
        "cluster_confidence",
        "cluster_model",
        "cluster_version",
    ]
    REQUIRES_EMBEDDING = True

    def __init__(self) -> None:
        """Initialize clustering enrichment."""
        super().__init__()
        self.clusterer: Any = None
        self.cluster_labels_map: dict[int, str] = {}
        try:
            import hdbscan

            self.hdbscan = hdbscan
            # Will fit clusterer on sample data
            logger.info("HDBSCAN available for clustering")

        except ImportError:
            logger.error("hdbscan package not installed. Install with: pip install hdbscan")
            raise

    def compute_enrichment(
        self, text: str, existing_embedding: list[float] | None = None
    ) -> dict[str, Any]:
        """Compute cluster assignment for text.

        Args:
            text: Text content (not used if embedding provided)
            existing_embedding: Sentence embedding vector

        Returns:
            Dictionary with cluster_id, cluster_label, cluster_confidence
        """
        if not self.clusterer or existing_embedding is None:
            return {
                "cluster_id": None,
                "cluster_label": None,
                "cluster_confidence": None,
                "cluster_model": None,
                "cluster_version": None,
            }

        try:
            # Predict cluster for this embedding
            embedding_array = np.array(existing_embedding).reshape(1, -1)
            cluster_id, confidence = self.clusterer.approximate_predict(embedding_array)

            cluster_id = int(cluster_id[0])
            cluster_confidence = float(confidence[0])

            # Get cluster label if available
            cluster_label = self.cluster_labels_map.get(cluster_id, None)

            return {
                "cluster_id": cluster_id,
                "cluster_label": cluster_label,
                "cluster_confidence": round(cluster_confidence, 4),
                "cluster_model": "hdbscan",
                "cluster_version": "0.8.33",
            }

        except Exception as e:
            logger.warning(f"Clustering failed: {e}")
            return {
                "cluster_id": None,
                "cluster_label": None,
                "cluster_confidence": None,
                "cluster_model": "hdbscan",
                "cluster_version": "0.8.33",
            }

    def fit_clusterer(self, sample_size: int = 50000) -> None:
        """Fit HDBSCAN clusterer on sample embeddings.

        Args:
            sample_size: Number of entities to use for fitting
        """
        from pipelines.enrichment.config import BQ_DATASET_ID, BQ_PROJECT_ID, ENRICHMENTS_TABLE

        logger.info(f"Fitting HDBSCAN clusterer on {sample_size:,} entities...")

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
            logger.warning(f"Only {len(embeddings)} embeddings found, need at least 100")
            return

        logger.info(f"Fitting on {len(embeddings):,} embeddings...")

        # Fit HDBSCAN
        embeddings_array = np.array(embeddings)
        self.clusterer = self.hdbscan.HDBSCAN(
            min_cluster_size=10,
            min_samples=5,
            cluster_selection_epsilon=0.0,
        )
        cluster_labels = self.clusterer.fit_predict(embeddings_array)

        # Create cluster labels map (can derive from cluster keywords later)
        unique_clusters = set(cluster_labels)
        for cluster_id in unique_clusters:
            if cluster_id != -1:  # -1 is noise
                self.cluster_labels_map[int(cluster_id)] = f"cluster_{cluster_id}"

        logger.info(f"Clustering complete: {len(unique_clusters)} clusters (including noise: -1)")


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    enrichment = ClusteringEnrichment()
    if "--fit-clusterer" in sys.argv:
        sample_size = 50000
        if "--fit-sample-size" in sys.argv:
            idx = sys.argv.index("--fit-sample-size")
            if idx + 1 < len(sys.argv):
                sample_size = int(sys.argv[idx + 1])
        enrichment.fit_clusterer(sample_size)
    else:
        enrichment.run()
