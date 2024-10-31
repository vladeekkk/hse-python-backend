from fastapi import HTTPException

class ExceptionManager:
    @staticmethod
    def raise_not_found(detail: str):
        raise HTTPException(status_code=404, detail=detail)

    @staticmethod
    def raise_not_modified(detail: str):
        raise HTTPException(status_code=304, detail=detail)

    @staticmethod
    def raise_unprocessable_entity(detail: str):
        raise HTTPException(status_code=422, detail=detail)
