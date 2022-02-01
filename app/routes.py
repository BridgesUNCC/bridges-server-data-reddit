from app import app

@app.route('/')
def defaultroute():

    return "hi"