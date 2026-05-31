from app import create_app

app = create_app()

@app.route('/')
def home():
    return "✅ Travelo Backend is Running!"

if __name__ == '__main__':
    app.run(debug=True, port=5000)