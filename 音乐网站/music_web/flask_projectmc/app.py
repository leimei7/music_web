from APP import create_app#导入构造app的函数
import os
from datetime import timedelta

app=create_app()
app.secret_key = os.urandom(24)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=20)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')