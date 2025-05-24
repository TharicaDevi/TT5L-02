from flask import Flask, render_template, request, redirect, url_for, session
import smtplib
import random
from email.message import EmailMessage

app = Flask(__name__)
app.secret_key = 'supersecretkey'

EMAIL_ADDRESS = 'elleyazmir@gmail.com'
EMAIL_PASSWORD = 'thqp rzyv fdne leer'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_email = request.form['email']
        session['user_email'] = user_email

        # Generate a 6-digit 2FA code
        code = str(random.randint(100000, 999999))
        session['2fa_code'] = code

        # Send email
        send_email(user_email, code)
        return redirect(url_for('verify'))

    return render_template('login.html')

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'POST':
        user_code = request.form['code']
        if user_code == session.get('2fa_code'):
            return "✅ 2FA Verified. Welcome!"
        else:
            return "❌ Invalid code."

    return render_template('verify.html')

def send_email(to_email, code):
    msg = EmailMessage()
    msg['Subject'] = 'Your 2FA Code'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = to_email
    msg.set_content(f'Your verification code is: {code}')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

if __name__ == '__main__':
    app.run(debug=True)