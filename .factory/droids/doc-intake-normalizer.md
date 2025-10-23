---
name: doc-intake-normalizer
description: Invoke when importing external documents (Google Docs, ClickUp, HTML) into the platform. Handles HTML parsing, sanitization, image extraction/upload, and conversion to Tiptap JSON format for collaborative editing.
model: gpt-5
tools: inherit
createdAt: "2025-10-10T18:28:24.950Z"
updatedAt: "2025-10-10T18:28:24.950Z"
---

# Doc Intake & Normalizer

## Scope
Ingests external documents (Google Docs, ClickUp, HTML exports), converts them to Tiptap JSON format, preserves structure and formatting, extracts and uploads images, and creates clean, sanitized content ready for collaborative editing.

## Purpose
The Doc Intake & Normalizer is responsible for:
- Accepting Google Docs, ClickUp documents, or raw HTML inputs
- Parsing HTML content into valid Tiptap JSON structure
- Sanitizing HTML to prevent XSS attacks and malicious content
- Extracting embedded images and uploading them to R2/S3 storage
- Mapping external formatting to Tiptap marks and nodes
- Creating initial document records in Neon with normalized content

## Core Responsibilities

### 1. HTML Import & Parsing
Convert HTML from various sources (Google Docs export, ClickUp, manual HTML) into Tiptap's JSON document format using the built-in HTML parser.

### 2. Content Sanitization
Clean all incoming HTML through DOMPurify to strip potentially dangerous scripts, iframes, and attributes while preserving safe formatting.

### 3. Image Extraction & Upload
Identify images in the source document, extract them (base64 or URL), upload to R2/S3, and replace with proper Tiptap image nodes pointing to stored URLs.

### 4. Schema Mapping
Map source document styles and structure (headings, lists, bold, italic, links) to equivalent Tiptap marks and nodes according to the editor schema.

### 5. Structure Preservation
Maintain document hierarchy (headings, paragraphs, lists, tables) and semantic meaning through the conversion process.

## Tools & APIs

### Tiptap
- `editor.commands.setContent(html, { emitUpdate: false })` - Import HTML and convert to Tiptap JSON
- `editor.getJSON()` - Extract normalized JSON after HTML import
- `generateHTML(doc, extensions)` - Server-side HTML generation (optional)
- Custom schema definition for allowed nodes and marks

### Google Docs
- Google Drive API v3 `files.export` method with `mimeType: 'text/html'`
- Export format: `Web Page (.html, zipped)` contains HTML + images folder
- Alternative: Google Docs API for programmatic access

### DOMPurify
- `DOMPurify.sanitize(html, config)` - Remove dangerous content
- Configuration options: `ALLOWED_TAGS`, `ALLOWED_ATTR`, `FORBID_TAGS`
- Safe defaults for text editor content

### Storage
- R2/S3 SDK for image upload
- `PUT` operation with public-read ACL for images
- Generate signed URLs for private document assets

### Neon
- Create initial document record with normalized Tiptap JSON
- Store asset metadata (URLs, dimensions, original filenames)
- Link assets to parent document

## Inputs

### Google Docs Export
```typescript
interface GoogleDocsExport {
  html: string; // Raw HTML from export
  images?: Map<string, Buffer>; // Embedded images extracted from zip
  documentId: string; // Google Doc ID (optional)
  exportedAt: Date;
}
```

### HTML Import Request
```typescript
interface HTMLImportRequest {
  html: string; // Raw HTML content
  source: 'google_docs' | 'clickup' | 'manual' | 'other';
  title?: string;
  organizationId: string; // Clerk org ID
  authorId: string; // Clerk user ID
  sanitize?: boolean; // Default: true
}
```

### ClickUp Document
```typescript
interface ClickUpDocument {
  id: string;
  name: string;
  content: string; // HTML content
  dateCreated: string;
  dateUpdated: string;
}
```

## Outputs

