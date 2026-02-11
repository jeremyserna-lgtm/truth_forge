#!/usr/bin/env node
/**
 * Test script to debug multiple file upload behavior
 * This simulates what handleUpload does in App.tsx
 */

import { readFile, readdir } from 'fs/promises';
import { join } from 'path';

// Simulate the estimateTokens function
function estimateTokens(text) {
  return Math.ceil(text.length / 4);
}

// Simulate handleUpload logic from App.tsx
async function simulateHandleUpload(filePaths, tokenLimit = 1000000) {
  console.log(`\n📤 [simulateHandleUpload] Received ${filePaths.length} files`);

  const newDocs = [];
  let tempUsedTokens = 0;
  let acceptedCount = 0;
  let rejectedCount = 0;

  // Process all files in parallel (like Promise.all in App.tsx)
  const filePromises = filePaths.map(async (filePath, i) => {
    console.log(`  [Processing] File ${i + 1}/${filePaths.length}: ${filePath}`);

    try {
      const content = await readFile(filePath, 'utf-8');
      const name = filePath.split('/').pop();
      console.log(`    ✓ Read: ${name} (${content.length} chars)`);
      return { error: false, contents: [{ name, content }] };
    } catch (e) {
      console.log(`    ✗ Error reading: ${e.message}`);
      return { error: true, name: filePath };
    }
  });

  const results = await Promise.all(filePromises);
  console.log(`\n📊 [Results] Processed ${results.length} files`);

  for (const result of results) {
    if (result.error) {
      console.log(`  ⚠ Skipping errored file: ${result.name}`);
      continue;
    }

    for (const item of result.contents || []) {
      const docTokens = estimateTokens(item.content);
      console.log(`  → Checking: ${item.name} (${docTokens} tokens)`);

      if (tempUsedTokens + docTokens <= tokenLimit) {
        newDocs.push({
          id: `${item.name}-${Date.now()}-${Math.random()}`,
          name: item.name,
          content: item.content,
          size: item.content.length
        });
        tempUsedTokens += docTokens;
        acceptedCount++;
        console.log(`    ✅ Accepted (total tokens: ${tempUsedTokens})`);
      } else {
        rejectedCount++;
        console.log(`    ❌ Rejected (would exceed ${tokenLimit} token limit)`);
      }
    }
  }

  console.log(`\n📋 [Final Summary]`);
  console.log(`   Documents to add: ${newDocs.length}`);
  console.log(`   Accepted: ${acceptedCount}`);
  console.log(`   Rejected: ${rejectedCount}`);
  console.log(`   Total tokens: ${tempUsedTokens}`);

  return newDocs;
}

// Test with sample files
async function runTest() {
  console.log('🧪 Testing Multiple File Upload Logic\n');
  console.log('═'.repeat(60));

  // Create test files
  const testDir = '/tmp/upload-test';
  const { mkdir, writeFile } = await import('fs/promises');

  try {
    await mkdir(testDir, { recursive: true });

    // Create 3 test files
    await writeFile(join(testDir, 'doc1.txt'), 'This is document one with some content.');
    await writeFile(join(testDir, 'doc2.txt'), 'This is document two with different content.');
    await writeFile(join(testDir, 'doc3.md'), '# Document Three\n\nThis is a markdown file.');

    console.log('Created 3 test files in', testDir);

    const files = await readdir(testDir);
    const filePaths = files.map(f => join(testDir, f));

    console.log('Files to upload:', filePaths);

    // Run simulation
    const docs = await simulateHandleUpload(filePaths);

    console.log('\n═'.repeat(60));
    console.log('📦 Final Documents Array:');
    docs.forEach((d, i) => {
      console.log(`  ${i + 1}. ${d.name} (${d.size} bytes)`);
    });

    if (docs.length === filePaths.length) {
      console.log('\n✅ SUCCESS: All files were processed correctly!');
    } else {
      console.log(`\n⚠ WARNING: Expected ${filePaths.length} docs but got ${docs.length}`);
    }

  } catch (e) {
    console.error('Test failed:', e);
  }
}

runTest();
