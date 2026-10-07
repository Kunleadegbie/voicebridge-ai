from pydantic import BaseModel
class TextTestIn(BaseModel):
    text: str
    language: str = "en-NG"
    session_id: str = "local-test"
