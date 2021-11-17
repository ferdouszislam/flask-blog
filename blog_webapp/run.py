from blog_webapp import app

# these two lines of code lets you run with 'python run.py'
# instead of 'flask run' and setting debug mode True everytime
if __name__ == '__main__':
    app.run(debug=True)
