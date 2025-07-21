from enum import Enum

class ResponseSignals(Enum):
    FILE_VALIDATED_SUCCESS="file validated successfully"
    FILE_TYPE_NOT_SUPPORTED="file type not supported"
    FILE_SIZE_EXCEEDED="file size exceeded"
    FILE_UPLOADED_SUCCESS="file uploaded successfully"
    FILE_UPLOADED_FAIL="file uploaded fail"
    FILE_PROCESS_FAIL="file processing fail"
    FILE_PROCESS_SUCCESS="file processing success"
    NO_FILES="there is no files"
    NO_FILE_NAME="not found with this name"
    PROJECT_NOT_FOUND_ERROR = "project_not_found"
    INSERT_INTO_VECTORDB_ERROR = "insert_into_vectordb_error"
    INSERT_INTO_VECTORDB_SUCCESS = "insert_into_vectordb_success"
    VECTORDB_COLLECTION_RETRIEVED = "vectordb_collection_retrieved"
    VECTORDB_SEARCH_SUCCESS="vectordb_search_success"
    VECTORDB_SEARCH_ERROR = "vectordb_search_error"
    RAG_ANSWER_ERROR = "rag_answer_error"
    RAG_ANSWER_SUCCESS = "rag_answer_success"
    