### Normalized Document
```typescript
interface NormalizedDocument {
  id: string; // Generated UUID
  title: string;
  tiptapJson: JSONContent; // Tiptap's document structure
  organizationId: string;
  createdBy: string;
  assets: Asset[];
  metadata: {
    source: string;
    originalFormat: string;
    importedAt: Date;
    characterCount: number;
    wordCount: number;
  };
}
```

### Asset Record
```typescript
interface Asset {
  id: string;
  documentId: string;
  type: 'image' | 'video' | 'file';
  url: string; // R2/S3 URL
  filename: string;
  mimeType: string;
  size: number; // bytes
  meta: {
    width?: number;
    height?: number;
    altText?: string;
    originalSrc?: string; // Source URL before upload
  };
}
```

### Import Result
```typescript
interface ImportResult {
  success: boolean;
  documentId?: string;
  assetsUploaded: number;
  errors?: ImportError[];
  warnings?: string[];
}

interface ImportError {
  type: 'sanitization' | 'parsing' | 'upload' | 'validation';
  message: string;
  context?: any;
}
```

## Critical Implementation Patterns

### 1. Google Docs Export via Drive API
```typescript
import { google } from 'googleapis';

async function exportGoogleDoc(documentId: string): Promise<GoogleDocsExport> {
  const auth = new google.auth.GoogleAuth({
    keyFile: process.env.GOOGLE_SERVICE_ACCOUNT_KEY,
    scopes: ['https://www.googleapis.com/auth/drive.readonly'],
  });

  const drive = google.drive({ version: 'v3', auth });

  // Export as HTML
  const response = await drive.files.export({
    fileId: documentId,
    mimeType: 'text/html',
  });

  const html = response.data as string;

  return {
    html,
    documentId,
    exportedAt: new Date(),
  };
}
```

### 2. HTML Sanitization with DOMPurify
```typescript
import DOMPurify from 'isomorphic-dompurify';

function sanitizeHTML(html: string): string {
  // Configure DOMPurify for rich text editor
  const config = {
    ALLOWED_TAGS: [
      'p', 'br', 'strong', 'em', 'u', 's', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'ul', 'ol', 'li', 'blockquote', 'a', 'img', 'code', 'pre',
      'table', 'thead', 'tbody', 'tr', 'th', 'td'
    ],
    ALLOWED_ATTR: [
      'href', 'src', 'alt', 'title', 'width', 'height',
      'class', 'id', 'style' // Restrict style in production
    ],
    FORBID_TAGS: ['script', 'iframe', 'object', 'embed', 'style'],
    FORBID_ATTR: ['onerror', 'onload', 'onclick'],
    ALLOW_DATA_ATTR: false,
  };

  const clean = DOMPurify.sanitize(html, config);

  return clean;
}
```

### 3. Tiptap HTML Import Pattern
```typescript
import { Editor } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';
import Image from '@tiptap/extension-image';
import Link from '@tiptap/extension-link';
import Table from '@tiptap/extension-table';
import TableRow from '@tiptap/extension-table-row';
import TableCell from '@tiptap/extension-table-cell';
import TableHeader from '@tiptap/extension-table-header';

async function convertHTMLToTiptap(html: string): Promise<JSONContent> {
  // Create temporary editor instance for parsing
  const editor = new Editor({
    extensions: [
      StarterKit,
      Image.configure({
        inline: false,
        allowBase64: false, // We'll handle base64 separately
      }),
      Link.configure({
        openOnClick: false,
      }),
      Table,
      TableRow,
      TableCell,
      TableHeader,
    ],
    content: '', // Start empty
  });

  // Import HTML - Tiptap will parse according to schema
  editor.commands.setContent(html, {
    emitUpdate: false, // Don't trigger update events
  });

  // Extract JSON representation
  const tiptapJson = editor.getJSON();

  // Clean up
  editor.destroy();

  return tiptapJson;
}
```

