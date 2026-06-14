from fastapi import HTTPException, status

class DatabaseError(HTTPException):
    def __init__(self, detail: str = "Database error occurred"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class ExternalAPIError(HTTPException):
    def __init__(self, detail: str = "External API error"):
        super().__init__(status_code=status.HTTP_502_BAD_GATEWAY, detail=detail)

class LocationNotFoundError(HTTPException):
    def __init__(self, detail: str = "Location not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)
