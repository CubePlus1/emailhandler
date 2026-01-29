/**
 * Cloudflare Email Worker
 * Handles incoming emails and forwards them to Flask API
 */

export default {
  async email(message, env, ctx) {
    try {
      // Parse email metadata
      const emailData = {
        from: message.from,
        to: message.to,
        subject: message.headers.get('subject') || '',
        timestamp: new Date().toISOString(),
        headers: {},
        body: {
          html: '',
          text: ''
        },
        attachments: []
      };

      // Extract important headers
      const headerKeys = ['date', 'message-id', 'reply-to', 'cc', 'bcc'];
      for (const key of headerKeys) {
        const value = message.headers.get(key);
        if (value) {
          emailData.headers[key] = value;
        }
      }

      // Read email stream
      const reader = message.raw.getReader();
      const chunks = [];
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        chunks.push(value);
      }

      // Combine chunks into single buffer
      const totalLength = chunks.reduce((acc, chunk) => acc + chunk.length, 0);
      const fullMessage = new Uint8Array(totalLength);
      let offset = 0;
      for (const chunk of chunks) {
        fullMessage.set(chunk, offset);
        offset += chunk.length;
      }

      // Parse MIME message
      const rawEmail = new TextDecoder().decode(fullMessage);
      const parsed = await parseEmail(rawEmail);

      emailData.body.html = parsed.html || '';
      emailData.body.text = parsed.text || '';
      emailData.attachments = parsed.attachments || [];

      // Send to Flask API
      const response = await fetch(`${env.FLASK_API_URL}/webhook/email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Webhook-Secret': env.WEBHOOK_SECRET
        },
        body: JSON.stringify(emailData)
      });

      if (!response.ok) {
        throw new Error(`Flask API returned ${response.status}: ${await response.text()}`);
      }

      console.log('Email processed successfully:', {
        from: emailData.from,
        subject: emailData.subject,
        attachmentCount: emailData.attachments.length
      });

      return new Response('Email processed successfully', { status: 200 });

    } catch (error) {
      console.error('Error processing email:', error);

      // Return error but don't bounce the email
      return new Response(`Error: ${error.message}`, { status: 500 });
    }
  }
};

/**
 * Parse email content (MIME parsing)
 * @param {string} rawEmail - Raw email content
 * @returns {Object} Parsed email with html, text, and attachments
 */
async function parseEmail(rawEmail) {
  const result = {
    html: '',
    text: '',
    attachments: []
  };

  // Split headers and body
  const parts = rawEmail.split('\r\n\r\n');
  if (parts.length < 2) {
    result.text = rawEmail;
    return result;
  }

  const headers = parts[0];
  const body = parts.slice(1).join('\r\n\r\n');

  // Extract Content-Type from headers
  const contentTypeMatch = headers.match(/Content-Type:\s*([^;\r\n]+)/i);
  const contentType = contentTypeMatch ? contentTypeMatch[1].trim().toLowerCase() : 'text/plain';

  // Check if multipart
  if (contentType.startsWith('multipart/')) {
    const boundaryMatch = headers.match(/boundary=["']?([^"'\r\n;]+)/i);
    if (boundaryMatch) {
      const boundary = boundaryMatch[1];
      const sections = body.split(`--${boundary}`);

      for (const section of sections) {
        if (section.trim() === '' || section.trim() === '--') continue;

        await parseSection(section, result);
      }
    }
  } else {
    // Single part email
    if (contentType.includes('text/html')) {
      result.html = decodeBody(body, headers);
    } else {
      result.text = decodeBody(body, headers);
    }
  }

  return result;
}

/**
 * Parse individual MIME section
 * @param {string} section - MIME section content
 * @param {Object} result - Result object to populate
 */
async function parseSection(section, result) {
  const sectionParts = section.split('\r\n\r\n');
  if (sectionParts.length < 2) return;

  const sectionHeaders = sectionParts[0];
  const sectionBody = sectionParts.slice(1).join('\r\n\r\n');

  const contentTypeMatch = sectionHeaders.match(/Content-Type:\s*([^;\r\n]+)/i);
  const contentType = contentTypeMatch ? contentTypeMatch[1].trim().toLowerCase() : '';

  const dispositionMatch = sectionHeaders.match(/Content-Disposition:\s*([^;\r\n]+)/i);
  const disposition = dispositionMatch ? dispositionMatch[1].trim().toLowerCase() : '';

  // Check if it's an attachment
  if (disposition === 'attachment' || disposition === 'inline') {
    const filenameMatch = sectionHeaders.match(/filename=["']?([^"'\r\n;]+)/i);
    const filename = filenameMatch ? filenameMatch[1] : 'unknown';

    result.attachments.push({
      filename: filename,
      contentType: contentType || 'application/octet-stream',
      size: sectionBody.length
    });
  } else {
    // It's a body part
    if (contentType.includes('text/html')) {
      result.html = decodeBody(sectionBody, sectionHeaders);
    } else if (contentType.includes('text/plain')) {
      result.text = decodeBody(sectionBody, sectionHeaders);
    } else if (contentType.startsWith('multipart/')) {
      // Nested multipart - recursively parse
      const boundaryMatch = sectionHeaders.match(/boundary=["']?([^"'\r\n;]+)/i);
      if (boundaryMatch) {
        const boundary = boundaryMatch[1];
        const subsections = sectionBody.split(`--${boundary}`);
        for (const subsection of subsections) {
          if (subsection.trim() === '' || subsection.trim() === '--') continue;
          await parseSection(subsection, result);
        }
      }
    }
  }
}

/**
 * Decode body content based on encoding
 * @param {string} body - Encoded body content
 * @param {string} headers - Section headers
 * @returns {string} Decoded content
 */
function decodeBody(body, headers) {
  const encodingMatch = headers.match(/Content-Transfer-Encoding:\s*([^\r\n]+)/i);
  const encoding = encodingMatch ? encodingMatch[1].trim().toLowerCase() : '7bit';

  let decoded = body;

  if (encoding === 'base64') {
    try {
      // Remove whitespace from base64
      const cleaned = body.replace(/\s/g, '');
      decoded = atob(cleaned);
    } catch (e) {
      console.error('Base64 decode error:', e);
    }
  } else if (encoding === 'quoted-printable') {
    decoded = body
      .replace(/=\r?\n/g, '') // Remove soft line breaks
      .replace(/=([0-9A-F]{2})/gi, (_, hex) => String.fromCharCode(parseInt(hex, 16)));
  }

  return decoded.trim();
}
