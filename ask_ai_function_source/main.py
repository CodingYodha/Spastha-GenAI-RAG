# FUNCTION 2: Search Function
import functions_framework
import os
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine

# --- FINAL CONFIGURATION ---
PROJECT_ID = "eminent-cycle-472512-u1"
LOCATION = "global"
DATA_STORE_ID = "spastha-final-datastore_1758347694410"  # Replace with your actual data store ID
# --- END CONFIGURATION ---

@functions_framework.http
def ask_legal_ai(request):
    """
    HTTP Cloud Function that queries ALL documents in the data store.
    """
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)
    
    headers = {'Access-Control-Allow-Origin': '*'}
    
    try:
        # Validate request method
        if request.method != 'POST':
            return ({'error': 'Only POST method is allowed.'}, 405, headers)
        
        request_json = request.get_json(silent=True)
        
        # Better error handling for missing JSON or query
        if not request_json:
            return ({'error': 'Request must contain valid JSON.'}, 400, headers)
        
        user_query = request_json.get('query', '').strip()
        
        if not user_query:
            return ({'error': 'JSON body must contain a non-empty "query" field.'}, 400, headers)
        
        # Optional: Limit query length to prevent abuse
        if len(user_query) > 1000:
            return ({'error': 'Query too long. Maximum 1000 characters allowed.'}, 400, headers)
        
        search_results = search_data_store(user_query)
        return (search_results, 200, headers)
        
    except Exception as e:
        print(f"An error occurred during the search process: {e}")
        return ({'error': 'An internal error occurred while querying the AI service.'}, 500, headers)

def search_data_store(search_query: str) -> dict:
    """
    Calls the Vertex AI Search API across all documents.
    """
    client_options = (
        ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com") 
        if LOCATION != "global" else None
    )
    client = discoveryengine.SearchServiceClient(client_options=client_options)
    
    serving_config = client.serving_config_path(
        project=PROJECT_ID, 
        location=LOCATION,
        data_store=DATA_STORE_ID, 
        serving_config="default_config",
    )
    
    content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
        summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
            summary_result_count=5, 
            include_citations=True,
            model_prompt_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelPromptSpec(
                preamble="You are a legal AI assistant. Provide accurate, helpful responses based on the legal documents in the knowledge base."
            )
        ),
        snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
            return_snippet=True,
            max_snippet_count=3
        )
    )
    
    print(f"Searching with query: {search_query}")
    
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=search_query,
        page_size=10,  # Increased from 5 for more results
        content_search_spec=content_search_spec,
    )
    
    response = client.search(request)
    
    # Enhanced response formatting
    formatted_response = {
        "summary": response.summary.summary_text if response.summary else "No summary available.",
        "query": search_query,
        "total_results": len(response.results),
        "references": []
    }
    
    for result in response.results:
        doc_data = result.document.derived_struct_data
        
        # Extract snippets more robustly
        snippets = []
        if "snippets" in doc_data and doc_data["snippets"]:
            for snippet_data in doc_data["snippets"]:
                if isinstance(snippet_data, dict) and "snippet" in snippet_data:
                    snippets.append(snippet_data["snippet"])
        
        snippet_text = " ... ".join(snippets) if snippets else "No snippet available."
        
        formatted_response["references"].append({
            "title": doc_data.get("title", "Untitled Document"),
            "link": doc_data.get("link", ""),
            "snippet": snippet_text,
            "document_id": result.document.id if hasattr(result.document, 'id') else ""
        })
    
    return formatted_response