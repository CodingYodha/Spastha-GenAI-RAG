# FUNCTION 1: Document Ingestion
import functions_framework
import os
import re
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions

# --- FINAL CONFIGURATION ---
PROJECT_ID = "eminent-cycle-472512-u1"
LOCATION = "global"
DATA_STORE_ID = "spastha-final-datastore_1758347694410"  # Replace with your actual data store ID
# --- END CONFIGURATION ---

@functions_framework.cloud_event
def ingest_document(cloud_event):
    """
    Cloud Storage triggered function that automatically indexes newly uploaded documents.
    """
    try:
        data = cloud_event.data
        bucket_name = data['bucket']
        file_name = data['name']
        
        # Skip if not a PDF file
        if not file_name.lower().endswith('.pdf'):
            print(f"Skipping non-PDF file: {file_name}")
            return
            
        print(f"Processing document: {file_name}")
        document_uri = f"gs://{bucket_name}/{file_name}"
        index_document(document_uri, file_name)
        print(f"Successfully indexed document {file_name}")
        
    except Exception as e:
        print(f"Error processing document ingestion: {e}")
        raise e

def index_document(document_uri: str, file_name: str):
    """
    Indexes a document in Vertex AI Search.
    """
    client_options = (
        ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com") 
        if LOCATION != "global" else None
    )
    client = discoveryengine.DocumentServiceClient(client_options=client_options)
    
    parent = client.branch_path(
        project=PROJECT_ID,
        location=LOCATION,
        data_store=DATA_STORE_ID,
        branch="default_branch"
    )
    
    # More robust document ID sanitization
    sanitized_file_name = re.sub(r'[^a-zA-Z0-9_-]', '-', file_name.lower())
    # Ensure ID doesn't start with a number and isn't too long
    if sanitized_file_name[0].isdigit():
        sanitized_file_name = 'doc-' + sanitized_file_name
    sanitized_file_name = sanitized_file_name[:100]  # Limit length
    
    document = discoveryengine.Document(
        id=sanitized_file_name,
        struct_data={
            "title": file_name,
            "document_type": "legal_document",
            "upload_timestamp": str(os.environ.get('TIMESTAMP', '')),
        },
        content=discoveryengine.Document.Content(
            uri=document_uri,
            mime_type="application/pdf"
        )
    )
    
    request = discoveryengine.CreateDocumentRequest(
        parent=parent,
        document=document,
        document_id=document.id
    )
    
    operation = client.create_document(request=request)
    print(f"Document indexing initiated. Operation: {operation.name}")
    return operation