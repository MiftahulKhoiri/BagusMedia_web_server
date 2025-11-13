from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    # pastikan instance dir ada
    instance_dir = os.path.join(os.path.dirname(__file__), "instance")
    os.makedirs(instance_dir, exist_ok=True)

    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)