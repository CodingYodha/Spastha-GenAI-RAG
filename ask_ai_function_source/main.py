import functions_framework
import os
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine

# --- CONFIGURATION ---
PROJECT_ID = "spastha-genai-exchange-google"
LOCATION = "global"
DATA_STORE_ID = "spastha-doc-store_1758203307842"
# --- END CONFIGURATION ---

@functions_framework.http
def ask_legal_ai(request):
    """
    An HTTP Cloud Function that serves as the API for the legal AI.
    It receives a user's question AND userId, queries only that user's documents,
    and returns a clean JSON response.
    """
    # --- CORS Headers ---
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 204, headers)

    headers = {
        'Access-Control-Allow-Origin': '*'
    }
    # --- End CORS Headers ---

    # --- Request Validation ---
    try:
        request_json = request.get_json(silent=True)
        if not request_json or 'query' not in request_json:
            error_message = 'Invalid request: JSON body with a "query" key is required.'
            print(error_message)
            return ({'error': error_message}, 400, headers)
        
        user_query = request_json['query']
        user_id = request_json.get('userId')  # Optional for backward compatibility
        
        if not user_query:
            error_message = 'Invalid request: "query" cannot be empty.'
            print(error_message)
            return ({'error': error_message}, 400, headers)

    except Exception as e:
        print(f"Error parsing request: {e}")
        return ({'error': 'Failed to parse request body.'}, 400, headers)
    # --- End Request Validation ---

    # --- Call the AI Service ---
    try:
        search_results = search_data_store(user_query, user_id)
        return (search_results, 200, headers)
    except Exception as e:
        print(f"An error occurred during the search process: {e}")
        return ({'error': 'An internal error occurred while querying the AI service.'}, 500, headers)
    # --- End Call the AI Service ---


def search_data_store(search_query: str, user_id: str = None) -> dict:
    """
    Calls the Vertex AI Search API with the user's query, filtering by userId if provided,
    and returns a formatted dictionary.
    """
    client_options = (
        ClientOptions(api_endpoint=f"{LOCATION}-discoveryengine.googleapis.com")
        if LOCATION != "global"
        else None
    )
    client = discoveryengine.SearchServiceClient(client_options=client_options)

    serving_config = client.serving_config_path(
        project=PROJECT_ID,
        location=LOCATION,
        data_store=DATA_STORE_ID,
        serving_config="default_config",
    )
    
    # --- Create Search Specs ---
    summary_spec = discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
        summary_result_count=5,
        include_citations=True
    )

    snippet_spec = discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
        return_snippet=True
    )

    content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
        summary_spec=summary_spec,
        snippet_spec=snippet_spec
    )
    
    # --- CRITICAL ADDITION: User-specific filtering ---
    search_filter = None
    if user_id:
        search_filter = f'user_id: "{user_id}"'
        print(f"Applying filter: {search_filter}")
    else:
        print("No userId provided - searching across all documents")
    # --- End User Filtering ---

    # Build the final search request with optional filter
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=search_query,
        page_size=5,
        content_search_spec=content_search_spec,
        filter=search_filter  # This is the key addition!
    )

    response = client.search(request)

    # --- Format Response ---
    formatted_response = {
        "summary": response.summary.summary_text if response.summary else "No summary available",
        "user_id": user_id,
        "query": search_query,
        "references": []
    }
    
    for result in response.results:
        doc_data = result.document.derived_struct_data
        
        snippet_text = ""
        if "snippets" in doc_data and doc_data["snippets"]:
            snippet_text = doc_data["snippets"][0].get("snippet", "Snippet not available.")

        formatted_response["references"].append({
            "title": doc_data.get("title", "Untitled Document"),
            "link": doc_data.get("link", ""),
            "snippet": snippet_text,
            "user_id": doc_data.get("user_id", "unknown")  # Show which user's doc this is
        })
    
    return formatted_response