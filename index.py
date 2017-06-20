from flask import Flask, render_template
app = Flask(__name__, static_url_path = "", static_folder = "tmp")

import proc

@app.route("/")
def main():
    proc.to_html()
    return render_template('data.html')

if __name__ == '__main__':
    app.run(debug=True)