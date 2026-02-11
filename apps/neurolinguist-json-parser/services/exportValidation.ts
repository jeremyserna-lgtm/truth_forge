/**
 * Export Validation Service
 * Validates conversation data before export to ensure data integrity
 */

import { Conversation, TopicSegment, Turn, Message, Sentence } from '../types';

export interface ValidationIssue {
  level: 'error' | 'warning' | 'info';
  code: string;
  message: string;
  path?: string;
  suggestion?: string;
}

export interface ValidationResult {
  valid: boolean;
  issues: ValidationIssue[];
  stats: {
    topics: number;
    turns: number;
    messages: number;
    sentences: number;
    spans: number;
    words: number;
    errors: number;
    warnings: number;
  };
}

/**
 * Validate a conversation for export readiness
 */
export function validateConversation(conversation: Conversation): ValidationResult {
  const issues: ValidationIssue[] = [];
  const stats = {
    topics: 0,
    turns: 0,
    messages: 0,
    sentences: 0,
    spans: 0,
    words: 0,
    errors: 0,
    warnings: 0,
  };

  // Check conversation level
  if (!conversation.id) {
    issues.push({
      level: 'error',
      code: 'MISSING_CONV_ID',
      message: 'Conversation is missing an ID',
      suggestion: 'Ensure the conversation was processed correctly',
    });
  }

  if (!conversation.topics || conversation.topics.length === 0) {
    issues.push({
      level: 'error',
      code: 'NO_TOPICS',
      message: 'Conversation has no topics',
      suggestion: 'Process the conversation to generate topic segments',
    });
  }

  // Validate topic structure
  conversation.topics?.forEach((topic, topicIdx) => {
    stats.topics++;
    const topicPath = `topics[${topicIdx}]`;

    if (!topic.id) {
      issues.push({
        level: 'error',
        code: 'MISSING_TOPIC_ID',
        message: `Topic ${topicIdx} is missing an ID`,
        path: topicPath,
      });
    }

    if (!topic.turns || topic.turns.length === 0) {
      issues.push({
        level: 'warning',
        code: 'EMPTY_TOPIC',
        message: `Topic ${topicIdx} has no turns`,
        path: topicPath,
        suggestion: 'Consider removing empty topics',
      });
    }

    // Validate turns
    topic.turns?.forEach((turn, turnIdx) => {
      stats.turns++;
      const turnPath = `${topicPath}.turns[${turnIdx}]`;

      if (!turn.id) {
        issues.push({
          level: 'error',
          code: 'MISSING_TURN_ID',
          message: `Turn ${turnIdx} in topic ${topicIdx} is missing an ID`,
          path: turnPath,
        });
      }

      if (!turn.messages || turn.messages.length === 0) {
        issues.push({
          level: 'warning',
          code: 'EMPTY_TURN',
          message: `Turn ${turnIdx} in topic ${topicIdx} has no messages`,
          path: turnPath,
        });
      }

      // Validate messages
      turn.messages?.forEach((msg, msgIdx) => {
        stats.messages++;
        const msgPath = `${turnPath}.messages[${msgIdx}]`;

        if (!msg.id) {
          issues.push({
            level: 'error',
            code: 'MISSING_MSG_ID',
            message: `Message ${msgIdx} in turn ${turnIdx} is missing an ID`,
            path: msgPath,
          });
        }

        if (!msg.role || !['user', 'assistant', 'system'].includes(msg.role)) {
          issues.push({
            level: 'warning',
            code: 'INVALID_ROLE',
            message: `Message ${msgIdx} has invalid role: ${msg.role}`,
            path: msgPath,
            suggestion: 'Role should be "user", "assistant", or "system"',
          });
        }

        if (!msg.content && msg.content !== '') {
          issues.push({
            level: 'warning',
            code: 'MISSING_CONTENT',
            message: `Message ${msgIdx} is missing content`,
            path: msgPath,
          });
        }

        // Validate sentences
        msg.sentences?.forEach((sent, sentIdx) => {
          stats.sentences++;
          const sentPath = `${msgPath}.sentences[${sentIdx}]`;

          if (!sent.id) {
            issues.push({
              level: 'error',
              code: 'MISSING_SENT_ID',
              message: `Sentence ${sentIdx} is missing an ID`,
              path: sentPath,
            });
          }

          if (!sent.text && sent.text !== '') {
            issues.push({
              level: 'warning',
              code: 'EMPTY_SENTENCE',
              message: `Sentence ${sentIdx} is empty`,
              path: sentPath,
            });
          }

          // Count spans and words
          stats.spans += sent.spans?.length || 0;
          stats.words += sent.words?.length || 0;

          // Check for orphan spans (spans without valid sentence)
          sent.spans?.forEach((span, spanIdx) => {
            if (!span.id) {
              issues.push({
                level: 'warning',
                code: 'MISSING_SPAN_ID',
                message: `Span ${spanIdx} in sentence ${sentIdx} is missing an ID`,
                path: `${sentPath}.spans[${spanIdx}]`,
              });
            }
          });
        });
      });
    });
  });

  // Check count consistency
  if (conversation.topicCount !== undefined && conversation.topicCount !== stats.topics) {
    issues.push({
      level: 'info',
      code: 'COUNT_MISMATCH',
      message: `Topic count mismatch: stored ${conversation.topicCount}, actual ${stats.topics}`,
      suggestion: 'Re-process conversation to update counts',
    });
  }

  // Check for very large exports
  const totalEntities = stats.topics + stats.turns + stats.messages + stats.sentences + stats.spans + stats.words;
  if (totalEntities > 10000) {
    issues.push({
      level: 'info',
      code: 'LARGE_EXPORT',
      message: `Large export: ${totalEntities.toLocaleString()} entities`,
      suggestion: 'Consider exporting without words for smaller file size',
    });
  }

  // Count error levels
  stats.errors = issues.filter(i => i.level === 'error').length;
  stats.warnings = issues.filter(i => i.level === 'warning').length;

  return {
    valid: stats.errors === 0,
    issues,
    stats,
  };
}

