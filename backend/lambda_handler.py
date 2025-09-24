# lambda_handler.py (финальный)
from mangum import Mangum
from app.main import app
handler = Mangum(app)