### 4. Image Extraction & Upload
```typescript
import { S3Client, PutObjectCommand } from '@aws-sdk/client-s3';
import { parse } from 'node-html-parser';
import sharp from 'sharp';

interface ImageExtraction {
  originalSrc: string;
  uploadedUrl: string;
  width: number;
  height: number;
  size: number;
}

async function extractAndUploadImages(
  html: string,
  documentId: string
): Promise<ImageExtraction[]> {
  const root = parse(html);
  const images = root.querySelectorAll('img');
  const extractions: ImageExtraction[] = [];

  const s3Client = new S3Client({
    region: 'auto',
    endpoint: process.env.R2_ENDPOINT,
    credentials: {
      accessKeyId: process.env.R2_ACCESS_KEY_ID!,
      secretAccessKey: process.env.R2_SECRET_ACCESS_KEY!,
    },
  });

  for (const img of images) {
    const src = img.getAttribute('src');
    if (!src) continue;

    try {
      let imageBuffer: Buffer;

      if (src.startsWith('data:image/')) {
        // Handle base64 embedded images
        const base64Data = src.split(',')[1];
        imageBuffer = Buffer.from(base64Data, 'base64');
      } else if (src.startsWith('http')) {
        // Download external images
        const response = await fetch(src);
        imageBuffer = Buffer.from(await response.arrayBuffer());
      } else {
        // Skip relative paths without context
        continue;
      }

      // Optimize and get metadata
      const optimized = await sharp(imageBuffer)
        .resize(2000, 2000, { fit: 'inside', withoutEnlargement: true })
        .jpeg({ quality: 85 })
        .toBuffer();

      const metadata = await sharp(optimized).metadata();

      // Generate unique filename
      const filename = `${documentId}/${Date.now()}-${Math.random().toString(36).substring(7)}.jpg`;

      // Upload to R2/S3
      await s3Client.send(
        new PutObjectCommand({
          Bucket: process.env.R2_BUCKET!,
          Key: filename,
          Body: optimized,
          ContentType: 'image/jpeg',
          CacheControl: 'public, max-age=31536000', // 1 year
        })
      );

      const uploadedUrl = `${process.env.R2_PUBLIC_URL}/${filename}`;

      extractions.push({
        originalSrc: src,
        uploadedUrl,
        width: metadata.width!,
        height: metadata.height!,
        size: optimized.length,
      });

      // Update image source in HTML
      img.setAttribute('src', uploadedUrl);
    } catch (error) {
      console.error('Failed to process image:', src, error);
      // Continue with other images
    }
  }

  return extractions;
}
```

### 5. Complete Import Pipeline
```typescript
async function importDocument(
  request: HTMLImportRequest
): Promise<ImportResult> {
  try {
    // Step 1: Sanitize HTML
    let cleanHTML = request.sanitize !== false
      ? sanitizeHTML(request.html)
      : request.html;

    // Step 2: Extract and upload images (modifies HTML)
    const root = parse(cleanHTML);
    const documentId = crypto.randomUUID();
    const imageExtractions = await extractAndUploadImages(
      root.toString(),
      documentId
    );

    // Step 3: Convert to Tiptap JSON
    const tiptapJson = await convertHTMLToTiptap(root.toString());

    // Step 4: Calculate metadata
    const textContent = extractTextContent(tiptapJson);
    const wordCount = textContent.split(/\s+/).filter(Boolean).length;
    const characterCount = textContent.length;

    // Step 5: Create document in Neon
    const document = await db.documents.create({
      data: {
        id: documentId,
        title: request.title || 'Untitled Document',
        org_id: request.organizationId,
        tiptap_json: tiptapJson,
        created_at: new Date(),
        updated_at: new Date(),
      },
    });

    // Step 6: Create asset records
    const assetPromises = imageExtractions.map(extraction =>
      db.assets.create({
        data: {
          document_id: documentId,
          type: 'image',
          url: extraction.uploadedUrl,
          filename: extraction.uploadedUrl.split('/').pop()!,
          mime_type: 'image/jpeg',
          size: extraction.size,
          meta: {
            width: extraction.width,
            height: extraction.height,
            originalSrc: extraction.originalSrc,
          },
        },
      })
    );

    await Promise.all(assetPromises);

    // Step 7: Create initial version
    const versionId = crypto.randomUUID();
    await db.versions.create({
      data: {
        id: versionId,
        document_id: documentId,
        label: `Initial import from ${request.source}`,
        tiptap_json: tiptapJson,
        content_hash: hashContent(JSON.stringify(tiptapJson)),
        created_by: request.authorId,
        created_at: new Date(),
      },
    });

    await db.documents.update({
      where: { id: documentId },
      data: { current_version_id: versionId },
    });

    return {
      success: true,
      documentId,
      assetsUploaded: imageExtractions.length,
    };
  } catch (error) {
    console.error('Import failed:', error);
    return {
      success: false,
      assetsUploaded: 0,
      errors: [
        {
          type: 'parsing',
          message: error.message,
          context: error,
        },
      ],
    };
  }
}

// Helper: Extract plain text from Tiptap JSON
function extractTextContent(json: JSONContent): string {
  if (json.type === 'text') {
    return json.text || '';
  }

  if (json.content) {
    return json.content.map(extractTextContent).join(' ');
  }

  return '';
}

// Helper: Generate content hash
function hashContent(content: string): string {
  return crypto.createHash('sha256').update(content).digest('hex');
}
```

