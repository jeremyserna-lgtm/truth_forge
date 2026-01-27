# Truth Engine User Manual

**Version**: 1.0.0
**Last Updated**: 2025-01-XX
**For**: End Users of Truth Engine

---

## 📖 Table of Contents

1. [What is Truth Engine?](#what-is-truth-engine)
2. [Getting Started](#getting-started)
3. [Your Data in Truth Engine](#your-data-in-truth-engine)
4. [Finding Your Information](#finding-your-information)
5. [Getting Insights and Recommendations](#getting-insights-and-recommendations)
6. [Understanding Your Patterns](#understanding-your-patterns)
7. [Searching Your Conversations](#searching-your-conversations)
8. [Exporting Your Data](#exporting-your-data)
9. [Privacy and Security](#privacy-and-security)
10. [Troubleshooting](#troubleshooting)
11. [Glossary](#glossary)

---

## 🎯 What is Truth Engine?

Truth Engine is a personal intelligence system that processes your conversations and communications to help you understand yourself better. It takes the "raw light" of your life—your conversations with AI assistants, messages, and interactions—and transforms it into meaningful insights.

### What Truth Engine Does

- **Processes Your Conversations**: Takes conversations from Claude Code, Codex, GitHub, text messages, and other sources
- **Finds Patterns**: Identifies recurring themes, topics, and patterns in how you communicate
- **Provides Insights**: Offers personalized recommendations and insights based on your data
- **Shows Your Timeline**: Helps you see your history and important moments
- **Answers Questions**: Lets you ask questions about your own data naturally

### What Makes Truth Engine Different

Unlike generic AI tools that just process commands, Truth Engine:
- **Understands You**: Learns your patterns and preferences over time
- **Respects Your Privacy**: Your data stays yours
- **Focuses on Growth**: Helps you understand yourself better, not just execute tasks
- **Provides Context**: Shows you the "why" behind patterns, not just the "what"

---

## 🚀 Getting Started

### First Time Setup

1. **Access Your Dashboard**: Log into Truth Engine through the web interface
2. **Connect Your Data Sources**: Truth Engine can process:
   - Claude Code conversations
   - Codex interactions
   - GitHub-related conversations
   - Text messages (if configured)
   - Other conversation sources

3. **Wait for Processing**: Your data is processed through multiple stages to ensure quality and accuracy. This happens automatically in the background.

4. **Explore Your Dashboard**: Once processing is complete, you'll see:
   - Recent conversations
   - Key insights
   - Recommended actions
   - Your timeline

### Understanding Your Dashboard

Your dashboard is organized into sections:

- **Recommendations**: Personalized suggestions based on your patterns
- **Recent Conversations**: Your latest interactions
- **Timeline**: Chronological view of your activity
- **Insights**: Key patterns and themes
- **Search**: Find specific conversations or topics

---

## 📊 Your Data in Truth Engine

### What Data is Processed

Truth Engine processes:
- **Conversation Messages**: Text from your conversations with AI assistants
- **Metadata**: When conversations happened, from which source, etc.
- **Patterns**: Topics, themes, and recurring concepts
- **Sentiment**: Emotional tone and patterns (if enabled)

### How Your Data is Processed

Your data goes through several stages:

1. **Extraction**: Messages are extracted from source files
2. **Enrichment**: Additional context and metadata are added
3. **Identity Recognition**: Your identity is preserved across different sources
4. **Text Correction**: Messages are cleaned and corrected for better analysis
5. **Storage**: Processed data is stored securely in your `entity_unified` table

**Note**: You don't need to understand these stages—they happen automatically. You just see the results.

### Data Freshness

- New conversations are processed automatically
- Processing typically happens within hours of new data arriving
- You'll see a status indicator showing when your data was last updated

---

## 🔍 Finding Your Information

### Using Search

**Search My Conversations** - Find any conversation quickly:
1. Click the search bar at the top
2. Type keywords, phrases, or topics
3. Results show matching conversations with context
4. Click any result to see the full conversation

**Find Conversation About...** - Natural language search:
- Ask questions like "Show me conversations about Python"
- Use topics, not just keywords
- Get semantically related results

### Filtering Your Data

**Filter by Source**:
- View only Claude Code conversations
- View only Codex interactions
- View only GitHub conversations
- Or view all sources together

**Filter by Date**:
- "Show Recent Conversations" - Last week, month, or custom range
- "View This Date Range" - Specific time periods
- Timeline view for chronological exploration

### Viewing Conversations

**View This Conversation**:
- Click any conversation in search results or timeline
- See full conversation thread with context
- View related conversations below

**Show Related Conversations**:
- When viewing a conversation, see others on similar topics
- Discover connected work automatically
- Explore your thinking patterns across conversations

---

## 💡 Getting Insights and Recommendations

### Getting Recommendations

**Get Recommendations** button:
- Click to receive personalized recommendations
- Based on your conversation patterns and recent activity
- Updated regularly as new data arrives
- Organized by category (Work, Life, Personal Growth)

**What Recommendations Look Like**:
- **Actionable**: Clear steps you can take
- **Contextual**: Based on your actual conversations
- **Personalized**: Tailored to your patterns and preferences

### Viewing Insights

**Show Me Insights** button:
- See key patterns in your communications
- Understand your focus areas and topics
- Discover trends over time
- Get summarized analytics

**Types of Insights**:
- **Topic Analysis**: What you talk about most
- **Pattern Recognition**: Recurring themes or concepts
- **Activity Trends**: How your communication patterns change
- **Sentiment Analysis**: Emotional patterns (if enabled)

### Understanding Your Focus

**What Should I Focus On?**:
- Analyzes your conversations to suggest priorities
- Identifies important themes you might be missing
- Highlights areas needing attention
- Provides actionable guidance

**Show My Patterns**:
- Visualizes recurring patterns in your communications
- Shows topic clusters and relationships
- Helps you see connections you might miss
- Updates as new data arrives

---

## 📈 Understanding Your Patterns

### Your Timeline

**Show My Timeline**:
- Chronological view of all your conversations
- See your activity over time
- Understand how your interests and focus evolve
- Navigate to any time period

**Key Moments**:
- Important conversations or breakthroughs highlighted
- Significant moments automatically detected
- Quick access to your most meaningful interactions

### Your Statistics

**Show My Stats**:
- Total conversation count
- Most active topics
- Communication frequency
- Sentiment trends (if enabled)
- Activity by source

### Comparing Time Periods

**Compare Time Periods**:
- Compare activity between weeks, months, or custom ranges
- See how your focus changes over time
- Understand evolution in your thinking
- Track progress on topics or projects

---

## 💬 Searching Your Conversations

### Basic Search

1. Use the search bar
2. Enter keywords or phrases
3. Results show:
   - Matching conversations
   - Relevant excerpts
   - Date and source
   - Context snippets

### Advanced Search Tips

- **Use quotes** for exact phrases: `"machine learning"`
- **Combine terms**: `Python AND database`
- **Exclude terms**: `coding NOT Python`
- **Search by date**: Use date filters
- **Search by source**: Filter to specific tools

### Natural Language Questions

**Ask About My Data**:
- Ask questions in plain English:
  - "What did I work on last week?"
  - "What topics am I most active in?"
  - "Show me conversations about project X"
- Get natural language answers
- See supporting conversations

---

## 📥 Exporting Your Data

### Exporting Conversations

**Export This Conversation**:
1. Open any conversation
2. Click "Export" button
3. Choose format:
   - **PDF**: Formatted document
   - **Markdown**: Plain text with formatting
   - **JSON**: Raw data format
4. Download to your device

### Exporting Your Data

**Export My Data**:
- Download all your processed data
- Choose format: CSV, JSON, or BigQuery export
- Select date range
- Includes all conversations and metadata

**Download My Insights**:
- Export insights and recommendations
- Shareable format (PDF or document)
- Perfect for reviews or sharing with others
- Includes visualizations and summaries

---

## 🔒 Privacy and Security

### Your Data is Private

- **Your Data Stays Yours**: Truth Engine doesn't share your data
- **Local Processing**: Most processing happens on secure servers
- **Encrypted Storage**: Data is encrypted at rest
- **Access Control**: Only you can access your data

### What We Don't Do

- We don't sell your data
- We don't use your data for training without permission
- We don't share your conversations with third parties
- We don't access your data without your explicit permission

### Data Retention

- Your data is stored as long as your account is active
- You can request deletion at any time
- Exported data is yours to keep indefinitely

---

## 🛠️ Troubleshooting

### Common Issues

**"No conversations found"**:
- Check that data sources are connected
- Wait for processing to complete
- Verify your data was imported correctly

**"Recommendations not updating"**:
- Processing may still be in progress
- Check your dashboard status
- Try refreshing the page

**"Search not finding conversations"**:
- Check spelling and keywords
- Try different search terms
- Use date filters to narrow results
- Check if conversations were processed correctly

**"Export failed"**:
- Check your internet connection
- Try a different format
- Contact support if issue persists

### Getting Help

- **In-App Help**: Click the "?" icon for contextual help
- **Documentation**: Visit the help section
- **Support**: Contact support through your dashboard
- **Feedback**: Use the feedback button to report issues

---

## 📚 Glossary

**Conversation**: A single interaction thread with an AI assistant or in a messaging platform

**Entity Unified**: The final table where all your processed data is stored

**Pattern**: A recurring theme, topic, or concept across multiple conversations

**Pipeline**: The automated process that transforms raw data into insights

**Recommendation**: Personalized suggestions based on your conversation patterns

**Source**: Where a conversation originated (Claude Code, Codex, GitHub, etc.)

**Timeline**: Chronological view of all your conversations and activity

---

## 🎯 Quick Reference

### One-Button Actions

| Button | What It Does |
|--------|-------------|
| **Get Recommendations** | Get personalized suggestions |
| **Search My Conversations** | Find any conversation |
| **Show My Timeline** | See chronological history |
| **Show Me Insights** | View key patterns |
| **Ask About My Data** | Natural language questions |
| **Export My Data** | Download your data |
| **Show Recent Conversations** | Latest interactions |
| **Show Key Moments** | Important highlights |

### Keyboard Shortcuts

- `Cmd/Ctrl + K`: Open search
- `Cmd/Ctrl + /`: Show keyboard shortcuts
- `Esc`: Close dialogs
- `Cmd/Ctrl + E`: Export current view

---

## 📝 Notes

This manual is a living document. As Truth Engine evolves, this manual will be updated. Check back regularly for new features and capabilities.

**Last Updated**: Check the version number at the top for the latest update date.

---

## 🤝 Feedback

Your feedback helps improve Truth Engine for everyone. Please share:
- What's working well
- What's confusing
- Features you'd like to see
- Documentation improvements

Thank you for using Truth Engine!
