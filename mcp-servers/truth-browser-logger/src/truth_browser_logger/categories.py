"""Domain Category Mapping.

Maps domains to skill/activity categories for richer signal interpretation.
Categories help understand what the user was researching or doing.
"""
from __future__ import annotations

from typing import Dict, Optional

# Domain to category mapping (~50 domains)
DOMAIN_CATEGORIES: Dict[str, str] = {
    # Coding / Development
    "github.com": "coding",
    "gitlab.com": "coding",
    "bitbucket.org": "coding",
    "stackoverflow.com": "coding",
    "stackexchange.com": "coding",
    "codepen.io": "coding",
    "codesandbox.io": "coding",
    "replit.com": "coding",
    "jsfiddle.net": "coding",
    "npmjs.com": "coding",
    "pypi.org": "coding",
    "crates.io": "coding",
    
    # Research / Academic
    "arxiv.org": "research",
    "scholar.google.com": "research",
    "researchgate.net": "research",
    "semanticscholar.org": "research",
    "pubmed.gov": "research",
    "ncbi.nlm.nih.gov": "research",
    "jstor.org": "research",
    "sciencedirect.com": "research",
    "nature.com": "research",
    "ieee.org": "research",
    "acm.org": "research",
    
    # Documentation
    "docs.python.org": "documentation",
    "developer.mozilla.org": "documentation",
    "devdocs.io": "documentation",
    "readthedocs.io": "documentation",
    "docs.rs": "documentation",
    "typescriptlang.org": "documentation",
    "reactjs.org": "documentation",
    "vuejs.org": "documentation",
    "angular.io": "documentation",
    "nodejs.org": "documentation",
    
    # AI / Machine Learning
    "huggingface.co": "ai_ml",
    "openai.com": "ai_ml",
    "anthropic.com": "ai_ml",
    "kaggle.com": "ai_ml",
    "replicate.com": "ai_ml",
    "wandb.ai": "ai_ml",
    "tensorflow.org": "ai_ml",
    "pytorch.org": "ai_ml",
    "colab.research.google.com": "ai_ml",
    
    # Business / Professional
    "linkedin.com": "business",
    "crunchbase.com": "business",
    "producthunt.com": "business",
    "angel.co": "business",
    "ycombinator.com": "business",
    "techcrunch.com": "business",
    "bloomberg.com": "business",
    "forbes.com": "business",
    
    # Communication / Collaboration
    "mail.google.com": "communication",
    "outlook.live.com": "communication",
    "slack.com": "communication",
    "discord.com": "communication",
    "notion.so": "collaboration",
    "figma.com": "collaboration",
    "miro.com": "collaboration",
    "trello.com": "collaboration",
    "asana.com": "collaboration",
    "linear.app": "collaboration",
    
    # Learning / Education
    "coursera.org": "learning",
    "udemy.com": "learning",
    "edx.org": "learning",
    "khanacademy.org": "learning",
    "pluralsight.com": "learning",
    "youtube.com": "learning",
    "medium.com": "learning",
    "dev.to": "learning",
    "hashnode.com": "learning",
    
    # Finance / Trading
    "finance.yahoo.com": "finance",
    "tradingview.com": "finance",
    "coinmarketcap.com": "finance",
    "coingecko.com": "finance",
    
    # News / Information
    "news.ycombinator.com": "news",
    "reddit.com": "news",
    "twitter.com": "social",
    "x.com": "social",
    
    # Cloud / Infrastructure
    "cloud.google.com": "cloud",
    "aws.amazon.com": "cloud",
    "portal.azure.com": "cloud",
    "vercel.com": "cloud",
    "netlify.com": "cloud",
    "heroku.com": "cloud",
    "digitalocean.com": "cloud",
}


def get_category_for_domain(domain: str) -> Optional[str]:
    """Get category for a domain.
    
    Checks exact match first, then tries parent domains.
    
    Args:
        domain: The domain to categorize (e.g., "github.com")
    
    Returns:
        Category string or None if not categorized
    """
    if not domain:
        return None
    
    domain = domain.lower().strip()
    
    # Check exact match
    if domain in DOMAIN_CATEGORIES:
        return DOMAIN_CATEGORIES[domain]
    
    # Check parent domains (e.g., "docs.github.com" -> "github.com")
    parts = domain.split(".")
    for i in range(1, len(parts)):
        parent = ".".join(parts[i:])
        if parent in DOMAIN_CATEGORIES:
            return DOMAIN_CATEGORIES[parent]
    
    return None


def get_all_categories() -> set:
    """Get set of all category names."""
    return set(DOMAIN_CATEGORIES.values())


def get_domains_for_category(category: str) -> list:
    """Get all domains mapped to a category."""
    return [d for d, c in DOMAIN_CATEGORIES.items() if c == category]
