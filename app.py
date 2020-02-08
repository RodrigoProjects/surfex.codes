from flask import Flask, render_template, request
import json
app = Flask(__name__)


@app.route('/scheduler')
def index():
    return '<h1>Hello World!!!</h1>'

@app.route('/getmsg/', methods=['GET'])
def respond():
    # Retrieve the name from url parameter
    name = request.args.get("name", None)

    # For debugging
    print(f"got name {name}")

    response = {}

    # Check if user sent a name at all
    if not name:
        response["ERROR"] = "no name found, please send a name."
    # Check if the user entered a number not a name
    elif str(name).isdigit():
        response["ERROR"] = "name can't be numeric."
    # Now the user entered a valid name
    else:
        response["MESSAGE"] = f"Welcome {name} to our awesome platform!!"

    # Return the response in json format
    return json.dumps(response)



if __name__ == "__main__":
    app.run(threaded=True,port=5000)