from flask import Flask, request, redirect, url_for, session, flash, render_template_string

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Hardcoded user login info
USER = {
    'username': 'admin',
    'password': '1234'
}

login_html = """
<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
    <h2>Login</h2>
    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        <ul>
          {% for category, message in messages %}
            <li style="color: {{ 'red' if category == 'danger' else 'green' }}">{{ message }}</li>
          {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}
    <form method="POST" action="/login">
        <label>Username:</label><br>
        <input type="text" name="username"><br><br>
        <label>Password:</label><br>
        <input type="password" name="password"><br><br>
        <input type="submit" value="Login">
    </form>
</body>
</html>
"""

@app.route('/')
def home():
    if 'user' in session:
        return f"Hello, {session['user']}! <br><a href='/logout'>Logout</a>"
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == USER['username'] and password == USER['password']:
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template_string(login_html)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)