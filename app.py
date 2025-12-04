from flask import Flask, request, render_template, jsonify
import os
import re
import base64
from datetime import datetime

app = Flask(__name__)

RESULT_DIR = os.path.join(os.path.dirname(__file__), "result")
os.makedirs(RESULT_DIR, exist_ok=True)

@app.route("/")
def index():
    # templates/index.html を表示
    return render_template("index.html")

@app.route("/upload_result", methods=["POST"])
def upload_result():
    """
    クライアントから画像と成功判定を受け取り保存するAPI
    期待データ例 (multipart/form-data):
      - image: "data:image/png;base64,iVBORw0KGgoAAAANS..."
      - success: "true" または "false"
    """
    image_data_url = request.form.get("image")
    success_str = request.form.get("success")

    if not image_data_url or not success_str:
        return jsonify({"error": "image or success missing"}), 400

    # 日時を使ったファイル名作成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

    # Base64部分抽出（data:image/png;base64,...）
    match = re.match(r"data:image/png;base64,(.*)", image_data_url)
    if not match:
        return jsonify({"error": "Invalid image data URL"}), 400

    image_base64 = match.group(1)

    # 画像の保存
    image_bytes = base64.b64decode(image_base64)
    image_filename = f"result_{timestamp}.png"
    image_path = os.path.join(RESULT_DIR, image_filename)
    with open(image_path, "wb") as f:
        f.write(image_bytes)

    # 成功判定の保存（true/falseテキストファイル）
    success_bool = success_str.lower() == "true"
    status_filename = f"result_{timestamp}.txt"
    status_path = os.path.join(RESULT_DIR, status_filename)
    with open(status_path, "w") as f:
        f.write(f"success: {success_bool}\n")

    return jsonify({"message": "Saved image and status", "image_file": image_filename, "success": success_bool})


if __name__ == "__main__":
    app.run(debug=True)
    
