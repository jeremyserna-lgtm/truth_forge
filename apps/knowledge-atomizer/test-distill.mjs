#!/usr/bin/env node
/**
 * End-to-end test for the Knowledge Atomizer distillToAtoms function
 * Fetches API key from GCP Secret Manager
 * Run with: node test-distill.mjs
 */

import { GoogleGenerativeAI } from '@google/generative-ai';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

async function getApiKeyFromSecretManager() {
  console.log('🔐 Fetching API key from GCP Secret Manager...');
  try {
    const { stdout } = await execAsync(
      'gcloud secrets versions access latest --secret="Google_API_Key" --project="flash-clover-464719-g1"'
    );
    const key = stdout.trim();
    if (!key || !key.startsWith('AIza')) {
      throw new Error('Invalid API key format');
    }
    console.log('✅ API key retrieved successfully');
    return key;
  } catch (error) {
    console.error('❌ Failed to get API key from Secret Manager:', error.message);
    // Fallback to environment variable
    const envKey = process.env.API_KEY || process.env.GEMINI_API_KEY;
    if (envKey) {
      console.log('💡 Using fallback from environment variable');
      return envKey;
    }
    throw new Error('No API key available');
  }
}

const TEST_CONTENT = `
The furnace doesn't strain. If forcing, find the shape that burns.
Stage 5 is recursive self-seeing as normal, not remarkable.
HOLD → AGENT → HOLD is the universal pattern.
`;

// Full 12-dimensional schema for testing
const FULL_ATOM_SCHEMA = {
  type: "array",
  items: {
    type: "object",
    properties: {
      content: { type: "string" },
      theme: { type: "string" },
      domain: { type: "string" },
      significance: { type: "string", enum: ["Fundamental", "Insight", "Prediction", "Nuance"] },
      certainty: { type: "string", enum: ["fact", "consensus", "claim", "speculation", "hypothesis"] },
      tags: { type: "array", items: { type: "string" } },
      novelty: { type: "number" },
      actionability: { type: "number" },
      sentiment: { type: "number" },
      entities: { type: "array", items: { type: "string" } },
      concepts: { type: "array", items: { type: "string" } },
      abstraction_level: { type: "string", enum: ["concrete", "conceptual", "abstract", "meta"] },
      evidence_strength: { type: "number" },
      verifiability: { type: "string", enum: ["observable", "testable", "logical", "intuitive"] },
      temporal_scope: { type: "string", enum: ["universal", "historical", "current", "emerging", "future"] },
      durability: { type: "string", enum: ["permanent", "durable", "transient", "ephemeral"] },
      dependencies: { type: "array", items: { type: "string" } },
      implications: { type: "array", items: { type: "string" } },
      supports: { type: "array", items: { type: "string" } },
      contradicts: { type: "array", items: { type: "string" } },
      tensions: { type: "array", items: { type: "string" } },
      synthesis_potential: { type: "string" },
      intensity: { type: "number" },
      stakes: { type: "string", enum: ["existential", "high", "medium", "low", "trivial"] },
      urgency: { type: "number" },
      action_items: { type: "array", items: { type: "string" } },
      preconditions: { type: "array", items: { type: "string" } },
      consequences: { type: "array", items: { type: "string" } },
      audience: { type: "array", items: { type: "string" } },
      structure_type: { type: "string", enum: ["claim", "definition", "comparison", "causation", "sequence", "classification"] },
      complexity: { type: "string", enum: ["atomic", "compound", "nested"] },
      completeness: { type: "number" },
      entity_type: { type: "string", enum: ["thing", "process", "relation", "property", "state"] },
      categories: { type: "array", items: { type: "string" } },
      is_a: { type: "array", items: { type: "string" } },
      has_parts: { type: "array", items: { type: "string" } },
      normative_type: { type: "string", enum: ["descriptive", "prescriptive", "evaluative"] },
      values_invoked: { type: "array", items: { type: "string" } },
      should_statements: { type: "array", items: { type: "string" } },
    },
    required: [
      // ALL fields are required - no optional dimensions
      "content", "theme", "domain", "tags",
      "abstraction_level",
      "significance", "novelty", "actionability",
      "certainty", "evidence_strength", "verifiability",
      "temporal_scope", "durability",
      "entities", "concepts", "dependencies", "implications",
      "supports", "contradicts", "tensions", "synthesis_potential",
      "sentiment", "intensity", "stakes", "urgency",
      "action_items", "preconditions", "consequences", "audience",
      "structure_type", "complexity", "completeness",
      "entity_type", "categories", "is_a", "has_parts",
      "normative_type", "values_invoked", "should_statements"
    ]
  }
};

