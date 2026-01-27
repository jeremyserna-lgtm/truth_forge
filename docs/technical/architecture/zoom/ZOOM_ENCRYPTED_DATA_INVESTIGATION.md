> **DEPRECATED** - This document is superseded by [ZOOM_SOURCE_OF_TRUTH.md](../ZOOM_SOURCE_OF_TRUTH.md)
>
> This document is kept for historical reference only.

---

# Zoom Encrypted Data Investigation

## Summary

This document captures the results of investigating Zoom's locally encrypted databases to understand what additional data exists and whether it can be accessed through legitimate means.

**Verdict**: Encrypted databases are **not practically accessible** without Zoom server cooperation. Our capture strategy should focus entirely on UI-accessible and unencrypted filesystem data.

---

## Encrypted Databases Found

### Location: `~/Library/Application Support/zoom.us/data/`

| Database | Size | Purpose |
|----------|------|---------|
| `zoomus.zmdb.kvs.enc.db` | 86KB | Key-value store with cached user data |
| `zoom_conf_local_asr.enc.db` | 5KB | Local ASR (automatic speech recognition) data |
| `zoomus.enc.db` | 0 bytes | Empty container |
| `zoommeeting.enc.db` | 0 bytes | Empty container |

---

## Encryption Method

### SQLCipher Implementation

The databases use **SQLCipher** encryption with the following parameters:
- Page size: 1024
- KDF iterations: 4000

These parameters were confirmed by examining the database headers and comparing against known SQLCipher signatures.

### Trying to Open Without Key

```bash
sqlite3 zoomus.zmdb.kvs.enc.db
# Error: file is not a database
```

The databases are properly encrypted - not just protected files.

---

## Key Management Architecture

### The Challenge: Server-Side Key Component

Per security research ([InfoSec Writeup - Decrypting Zoom Team Chat](https://infosecwriteups.com/decrypting-zoom-team-chat-forensic-analysis-of-encrypted-chat-databases-394d5c471e60)):

> "The Key Wrapping Key (kwk) is **dynamically fetched from Zoom servers** during login or session refresh."

This is critical: Even if we had the local encrypted key, we'd need the server-side `kwk` to unwrap it.

### Platform Differences

| Platform | Key Storage | Accessibility |
|----------|-------------|---------------|
| Windows | `zoom.us.ini` + DPAPI | Wrapped key exists locally, requires kwk from server |
| macOS | Unknown location | Similar architecture, no ini file |

### Keychain Search Results

Searched macOS Keychain for Zoom-related keys:

```bash
security find-generic-password -a zoom.us
# No results for encryption keys
```

Checked for:
- `zoom` - No encryption keys
- `zoom.us` - No encryption keys
- `kwk` - Not found
- Various Zoom service names - Not found

---

## What the Encrypted Databases Likely Contain

Based on forensic research and database names:

### `zoomus.zmdb.kvs.enc.db` (Key-Value Store)
- User settings and preferences
- Cached contact information
- Historical meeting metadata
- UI state persistence

### `zoom_conf_local_asr.enc.db` (ASR Data)
- Local speech-to-text cache
- Transcription fragments
- Speaker identification data
- Audio processing metadata

### Empty Databases
The empty `.enc.db` files are likely:
- Schema templates for future use
- Containers that populate during specific features
- Legacy or deprecated storage

---

## Decryption Feasibility Assessment

### Approach 1: Extract Key from Memory ❌
- Requires memory forensics during active Zoom session
- Invasive and potentially unstable
- Key may be protected by secure enclaves
- **Not recommended** for personal use

### Approach 2: Intercept kwk from Server ❌
- Would require MitM on Zoom API calls
- Zoom uses certificate pinning
- Likely violates ToS
- **Not recommended**

### Approach 3: Brute Force ❌
- 4000 KDF iterations makes this slow
- Key space is effectively infinite
- **Not feasible**

### Approach 4: Wait for Zoom to Provide ❌
- No official API for local database access
- Privacy concerns make this unlikely
- **Not available**

---

## Conclusion: Focus on What's Accessible

### Available Data Sources (Focus Here)

1. **UI Extraction (AppleScript)**
   - All visible chat messages
   - Participant lists and states
   - Meeting info, recording status, screen share
   - Speaking indicators
   - Everything displayed during meeting

2. **Unencrypted Filesystem**
   - XMPP ID directories (`*@xmpp.zoom.us`)
   - Avatar cache (`ConfAvatar/`)
   - Preferences (`defaults read`)
   - Log files (if any)

3. **Process Information**
   - Window states
   - Active meeting detection
   - Session timing

### Data NOT Accessible (Accept Limitation)

- Historical chat messages (encrypted)
- Contact metadata beyond XMPP IDs (encrypted)
- Local ASR transcriptions (encrypted)
- Persistent preferences beyond what's in plist (encrypted)

---

## Recommendations

1. **Do not attempt decryption** - The server-side key component makes this impractical and potentially problematic

2. **Maximize UI extraction** - Our enhanced extractor already captures all UI-visible data

3. **Capture at the right moments** - SESSION_END is critical because temporary data vanishes

4. **Store persistent artifacts** - XMPP IDs and avatar hashes are unencrypted and valuable for identity correlation

5. **Accept the gap** - Some data is simply not meant to be accessible locally, and that's by design

---

## Technical References

- [InfoSec Writeups: Decrypting Zoom Team Chat](https://infosecwriteups.com/decrypting-zoom-team-chat-forensic-analysis-of-encrypted-chat-databases-394d5c471e60)
- [SQLCipher Documentation](https://www.zetetic.net/sqlcipher/sqlcipher-api/)
- Zoom Desktop Client forensic analysis papers

---

## Appendix: Encryption Detection

How to verify a file is SQLCipher encrypted:

```bash
# Check file header (SQLCipher has no "SQLite" magic bytes)
xxd -l 16 zoomus.zmdb.kvs.enc.db

# Try opening (will fail with "not a database")
sqlite3 zoomus.zmdb.kvs.enc.db ".tables"

# Check for SQLCipher signature
file zoomus.zmdb.kvs.enc.db
# Output: data (not "SQLite database")
```

---

**Last Updated**: 2025-12-02
**Status**: Investigation Complete
**Outcome**: Encrypted data not accessible; focus on UI extraction
