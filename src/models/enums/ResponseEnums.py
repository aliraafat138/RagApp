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
    
