import flask
from flask import request, abort, Response
import json
from executor import Executor
from plots import Plotter, PlotterError


app = flask.Flask(__name__)

executor = Executor()
plotter = Plotter()


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Welcome to the REST service for SymPy</h1>
    '''


@app.route('/api/v1/custom', methods=['POST'])
def execute_custom():
    if not request.json:
        abort(400, "no json provided as the request body")
    method = request.json["method"]

    if 'method' not in request.json:
        abort(400, "no 'method' field found in the JSON")
    if 'args' not in request.json:
        abort(400, "no 'args' field found in the JSON")

    args = request.json["args"]
    result = executor.run_custom(method, args)
    return Response(json.dumps(result), mimetype="application/json")


@app.route('/api/v1/function', methods=['POST'])
def execute_function():
    if not request.json:
        abort(400, "no json provided as the request body")

    if 'method' not in request.json:
        abort(400, "no 'method' field found in the JSON")
    if 'args' not in request.json:
        abort(400, "no 'args' field found in the JSON")

    if 'params' in request.json:
        try:
            params = request.json['params']
        except:
            abort(400, "can't parse json:"+request.args['params'])
    else:
        params = dict()
    
    method = request.json["method"]
    args = request.json["args"]
    result = executor.run_function(method, args, params)
    return Response(json.dumps(result), mimetype="application/json")


@app.route('/api/v1/method', methods=['POST'])
def execute_method():
    if not request.json:
        abort(400, "no json provided as the request body")

    if 'method' not in request.json:
        abort(400, "no 'method' field found in the JSON")
    if 'object' not in request.json:
        abort(400, "no 'object' field found in the JSON")
    if 'args' not in request.json:
        abort(400, "no 'args' field found in the JSON")

    method = request.json["method"]
    obj = request.json["object"]
    args = request.json["args"]

    result = executor.run_method(obj, method, args)
    return Response(json.dumps(result), mimetype="application/json")


@app.route('/api/v1/plot', methods=['GET'])
def plot():
    if 'method' in request.args and 'args' in request.args:
        method = request.args['method']
        text_args = request.args['args']
        try:
            args = json.loads(text_args)
        except:
            abort(400, "can't parse json:"+text_args)
        if 'params' in request.args:
            try:
                params = json.loads(request.args['params'])
            except:
                abort(400, "can't parse json:"+request.args['params'])
        else:
            params = dict()
        try:
            fig = plotter.create_figure(method, args, params)
            checkOnly = 'checkOnly' in request.args
            if checkOnly:
                return Response(json.dumps({"ok": True, "result": True}), mimetype="application/json")
            else:
                svg = 'format' in request.args and request.args["format"] == "svg"
                output = plotter.fugure_to_image(fig,svg)
                if svg:
                    return Response(output.getvalue(), mimetype='image/svg+xml')
                else:
                    return Response(output.getvalue(), mimetype='image/png')     
        except PlotterError as e:
            return Response(json.dumps({"ok": False, "error": e.message, "errorCode": e.code}), mimetype="application/json")
    else:
        abort(400, "method and args are required arguments")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
