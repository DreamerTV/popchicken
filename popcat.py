from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///popcat.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# 創建 User 模型來存儲點擊數
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    clicks = db.Column(db.Integer, default=0)

# 初始化資料庫
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/click", methods=["POST"])
def click():
    username = request.json.get("username")
    if not username:
        return jsonify({"error": "請提供用戶名"}), 400

    user = User.query.filter_by(name=username).first()
    if not user:
        user = User(name=username, clicks=0)
        db.session.add(user)

    user.clicks += 1
    db.session.commit()
    return jsonify({"clicks": user.clicks})

@app.route("/get_clicks", methods=["GET"])
def get_clicks():
    username = request.args.get("username")
    user = User.query.filter_by(name=username).first()
    return jsonify({"clicks": user.clicks if user else 0})

@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    top_users = User.query.order_by(User.clicks.desc()).limit(5).all()
    leaderboard_data = [{"name": u.name, "clicks": u.clicks} for u in top_users]
    return jsonify(leaderboard_data)

if __name__ == "__main__":
    app.run(debug=True)

