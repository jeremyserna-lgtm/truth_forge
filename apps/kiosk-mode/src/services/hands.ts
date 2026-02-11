/**
 * The Hands - capabilities the LLM can use to reach outside the kiosk
 *
 * The user just talks. The LLM decides when to use these hands
 * to deliver things to the user's life.
 */

// Email configuration (uses local mail or configured SMTP)
const JEREMY_EMAIL = 'jeremy@example.com'; // Configure this

export interface HandResult {
  success: boolean;
  message: string;
  url?: string;
  path?: string;
}

/**
 * Send an email to Jeremy with an attachment or content
 */
export async function sendEmail(
  subject: string,
  body: string,
  attachment?: { name: string; content: string; type: string }
): Promise<HandResult> {
  try {
    // For now, save to a folder that can be picked up by email client
    // In production, this would use nodemailer or an email API
    const emailDir = '/Users/jeremyserna/truth_forge/data/outbox';
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const emailFile = `${emailDir}/${timestamp}-${subject.replace(/[^a-z0-9]/gi, '_')}.json`;

    const emailData = {
      to: JEREMY_EMAIL,
      subject,
      body,
      attachment,
      createdAt: new Date().toISOString()
    };

    await fetch('/api/write-file', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: emailFile, content: JSON.stringify(emailData, null, 2) })
    });

    return { success: true, message: `Email queued: ${subject}`, path: emailFile };
  } catch (error) {
    return { success: false, message: `Failed to send email: ${error}` };
  }
}

/**
 * Create a document and save it to Jeremy's documents folder
 */
export async function createDocument(
  name: string,
  content: string,
  type: 'md' | 'txt' | 'html' | 'json' = 'md'
): Promise<HandResult> {
  try {
    const docsDir = '/Users/jeremyserna/truth_forge/data/documents';
    const timestamp = new Date().toISOString().split('T')[0];
    const fileName = `${timestamp}-${name.replace(/[^a-z0-9]/gi, '_')}.${type}`;
    const filePath = `${docsDir}/${fileName}`;

    await fetch('/api/write-file', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: filePath, content })
    });

    return { success: true, message: `Document created: ${fileName}`, path: filePath };
  } catch (error) {
    return { success: false, message: `Failed to create document: ${error}` };
  }
}

/**
 * Build and deploy a mini website/app
 */
export async function buildMiniSite(
  name: string,
  htmlContent: string,
  description: string
): Promise<HandResult> {
  try {
    const sitesDir = '/Users/jeremyserna/truth_forge/apps/kiosk-sites';
    const siteName = name.toLowerCase().replace(/[^a-z0-9]/gi, '-');
    const siteDir = `${sitesDir}/${siteName}`;

    // Create a simple static site
    await fetch('/api/create-site', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: siteName,
        html: htmlContent,
        description
      })
    });

    return {
      success: true,
      message: `Site created: ${name}`,
      url: `file://${siteDir}/index.html`
    };
  } catch (error) {
    return { success: false, message: `Failed to build site: ${error}` };
  }
}

/**
 * Create a crossword puzzle from topics
 */
export async function createCrossword(
  title: string,
  clues: { word: string; clue: string }[]
): Promise<HandResult> {
  // Generate crossword HTML
  const html = generateCrosswordHTML(title, clues);
  return buildMiniSite(`crossword-${Date.now()}`, html, `Crossword: ${title}`);
}

/**
 * Generate crossword puzzle HTML
 */
function generateCrosswordHTML(title: string, clues: { word: string; clue: string }[]): string {
  return `<!DOCTYPE html>
<html>
<head>
  <title>${title}</title>
  <style>
    body { font-family: system-ui; max-width: 800px; margin: 40px auto; padding: 20px; background: #1a1a2e; color: white; }
    h1 { text-align: center; }
    .clues { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 30px; }
    .clue { padding: 10px; background: rgba(255,255,255,0.1); border-radius: 8px; }
    .clue-word { font-weight: bold; color: #4ade80; }
    input { width: 100%; padding: 8px; margin-top: 8px; border: none; border-radius: 4px; }
  </style>
</head>
<body>
  <h1>${title}</h1>
  <div class="clues">
    ${clues.map((c, i) => `
      <div class="clue">
        <span class="clue-word">${i + 1}.</span> ${c.clue}
        <input type="text" placeholder="Your answer..." maxlength="${c.word.length}" />
      </div>
    `).join('')}
  </div>
  <script>
    document.querySelectorAll('input').forEach((input, i) => {
      const answer = ${JSON.stringify(clues.map(c => c.word.toUpperCase()))};
      input.addEventListener('input', (e) => {
        if (e.target.value.toUpperCase() === answer[i]) {
          e.target.style.background = '#4ade80';
          e.target.style.color = 'black';
        }
      });
    });
  </script>
</body>
</html>`;
}

/**
 * Open a URL in the default browser (outside the kiosk)
 */
export async function openInBrowser(url: string): Promise<HandResult> {
  try {
    await fetch('/api/open-url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    return { success: true, message: `Opened: ${url}`, url };
  } catch (error) {
    return { success: false, message: `Failed to open URL: ${error}` };
  }
}

/**
 * Schedule a reminder (creates a calendar event or notification)
 */
export async function scheduleReminder(
  title: string,
  when: Date,
  notes?: string
): Promise<HandResult> {
  try {
    const remindersDir = '/Users/jeremyserna/truth_forge/data/reminders';
    const reminderFile = `${remindersDir}/${when.toISOString().split('T')[0]}-${title.replace(/[^a-z0-9]/gi, '_')}.json`;

    await fetch('/api/write-file', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        path: reminderFile,
        content: JSON.stringify({ title, when: when.toISOString(), notes }, null, 2)
      })
    });

    return { success: true, message: `Reminder set: ${title}`, path: reminderFile };
  } catch (error) {
    return { success: false, message: `Failed to set reminder: ${error}` };
  }
}
