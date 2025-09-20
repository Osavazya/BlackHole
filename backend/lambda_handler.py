from mangum import Mangum
from app.main import app   # <- импортируй свою FastAPI-аппу

handler = Mangum(app)