async function testDistillToAtoms() {
  console.log('🧪 Testing distillToAtoms with 12-dimensional schema...\n');

  const API_KEY = await getApiKeyFromSecretManager();
  const genAI = new GoogleGenerativeAI(API_KEY);

  const model = genAI.getGenerativeModel({
    model: "gemini-2.0-flash",
    generationConfig: {
      responseMimeType: "application/json",
      responseSchema: FULL_ATOM_SCHEMA
    }
  });

  const prompt = `
    You are a Knowledge Extraction Engine performing FULL 12-DIMENSIONAL ANALYSIS.

    Analyze the following text and distill core truths into Knowledge Atoms.
    Each atom is a single, standalone sentence that captures one truth.

    For EACH atom, provide ALL dimensions:
    - content: The atomic truth statement
    - theme: 1-2 word category
    - domain: Knowledge domain (tech, philosophy, business, etc.)
    - significance: Fundamental, Insight, Prediction, or Nuance
    - certainty: fact, consensus, claim, speculation, or hypothesis
    - tags: 2-5 keywords
    - novelty: 0-1 how unique
    - actionability: 0-1 can you act on this
    - sentiment: -1 to 1 tone
    - entities: Named entities referenced
    - concepts: Abstract concepts referenced
    - abstraction_level: concrete, conceptual, abstract, or meta
    - evidence_strength: 0-1 how well supported
    - verifiability: observable, testable, logical, or intuitive
    - temporal_scope: universal, historical, current, emerging, or future
    - durability: permanent, durable, transient, or ephemeral
    - dependencies: What this depends on
    - implications: What follows from this
    - supports: Positions this supports
    - contradicts: Positions this contradicts
    - tensions: Internal paradoxes
    - synthesis_potential: How to resolve tensions
    - intensity: 0-1 emotional intensity
    - stakes: existential, high, medium, low, or trivial
    - urgency: 0-1 time pressure
    - action_items: Implied actions
    - preconditions: What must be true first
    - consequences: What happens if acted upon
    - audience: Who needs to know
    - structure_type: claim, definition, comparison, causation, sequence, classification
    - complexity: atomic, compound, nested
    - completeness: 0-1 is this self-contained
    - entity_type: thing, process, relation, property, state
    - categories: Classification categories
    - is_a: Parent types
    - has_parts: Component parts
    - normative_type: descriptive, prescriptive, evaluative
    - values_invoked: Values appealed to
    - should_statements: Implied oughts

    Text to analyze:
    ${TEST_CONTENT}
  `;

  try {
    console.log('📤 Sending request to Gemini...');
    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();

    console.log('📥 Raw response received\n');

    const atoms = JSON.parse(text);

    console.log(`✅ SUCCESS: Extracted ${atoms.length} atoms\n`);
    console.log('─'.repeat(60));

    for (let i = 0; i < atoms.length; i++) {
      const atom = atoms[i];
      console.log(`\n🔬 ATOM ${i + 1}:`);
      console.log(`   Content: ${atom.content}`);
      console.log(`   Theme: ${atom.theme}`);
      console.log(`   Domain: ${atom.domain}`);
      console.log(`   Significance: ${atom.significance}`);
      console.log(`   Certainty: ${atom.certainty}`);
      console.log(`   Abstraction: ${atom.abstraction_level}`);
      console.log(`   Tags: ${atom.tags?.join(', ')}`);
      console.log(`   Novelty: ${atom.novelty}`);
      console.log(`   Actionability: ${atom.actionability}`);
      console.log(`   Sentiment: ${atom.sentiment}`);
      console.log(`   Stakes: ${atom.stakes}`);
      console.log(`   Temporal: ${atom.temporal_scope}`);
      console.log(`   Entities: ${atom.entities?.join(', ') || 'none'}`);
      console.log(`   Concepts: ${atom.concepts?.join(', ') || 'none'}`);

      // Count filled dimensions
      const dimensionFields = [
        'domain', 'certainty', 'abstraction_level', 'evidence_strength', 'verifiability',
        'temporal_scope', 'durability', 'sentiment', 'intensity', 'stakes', 'urgency',
        'structure_type', 'complexity', 'completeness', 'entity_type', 'normative_type'
      ];
      const filled = dimensionFields.filter(f => atom[f] !== undefined && atom[f] !== null).length;
      const coverage = Math.round((filled / dimensionFields.length) * 100);
      console.log(`   📊 Enrichment Coverage: ${coverage}%`);
    }

    console.log('\n' + '─'.repeat(60));
    console.log('✅ TEST PASSED: 12-dimensional extraction working correctly');
    console.log('─'.repeat(60));

    return true;

  } catch (error) {
    console.error('❌ TEST FAILED:', error.message);
    if (error.response) {
      console.error('Response:', error.response);
    }
    return false;
  }
}

testDistillToAtoms().then(success => {
  process.exit(success ? 0 : 1);
});
