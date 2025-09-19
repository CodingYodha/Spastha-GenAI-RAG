import functions_framework
import os
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.client_options import ClientOptions

# --- CONFIGURATION ---
PROJECT_ID = "spastha-genai-exchange-google"
LOCATION = "global"
DATA_STORE_ID = "spastha-doc-store_1758203307842"
# --- END CONFIGURATION ---

@functions_framework.cloud_event
def ingest_document(cloud_event):
    """
    Cloud Storage triggered function that automatically indexes newly uploaded documents
    with user-specific metadata for document isolation.
    """
    try:
        # Extract file information from the Cloud Storage event
        data = cloud_event.data
        bucket_name = data['bucket']
        file_name = data['name']
        
        # Extract userId from file metadata or filename convention
        # Option 1: If userId is embedded in filename (e.g., "user123_rental_agreement.pdf")
        if '_' in file_name:
            user_id = file_name.split('_')[0]
        else:
            # Fallback: use a default user or log an error
            user_id = "default_user"
            print(f"Warning: Could not extract userId from filename {file_name}")
        
        print(f"Processing document: {file_name} for user: {user_id}")
        
        # Create the document URI for Vertex AI
        document_uri = f"gs://{bucket_name}/{file_name}"
        
        # Index the document with user metadata
        index_document_with_metadata(document_uri, user_id, file_name)
        
        print(f"Successfully indexed document {file_name} for user {user_id}")
        
    except Exception as e:
        print(f"Error processing document ingestion: {e}")
        raise e

def index_document_with_metadata(document_uri: str, user_id: str, file_name: str):
    """
    Index a document in Vertex AI Search with user-specific metadata
    """
    client_options = (
        ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
        if LOCATION != "global"
        else None
    )
    
    # Use DocumentService for programmatic document indexing
    client = discoveryengine.DocumentServiceClient(client_options=client_options)
    
    # Construct the parent path
    parent = client.branch_path(
        project=PROJECT_ID,
        location=LOCATION,
        data_store=DATA_STORE_ID,
        branch="default_branch"
    )
    
    # Create document with user metadata
    document = discoveryengine.Document(
        id=f"{user_id}_{file_name}",  # Unique document ID
        struct_data={
            "title": file_name,
            "user_id": user_id,  # Critical: This enables user-specific filtering
            "document_type": "legal_document",
            "upload_timestamp": "2024-01-01"  # You can use actual timestamp
        },
        content=discoveryengine.Document.Content(
            uri=document_uri,
            mime_type="application/pdf"
        )
    )
    
    # Create the document in the data store
    request = discoveryengine.CreateDocumentRequest(
        parent=parent,
        document=document,
        document_id=document.id
    )
    
    operation = client.create_document(request=request)
    print(f"Document indexing initiated. Operation: {operation.name}")
    
    return operation