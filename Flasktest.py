from flask import Flask, redirect, url_for, request
app = Flask(__name__)


@app.route('/success/<name>')
def success(name):
    return 'welcome %s' % name
@app.route('/fail')
def fail():
    return 'Wrong password ' 


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        user = request.form['username']
        pword = request.form['pw']
        if pword == "123":
            return redirect(url_for('success', name=user))
        else:
            return redirect(url_for('fail'))
    


if __name__ == '__main__':
    app.run(debug=True)