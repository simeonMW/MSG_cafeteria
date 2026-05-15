from app import create_app
from app.config import Config

if __name__ == "__main__":
    app = create_app()
    # host='0.0.0.0' allows mobile apps in the local Malawian network to connect.
    app.run(host='0.0.0.0', port=5000, debug=Config.DEBUG)