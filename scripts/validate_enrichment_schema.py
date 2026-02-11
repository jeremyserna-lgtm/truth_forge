#!/usr/bin/env python3
"""Validate enrichment schema - columns owned by enrichers vs BQ table."""

import subprocess
import json

def get_bq_schema():
    """Get BQ entity_enrichments schema."""
    result = subprocess.run(
        ["bq", "show", "--schema", "--format=json", 
         "flash-clover-464719-g1:spine.entity_enrichments"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"BQ error: {result.stderr}")
        return []
    return [col["name"] for col in json.loads(result.stdout)]


# Columns owned by each enricher (from Python code COLUMNS_OWNED)
ENRICHER_COLUMNS = {
    "textblob": ["textblob_polarity", "textblob_subjectivity", "textblob_version"],
    "textstat": [
        "textstat_flesch_reading_ease", "textstat_flesch_kincaid_grade", "textstat_gunning_fog",
        "textstat_smog_index", "textstat_automated_readability_index", "textstat_coleman_liau_index",
        "textstat_linsear_write_formula", "textstat_dale_chall_readability_score",
        "textstat_difficult_words", "textstat_syllable_count", "textstat_lexicon_count",
        "textstat_sentence_count", "textstat_char_count", "textstat_version",
    ],
    "nrclx": ["nrclx_emotions", "nrclx_top_emotion", "nrclx_top_count"],
    "goemotions": [
        "goemotions_scores", "goemotions_top_emotions", "goemotions_primary_emotion",
        "goemotions_primary_score", "goemotions_model",
    ],
    "roberta_hate": ["roberta_hate_label", "roberta_hate_score", "roberta_hate_model"],
    "keybert": [
        "keybert_top_keyword", "keybert_top_score", "keybert_top_5_keywords",
        "keybert_all_keywords", "keybert_version",
    ],
    "bertopic": [
        "bertopic_topic_id", "bertopic_topic_probability", "bertopic_topic_words",
        "bertopic_model_id",
    ],
    "clustering": ["cluster_id", "cluster_label", "cluster_confidence"],
    "taxonomy": ["primary_category", "category_path", "content_type", "domain"],
    "resonance": ["resonance_group_id", "resonance_score"],
    "claims": ["qa_role", "is_claim", "claim_type"],
    "quality": ["enrichment_quality_flags"],
    "embedding": ["sentence_embedding", "sentence_embedding_model", "sentence_embedding_computed_at"],
}


def main():
    print("=" * 70)
    print("ENRICHMENT SCHEMA VALIDATION")
    print("=" * 70)
    
    bq_columns = set(get_bq_schema())
    print(f"\nBQ entity_enrichments has {len(bq_columns)} columns\n")
    
    all_enricher_cols = set()
    errors = []
    
    for enricher, cols in ENRICHER_COLUMNS.items():
        all_enricher_cols.update(cols)
        missing = [c for c in cols if c not in bq_columns]
        if missing:
            errors.append(f"{enricher}: {missing}")
            print(f"❌ {enricher}: MISSING FROM BQ:")
            for m in missing:
                print(f"     - {m}")
        else:
            print(f"✅ {enricher}: all {len(cols)} columns exist in BQ")
    
    # Check enriched_at columns (auto-added by base class)
    print("\n" + "-" * 70)
    print("ENRICHED_AT TIMESTAMPS (auto-added by base class):")
    for enricher in ENRICHER_COLUMNS:
        if enricher == "embedding":
            continue  # Uses sentence_embedding_computed_at
        col = f"{enricher}_enriched_at"
        if col in bq_columns:
            print(f"  ✅ {col}")
        else:
            errors.append(f"Missing timestamp: {col}")
            print(f"  ❌ {col} MISSING FROM BQ")
    
    # Check for BQ columns not owned by any enricher
    print("\n" + "-" * 70)
    print("BQ INFRASTRUCTURE COLUMNS (not owned by enrichers):")
    infra_cols = [c for c in sorted(bq_columns) 
                  if c not in all_enricher_cols and "_enriched_at" not in c]
    for c in infra_cols:
        print(f"  {c}")
    
    print("\n" + "=" * 70)
    print(f"SUMMARY: {len(bq_columns)} BQ columns, {len(all_enricher_cols)} enricher columns")
    
    if errors:
        print(f"\n🚨 {len(errors)} ERRORS FOUND")
        return 1
    else:
        print("\n✅ ALL ENRICHER COLUMNS MATCH BQ SCHEMA")
        return 0


if __name__ == "__main__":
    exit(main())