/**
 * Format validation result as a human-readable string
 */
export function formatValidationResult(result: ValidationResult): string {
  const lines: string[] = [];

  lines.push(`Validation ${result.valid ? 'PASSED' : 'FAILED'}`);
  lines.push('');
  lines.push(`Stats:`);
  lines.push(`  Topics: ${result.stats.topics}`);
  lines.push(`  Turns: ${result.stats.turns}`);
  lines.push(`  Messages: ${result.stats.messages}`);
  lines.push(`  Sentences: ${result.stats.sentences}`);
  lines.push(`  Spans: ${result.stats.spans}`);
  lines.push(`  Words: ${result.stats.words}`);
  lines.push('');

  if (result.issues.length > 0) {
    lines.push(`Issues (${result.stats.errors} errors, ${result.stats.warnings} warnings):`);
    result.issues.forEach(issue => {
      const prefix = issue.level === 'error' ? '✗' : issue.level === 'warning' ? '⚠' : 'ℹ';
      lines.push(`  ${prefix} [${issue.code}] ${issue.message}`);
      if (issue.path) lines.push(`    Path: ${issue.path}`);
      if (issue.suggestion) lines.push(`    Suggestion: ${issue.suggestion}`);
    });
  } else {
    lines.push('No issues found.');
  }

  return lines.join('\n');
}

/**
 * Quick validation check (returns boolean only)
 */
export function isValidForExport(conversation: Conversation): boolean {
  // Quick checks without full traversal
  if (!conversation.id) return false;
  if (!conversation.topics || conversation.topics.length === 0) return false;

  // Check first topic has turns
  const firstTopic = conversation.topics[0];
  if (!firstTopic.turns || firstTopic.turns.length === 0) return false;

  // Check first turn has messages
  const firstTurn = firstTopic.turns[0];
  if (!firstTurn.messages || firstTurn.messages.length === 0) return false;

  return true;
}
