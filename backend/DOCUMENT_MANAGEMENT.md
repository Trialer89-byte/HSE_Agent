# Document Management API

## Overview

The document management system allows you to upload, update, and manage normative documents with automatic versioning and duplicate detection.

## Features

1. **Automatic Versioning**: When uploading a document with an existing `document_code`, the system automatically creates a new version (e.g., 1.0 → 1.1)

2. **Duplicate Detection**: Uses SHA256 hash to detect identical files and prevent duplicate uploads

3. **Force Reload**: Option to re-analyze documents even if the file already exists

4. **Metadata Updates**: Update document metadata without re-uploading the file

5. **Version Management**: View and manage all versions of a document

## API Endpoints

### Upload Document
```
POST /api/documents/upload
```

Form data:
- `file`: Document file (PDF, DOCX, DOC, TXT)
- `document_code`: Unique document identifier
- `title`: Document title
- `document_type`: Type (e.g., "normativa", "istruzione_operativa")
- `category`: Document category
- `subcategory`: Optional subcategory
- `authority`: Issuing authority
- `scope`: Document scope ("tenant" or "global")
- `industry_sectors`: Comma-separated sectors
- `force_reload`: Force re-analysis (true/false)

### List Documents
```
GET /api/documents?document_type=normativa&category=safety&limit=50&offset=0
```

### Get Document
```
GET /api/documents/{document_id}
```

### Update Document Metadata
```
PATCH /api/documents/{document_id}
```

JSON body:
```json
{
  "title": "Updated Title",
  "category": "New Category",
  "industry_sectors": ["chemical", "construction"]
}
```

### Get Document Versions
```
GET /api/documents/versions/{document_code}
```

### Delete Document
```
DELETE /api/documents/{document_id}
```

### Re-analyze Document
```
POST /api/documents/{document_id}/reanalyze
```

## Database Migration

Run the migration to add the file_hash column:

```bash
cd backend
python migrations/add_file_hash_to_documents.py
```

## Usage Examples

### Upload a New Document
```python
import requests

files = {'file': open('normativa.pdf', 'rb')}
data = {
    'document_code': 'NORM-001',
    'title': 'Safety Regulations 2024',
    'document_type': 'normativa',
    'category': 'safety',
    'authority': 'Ministry of Labor',
    'industry_sectors': 'chemical,construction'
}

response = requests.post(
    'http://localhost:8000/api/documents/upload',
    files=files,
    data=data,
    headers={'Authorization': 'Bearer YOUR_TOKEN'}
)
```

### Handle Duplicate Files
```python
# If upload fails with 409 Conflict (duplicate file)
if response.status_code == 409:
    # Option 1: Force reload
    data['force_reload'] = True
    response = requests.post(url, files=files, data=data, headers=headers)
    
    # Option 2: Update metadata only
    existing_doc_id = extract_id_from_error_message(response.json())
    requests.patch(
        f'http://localhost:8000/api/documents/{existing_doc_id}',
        json={'title': 'Updated Title'},
        headers=headers
    )
```

## Implementation Details

1. **Hash Calculation**: SHA256 hash is calculated on file upload to detect duplicates

2. **Version Numbering**: Follows semantic versioning (major.minor format)

3. **Vector Storage**: Each document is chunked and stored in Weaviate for semantic search

4. **Tenant Isolation**: All documents are isolated by tenant_id

5. **AI Analysis**: Documents are automatically analyzed for keywords and relevance scoring