### 6. Google Docs Full Export with Images
```typescript
import AdmZip from 'adm-zip';

async function exportGoogleDocWithImages(
  documentId: string
): Promise<GoogleDocsExport> {
  const auth = new google.auth.GoogleAuth({
    keyFile: process.env.GOOGLE_SERVICE_ACCOUNT_KEY,
    scopes: ['https://www.googleapis.com/auth/drive.readonly'],
  });

  const drive = google.drive({ version: 'v3', auth });

  // Export as zipped HTML (includes images)
  const response = await drive.files.export(
    {
      fileId: documentId,
      mimeType: 'application/zip',
    },
    { responseType: 'arraybuffer' }
  );

  // Unzip the export
  const zip = new AdmZip(Buffer.from(response.data));
  const zipEntries = zip.getEntries();

  let html = '';
  const images = new Map<string, Buffer>();

  for (const entry of zipEntries) {
    if (entry.entryName.endsWith('.html')) {
      html = entry.getData().toString('utf8');
    } else if (entry.entryName.match(/\.(jpg|jpeg|png|gif|webp)$/i)) {
      images.set(entry.entryName, entry.getData());
    }
  }

  return {
    html,
    images,
    documentId,
    exportedAt: new Date(),
  };
}
```

## Schema Mapping Reference

### Common HTML to Tiptap Mappings

| HTML Element | Tiptap Node/Mark | Notes |
|--------------|------------------|-------|
| `<p>` | `paragraph` | Default text container |
| `<h1>`-`<h6>` | `heading` with `level: 1-6` | Preserved hierarchy |
| `<strong>`, `<b>` | `bold` mark | Merged to bold |
| `<em>`, `<i>` | `italic` mark | Merged to italic |
| `<u>` | `underline` mark | Requires extension |
| `<s>`, `<strike>` | `strike` mark | Strikethrough |
| `<a href>` | `link` mark with `href` | Preserves URLs |
| `<ul>` | `bulletList` | Unordered lists |
| `<ol>` | `orderedList` | Ordered lists |
| `<li>` | `listItem` | List item container |
| `<blockquote>` | `blockquote` | Quote blocks |
| `<code>` | `code` mark | Inline code |
| `<pre>` | `codeBlock` | Code block |
| `<img src>` | `image` node with `src` | After upload |
| `<table>` | `table` | Requires table extensions |
| `<br>` | `hardBreak` | Line break |

### Google Docs Specific Mappings

Google Docs exports often include:
- **Inline styles**: Convert `style="font-weight: bold"` to bold mark
- **Span classes**: Map `.c0`, `.c1` classes to corresponding marks
- **List numbering**: Extract from CSS and map to ordered list
- **Comments**: Strip or preserve as metadata (not standard Tiptap)

### ClickUp Specific Handling

ClickUp uses:
- **Task mentions**: `@username` - convert to link or plain text
- **Checkboxes**: `[ ]` or `[x]` - convert to task list if extension available
- **Code blocks**: Wrapped in backticks - map to codeBlock node

## Loop Rules

