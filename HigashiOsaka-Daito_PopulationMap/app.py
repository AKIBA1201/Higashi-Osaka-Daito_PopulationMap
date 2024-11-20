# app.py

from dash import Dash
import webbrowser
from threading import Timer
import logging
import socket

# ログの設定
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(message)s')

# アプリケーションの初期化
app = Dash(__name__)

# 他のファイルからレイアウトとコールバックをインポート
from layout import layout
from callbacks import register_callbacks

# アプリのレイアウトを設定
app.layout = layout

# コールバック関数の登録
register_callbacks(app)

# ローカルIPアドレスの取得
def get_local_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

# サーバー起動設定
if __name__ == '__main__':
    port = 8049  # ポート番号を設定
    local_ip = get_local_ip()
    Timer(1, lambda: webbrowser.open(f'http://{local_ip}:{port}')).start()
    try:
        logging.info(f"Dash is running on http://{local_ip}:{port}/")
        print(f"Dash is running on http://{local_ip}:{port}/")
        app.run_server(host='0.0.0.0', port=port, debug=True, use_reloader=False)
    except OSError as e:
        logging.error(f"サーバー起動エラー: {e}")
        print(f"サーバー起動エラー: {e}")
        logging.info("別のポート番号を試してください。")
        print("別のポート番号を試してください。")
