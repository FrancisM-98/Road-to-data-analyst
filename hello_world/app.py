from flask import Flask, request, redirect

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <h1>🌍 Hello World!</h1>
    <p>Welcome to my Flask app. Try these pages:</p>
    <a href="/about"><button>About</button></a>
    <a href="/contact"><button>Contact</button></a>
    <a href="/ask"><button>What's your name?</button></a>
    """


@app.route("/about")
def about():
    return """
    <h1>📖 About</h1>
    <p>This is the About page. I'm learning Flask!</p>
    <a href="/"><button>← Back to Home</button></a>
    """


@app.route("/contact")
def contact():
    return """
    <h1>📬 Contact</h1>
    <p>Contact me at: francis@example.com</p>
    <a href="/"><button>← Back to Home</button></a>
    """


@app.route("/ask", methods=["GET", "POST"])
def ask_name():
    if request.method == "POST":
        name = request.form["name"]
        return redirect(f"/hello/{name}")
    return """
    <h1>👋 What's your name?</h1>
    <form method="POST">
        <input type="text" name="name" placeholder="Type your name..." required>
        <button type="submit">Say Hello!</button>
    </form>
    <br>
    <a href="/"><button>← Back to Home</button></a>
    """


@app.route("/hello/<name>")
def greet(name):
    return f"""
    <h1>🎉 Hello, {name}!</h1>
    <p>Welcome to my Flask app!</p>
    <a href="/ask"><button>Try another name</button></a>
    <a href="/"><button>← Back to Home</button></a>
    """


if __name__ == "__main__":
    app.run(debug=True)
