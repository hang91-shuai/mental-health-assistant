"""
Flask 主入口 — 启动后端服务
"""

from flask import Flask
from flask_cors import CORS

from config.settings import settings

app = Flask(__name__)
CORS(app)

# ---- 注册路由 ----
from routes.health import health_bp
from routes.analyze import analyze_bp
from routes.chat import chat_bp

app.register_blueprint(health_bp)
app.register_blueprint(analyze_bp)
app.register_blueprint(chat_bp)


@app.route("/api/ping")
def ping():
    """连通性测试"""
    from utils.response import success
    return success({"status": "ok", "message": "server running"})


if __name__ == "__main__":
    app.run(debug=settings.FLASK_DEBUG, port=settings.FLASK_PORT)
