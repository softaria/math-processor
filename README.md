# math-processor
Simple REST service around [SymPy](https://sympy.org)

SymPy is a great library for symbolic mathematics. It aims to become a full-featured computer algebra system (CAS).

This project is a simple REST wrapper around SymPy, which allows calling most (but not all) SymPy functions via HTTP requests.

# Installation 

The simplest way to run math-processor is using its [docker image](https://hub.docker.com/repository/docker/softaria/math-processor/)

```
docker run -d -p "80:5000" softaria/math-processor
```

Please replace 80 with a port where you want the service to run.

# Usage

There are following end points in the math-processor REST service:

1. /api/v1/method
2. /api/v1/function
3. /api/v1/plot
4. /api/v1/custom

Below we suppose the server is running at http://localhost:80

## Calling a method on SymPy object

URL: http://localhost:80/api/v1/method

Supported HTTP method: POST

Meaning: It calls python methon on the provided SymPy object (expression).

Body: json as following:
```
{
   "object":"{Sympy expression to be transformed to SymPy object. We will call method on this object.}"
   "method":"{name of python method to be called on the object (e.g. doit)}",
   "args":[{an array of arguments to be passed to the method (if any)}],
}
```

Result: either HTTP code 400 with the error explanation or json as following
```
{
 "ok": {"True" or "False"}
 "result": {Only exists if ok=True. Contains the exection result}.
 "error: {Only exists if ok=False. Conains human readable error description.
 "errorCode": {Only exists if ok=False. Contains error code (see below).
}
```
Error codes:

BAD_ARGUMENT - the provoded object can't be parsed as SymPy expression.
METHOD_FAILURE - the call of the method failed.

In contrast to errors described in the response json that are useful in runtime, errors with HTTP code 400 means the calling code must be fixed. In particular they occur when you do not pass json body at all or when the json lacks one of ith required fields.

Example:

Let's call method doit() on SymPy expression Integral(Mul(Integer(2),Symbol('x')),(Symbol('x'),Integer(0),Integer(1)))

Let's do it with [curl](https://curl.haxx.se/)

```
curl -d "@doit.json" -X POST  -H "Content-Type: application/json" http://localhost:80/api/v1/method
```

where doit.json contains following:

```
{"method":"doit","args":[],"object":"Integral(Mul(Integer(2),Symbol('x')),(Symbol('x'),Integer(0),Integer(1)))"}
```

The result will be:

```
{"ok": true, "result": "Integer(1)"}
```

You can try it yourself without installing the math-processor. Just use one installed at https://math-processor.math-editor.com

You are allowed to run any method, supportd by SymPy.

For example here is a jon for rewriting tan(x) in term of sinuses.

```
{
  "method": "rewrite",
  "object":"tan(x)",
  "args": [
    "sin"
  ]
}
```

where result will be:

```
{
   "ok": true, 
   "result": "Mul(Integer(2), Pow(sin(Symbol('x')), Integer(2)), Pow(sin(Mul(Integer(2), Symbol('x'))), Integer(-1)))"
} 
```