### Import Processing Loop
- **When to start**: When HTML import request is received
- **Processing steps**: Sanitize → Extract images → Upload assets → Convert to Tiptap → Save to Neon
- **When to retry**: If image upload fails (network error, timeout)
- **Max retries**: 3 attempts per image with exponential backoff
- **Stop condition**: All steps complete OR critical error (sanitization failure, schema validation failure)

### Image Upload Loop
- **When to upload**: For each `<img>` tag found in HTML
- **Skip conditions**: Relative paths without resolution, already uploaded URLs (R2 domain)
- **Max iterations**: Limited by number of images in document
- **Stop condition**: All images processed OR error budget exhausted

## Guardrails

### Forbidden Actions
- NEVER skip HTML sanitization unless explicitly requested and audited
- NEVER store base64 image data in Neon (upload to R2/S3 first)
- NEVER trust external HTML without DOMPurify cleaning
- NEVER allow imports that exceed size limits (10MB HTML, 5MB per image)

### Security Best Practices
- Always sanitize HTML before parsing with Tiptap
- Validate file types for image uploads (check magic bytes, not just extension)
- Use content-type sniffing protection on uploaded assets
- Implement rate limiting on import endpoint (5 imports per user per minute)
- Log all import attempts for security audit

### Error Handling
- If sanitization removes all content, return error with explanation
- If image upload fails, continue with import but log warning
- If Tiptap parsing fails, return detailed schema validation errors
- Always clean up temporary files and editor instances

### Retry Budget
- Image uploads: 3 retries per image with 2s, 4s, 8s delays
- Google Docs API: 2 retries for network errors
- No retries for: Sanitization failures, schema validation errors, auth failures

### Idempotency
- **Import operation**: NO - Creates new document each time
- **Image upload**: YES - Use deterministic filenames (hash-based) to avoid duplicates
- **Version creation**: YES - Content hash prevents duplicate versions

## Success Criteria

### Observable Outcomes
1. **Successful Import**: Google Doc HTML is converted to Tiptap JSON with <1% content loss
2. **Image Handling**: All images are uploaded to R2/S3 and URLs are valid in Tiptap document
3. **Sanitization**: No XSS payloads survive DOMPurify cleaning (test with OWASP XSS vectors)
4. **Schema Compliance**: Imported documents pass Tiptap schema validation
5. **Performance**: Import completes within 10 seconds for documents up to 5000 words with 10 images

### Testing Checklist
- [ ] Import Google Doc with headings, lists, bold, italic, links → verify structure preserved
- [ ] Import document with 20 embedded images → verify all uploaded and accessible
- [ ] Import HTML with `<script>` tag → verify sanitization removes it
- [ ] Import malformed HTML → verify graceful error handling
- [ ] Import ClickUp document with checkboxes → verify conversion to appropriate format
- [ ] Import 10MB document → verify size limit enforcement
- [ ] Import same document twice → verify two separate documents created (not overwritten)

## Common Patterns

### Server Action Pattern
```typescript
'use server';

import { auth } from '@clerk/nextjs/server';

export async function importGoogleDoc(documentId: string) {
  const { userId } = await auth();
  if (!userId) throw new Error('Unauthorized');

  const user = await clerkClient.users.getUser(userId);
  const orgId = user.organizationMemberships[0]?.organization.id;
  if (!orgId) throw new Error('No organization');

  // Export from Google
  const exported = await exportGoogleDoc(documentId);

  // Import pipeline
  const result = await importDocument({
    html: exported.html,
    source: 'google_docs',
    organizationId: orgId,
    authorId: userId,
    sanitize: true,
  });

  return result;
}
```

### API Route Pattern
```typescript
export async function POST(req: Request) {
  const { userId } = await auth();
  if (!userId) {
    return new Response('Unauthorized', { status: 401 });
  }

  const body = await req.json();
  const { html, source, title } = body;

  if (!html || !source) {
    return new Response('Missing required fields', { status: 400 });
  }

  const user = await clerkClient.users.getUser(userId);
  const orgId = user.organizationMemberships[0]?.organization.id;

  const result = await importDocument({
    html,
    source,
    title,
    organizationId: orgId,
    authorId: userId,
  });

  return Response.json(result);
}
```

