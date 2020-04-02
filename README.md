# math-processor
Simple REST service around [SymPy](https://sympy.org)

SymPy is a great library for symbolic mathematics. It aims to become a full-featured computer algebra system (CAS).

This project is a simple REST wrapper around SymPy, which allows calling most (but not all) SymPy functions via HTTP requests.

# What can it do?

The service allows:

* Calling any SymPy functions and methods on any math eхpression, parseable with SymPy.
* Getting results in SymPy expression language.
* Generating 2d and 3d plots and returning them in PNG or SVG format.
* Running several additional custom functionality. In particular:
   * Solving integrals step by step and providing the step by step solution.
   * Checking if two mathematical expressions are equivalent and, if yes telling which one is simpler.

# Installation 

The simplest way to run math-processor is using its [docker image](https://hub.docker.com/repository/docker/softaria/math-processor/)

```
docker run -d -p "80:5000" softaria/math-processor
```

Please replace 80 with a port where you want the service to run.

# Usage

There are following endpoints in the math-processor REST service:

1. /api/v1/method
2. /api/v1/function
3. /api/v1/plot
4. /api/v1/custom

Below we suppose the server is running at http://localhost:80

## Calling a method on SymPy object

URL: http://localhost:80/api/v1/method

Supported HTTP method: POST

Meaning: It calls the python method on the provided SymPy object (expression).

Body: JSON as following:
```
{
   "object":"{Sympy expression to be transformed to SymPy object. We will call method on this object.}"
   "method":"{name of python method to be called on the object (e.g. doit)}",
   "args":[{an array of arguments to be passed to the method (if any)}],
}
```

Result: either HTTP code 400 with the error explanation or JSON as following
```
{
 "ok": {"True" or "False"}
 "result": {Only exists if ok=True. Contains the execution result}
 "error: {Only exists if ok=False. Contains human-readable error description}
 "errorCode": {Only exists if ok=False. Contains error code (see below)}
}
```
Error codes:

* BAD_ARGUMENT - the provided object or some of the provided arguments can't be parsed as SymPy expression.
* METHOD_FAILURE - the call of the method failed.

In contrast to errors described in the response JSON that are useful in runtime, errors with HTTP code 400 mean the calling code must be fixed. In particular, they occur when you do not pass JSON body at all or when the JSON lacks one of its required fields.

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

You are allowed to run any method, supported by SymPy.

For example, here is JSON for rewriting tan(x) via sinuses.

```
{
  "method": "rewrite",
  "object":"tan(x)",
  "args": [
    "sin"
  ]
}
```

It is the equivalent of typing in python: Tan(x).rewrite(sin)

The result will be:

```
{
   "ok": true, 
   "result": "Mul(Integer(2), Pow(sin(Symbol('x')), Integer(2)), Pow(sin(Mul(Integer(2), Symbol('x'))), Integer(-1)))"
} 
```

## Calling a SymPy function

URL: http://localhost:80/api/v1/function

Supported HTTP method: POST

Meaning: It calls a function defined in 'sympy' module with the provided arguments (SymPy expressions)

Body: JSON as following:
```
{
   "method":"{name of a function from 'sympy' python module to call}",
   "args":[{an array of arguments to be passed to the function}],
}
```

Result: either HTTP code 400 with the error explanation or JSON as following
```
{
 "ok": {"True" or "False"}
 "result": {Only exists if ok=True. Contains the execution result}
 "error: {Only exists if ok=False. Contains human readable error description}
 "errorCode": {Only exists if ok=False. Contains error code (see below)}
}
```
Error codes:

* BAD_ARGUMENT - some of the provided arguments can't be parsed as SymPy expression.
* METHOD_FAILURE - the call of the function failed.

Example:

Let's call simplify(Pow(sin(x),2) + Pow(cos(x),2))

```
curl -d "@simplify.json" -X POST  -H "Content-Type: application/json" http://localhost:80/api/v1/function
```

simplify.json:

```
{
  "method": "simplify",
  "args": [
    "Pow(sin(x),2) + Pow(cos(x),2)"

  ]
}
```

The result:

```
{"ok": true, "result": "Integer(1)"}
```

## Generating a plot

URL: http://localhost:80/api/v1/plot

Supported HTTP method: GET

Meaning: It uses [SymPy plotting](https://docs.sympy.org/latest/modules/plotting.html) and [matplotlib](https://matplotlib.org/) to generate 2d, 3d and parametric plots.

Query parameters:

* method
* args
* params
* checkOnly
* format

### Method

It specifies what type of plot you want to get. In fact, it is the name of sympy plotting functions:

* plot
* plot_parametric
* plot3d
* plot3d_parametric_line
* plot3d_parametric_surface

The functions are described here: https://docs.sympy.org/latest/modules/plotting.html

### Args

Ags is a JSON array of SymPy expressions to plot. We have an array here as some of the plotting functions above require more than one mathematical function.

### Params

Optional parameter.

Params are plain key-value pairs formatted as JSON.
They are parsed and passed as the kwargs to corresponding SymPy plotting function (for details: https://docs.sympy.org/latest/modules/plotting.html). Its goal to pass all the additional parameters such as required plot size or its resolution.

### checkOnly

Optional parameter.

If present, the math-processor only checks if the passed arguments are valid and returns JSON formatted answer instead of the plot itself. Useful when your code wants to know if the plot was generated perfectly or if the plot image is broken because of error.

If passed, the result will be JSON as following:

```
{
 "ok": {"true" or "false"}
 "result": {Only exists if ok=true. Contains the execution result}
 "error: {Only exists if ok=false. Contains human readable error description}
 "errorCode": {Only exists if ok=False. Contains error code (see below)}
}
```

Where error codes are:

* BAD_ARGUMENT - at least one of the arguments can't be parsed
* BAD_METHOD - 'method' parameter does not equal to any of the supported values listed above
* METHOD_FAILURE - internal error occurs when the sympy plotting method was called


### format

Optional parameter.

If omitted or not equal to 'svg' then png format is used.
If equal to 'svg' the result is generated in SVG format.

### Example

```
   https://math-processor.math-editor.com/api/v1/plot?method=plot3d&args=["cos(Add(Abs(Symbol('x'))%2CAbs(Symbol('y'))))"]
```

the result is 

![3d plot](https://math-processor.math-editor.com/api/v1/plot?method=plot3d&args=["cos(Add(Abs(Symbol('x'))%2CAbs(Symbol('y'))))"] "3d plot")

# Calling custom methods

Besides calling SymPy built-in functions and methods, the math-processor has several manually coded functionality its authors found usable. For now it is:

* Ability to get step by step solution for integrals
* Ability to check if 2 expressions are equivalent
* Mirror method (see below for details)

URL: http://localhost:80/api/v1/custom

Supported HTTP method: POST

Body: JSON as following: 

```
{
  "method": "{name of custom method to call}",
  "args": [ {JSON array of expressions to pass to the custom method}  ]
}
```

Where the method is one of the following:

* integral_steps - calculate integral step by step and return the step by step solution
* equiv - check if two expressions are equivalent
* mirror - parse the provided expression and return its canonical SymPy form

If the custom method ends with error it returns following JSON:

The negative result is:

```
{
 "ok": "false"
 "error: {Contains human readable error description.}
 "errorCode": {Contains error code (see below).}
}
```

Error codes are:

* BAD_ARGUMENT - can't parse at least one of the passed expressions
* BAD_METHOD - no method for given name found
* METHOD_FAILURE - internal error occurred while executing the method

## Integral steps method

```
curl  -d "@integrate.json" -X POST  -H "Content-Type: application/json" http://localhost:80/api/v1/custom
```

where integrate.json is, for example:

```
{
  "method": "integral_steps",
  "args": [
    "exp(x) / (1 + exp(2 * x))",
    "Symbol('x')"
  ]
}
```

Look [here](https://docs.sympy.org/latest/modules/integrals/integrals.html#sympy.integrals.manualintegrate.integral_steps) for the result explanation.

## Checking equivalence

```
curl -d "@equiv.json" -X POST  -H "Content-Type: application/json" http://localhost:80/api/v1/custom
```

where equiv.json could be (note it must contain exactly two arguments):

```
{
  "method": "equiv",
  "args": [
    "Pow(sin(x),2) + Pow(cos(x),2)",
    "1"
  ]
}
```

The positive result is:

```
{ 
   "ok": true, 
   "result": 
           {
            "eq": "{eqivalency type}", 
            "si": "{which expression is simpler}"
           }
} 
```

where equivalency type is one of:

* identical - expressions are literally identical
* equiv - expressions become equal when you do some algebra transformation
* equivCalc - expression become equal only if you apply calculus transformation (like integrating, differentiating or calculating limit)
* different - expressions are not equivalent

the value of "si" could be one of the following:

* first - you have to simplify the second expression more than the first in order to make them identical.
* second - you have to simplify the first expression more than the second in order to make them identical.
* none - returned when the expressions are identical.
* unknown - you have to simplify both expressions to make them identical and these simplifications are both algebraic or both calulus.


## Mirroring

```
curl -d "@mirror.json" -X POST  -H "Content-Type: application/json" http://localhost:80/api/v1/custom
```

where mirror.json could be:

```
{
  "method": "mirror",
  "args": [
    "Pow(sin(x),2) + Pow(cos(x),2)"
  ]
}
```

It returns canonical SymPy form of the given expression. Or reports an error.

E.g. for the exression given above the answer is:

```
{"ok": true, "result": "Add(Pow(sin(Symbol('x')), Integer(2)), Pow(cos(Symbol('x')), Integer(2)))"}
```

# Playground

The math-processor is integrated with our math-editor. 
So, you can try its calculating and plotting functionality here

https://math-editor.com/integrationsDemo.html
