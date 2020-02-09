from flask import Flask, render_template, request, jsonify
from um_schedule_api import *

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False # Garant utf-8

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


@app.route('/schedule/', methods=['GET'])
def schedule():

    curso = request.args.get('curso')
    ano = request.args.get('ano')

    print(f'{curso} - {ano}')
    if not curso or not ano:
        return jsonify({'error': 'Argumento ano ou curso em falta!'})


    try:
        ano = int(request.args.get('ano'))

    except Exception:
        return jsonify({'erro' : 'Ano tem de ser um número inteiro!'})

    try:
        api = UM_Schedule_API()
        return jsonify(api.get(CURSO = curso,ANO = ano))

    except Exception as e:
        return jsonify({'erro' : 'Ano ou curso não existente!', 'trace' : e.args})

    finally:
        del api
    

if __name__ == "__main__":
    app.run(threaded=True,port=5000,debug=True)