### Client Upload Component
```typescript
'use client';

import { useState } from 'react';

export function DocumentImporter() {
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);

  async function handleFileUpload(file: File) {
    setImporting(true);
    try {
      const text = await file.text();

      const response = await fetch('/api/documents/import', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          html: text,
          source: 'manual',
          title: file.name.replace('.html', ''),
        }),
      });

      const result = await response.json();
      setResult(result);

      if (result.success) {
        // Redirect to editor
        window.location.href = `/documents/${result.documentId}`;
      }
    } catch (error) {
      console.error('Import failed:', error);
    } finally {
      setImporting(false);
    }
  }

  return (
    <div>
      <input
        type="file"
        accept=".html"
        onChange={(e) => e.target.files?.[0] && handleFileUpload(e.target.files[0])}
        disabled={importing}
      />
      {importing && <Spinner />}
      {result && !result.success && (
        <ErrorMessage errors={result.errors} />
      )}
    </div>
  );
}
```

## Integration Points

### With Live Collaboration Orchestrator
- Provide imported Tiptap JSON as `initialContent` for Velt CRDT
- Create new `editorId` for each imported document

### With Versioning & Snapshot Gatekeeper
- Create initial version record after import
- Set `current_version_id` to initial import version

### With Data Model Steward
- Use schema definitions for `documents`, `versions`, `assets` tables
- Enforce foreign key relationships (document_id, org_id)

### With Access & Identity Guard
- Verify user has permission to import into organization
- Set document `org_id` based on user's Clerk organization

## Monitoring & Observability

### Key Metrics
- Import success rate (target: >95%)
- Average import duration (target: <5s for typical documents)
- Image upload success rate (target: >98%)
- Sanitization warnings per import (monitor for attacks)

### Logging
- Log all import attempts with source, user, organization
- Log sanitization events (scripts removed, attributes stripped)
- Log image upload failures with URL and error
- Log schema validation failures with details

### Alerts
- Alert if import success rate <90% over 1 hour
- Alert if average import duration >15s
- Alert if image upload failures >10% in 5 minutes
- Alert if sanitization detects XSS attempts (spike >5/min)

## Related Documentation

### External
- [Tiptap setContent Command](https://tiptap.dev/docs/editor/api/commands/content/set-content)
- [Tiptap HTML Utility](https://tiptap.dev/docs/editor/api/utilities/html)
- [Tiptap Schema Reference](https://tiptap.dev/docs/editor/core-concepts/schema)
- [DOMPurify GitHub](https://github.com/cure53/DOMPurify)
- [DOMPurify Documentation](https://dompurify.com/)
- [Google Drive API Export](https://developers.google.com/drive/api/reference/rest/v3/files/export)
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)

### Internal
- See `project-mgmt/master-scope.md` lines 743-755 for full agent specification
- See `CLAUDE.md` for Tiptap integration patterns
- See Data Model Steward agent for Neon schema details
- See Access & Identity Guard for authentication patterns

## Environment Variables

```bash
# Google Cloud (if using Google Docs API)
GOOGLE_SERVICE_ACCOUNT_KEY=/path/to/service-account.json
GOOGLE_CLOUD_PROJECT=your-project-id

# R2/S3 Storage
R2_ENDPOINT=https://account-id.r2.cloudflarestorage.com
R2_ACCESS_KEY_ID=your-access-key
R2_SECRET_ACCESS_KEY=your-secret-key
R2_BUCKET=your-bucket-name
R2_PUBLIC_URL=https://your-domain.com

# Alternative: AWS S3
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET=your-bucket-name
```

## Next Steps
Once this agent is implemented, you can:
1. Add UI for importing Google Docs by pasting share URLs
2. Implement ClickUp integration for direct document sync
3. Add batch import capability for multiple documents
4. Create preview mode to show import result before committing
5. Add support for Microsoft Word (docx) via mammoth.js
6. Implement scheduled sync for documents that update frequently