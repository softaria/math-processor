from matplotlib.figure import Figure
from sympy.parsing.sympy_parser import parse_expr
from sympy.plotting import plot, plot3d, plot_parametric, plot3d_parametric_line, plot3d_parametric_surface
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.backends.backend_svg import FigureCanvasSVG
from sympy.plotting.plot import Plot
import sys
from enum import Enum
import io


class ErrorCode(str, Enum):
    BAD_ARG = "BAD_ARGUMENT",
    BAD_METHOD = "BAD_METHOD",
    METHOD_FAILURE = "METHOD_FAILURE",


class PlotterError(Exception):
    def __init__(self, message: str, code: ErrorCode):
        self.message = message
        self.code = code


class Plotter:
    def __init__(self):
        self.plotters = {
            "plot": lambda args, params: plot(*args, **params),
            "plot_parametric": lambda args, params: plot_parametric(*args, **params),
            "plot3d": lambda args, params: plot3d(*args, **params),
            "plot3d_parametric_line": lambda args, params: plot3d_parametric_line(*args, **params),
            "plot3d_parametric_surface": lambda args, params: plot3d_parametric_surface(*args, **params),
        }

    def create_figure(self, method: str, args: [], params: dict)->Figure:
        if method in self.plotters:
            plotter = self.plotters[method]
            parsed_args = []
            for arg in args:
                try:
                    parsed_args.append(parse_expr(arg, evaluate=False))
                except:
                    raise PlotterError(
                        "Can't parse argument "+arg + " because of "+str(sys.exc_info()[1]), ErrorCode.BAD_ARG)
            # set show to False as it is MUST
            params["show"] = False
            try:
                p = plotter(parsed_args, params)
                be = p.backend(p)
                be.process_series()
                return be.fig
            except:
                raise PlotterError(
                    str(sys.exc_info()[1]), ErrorCode.METHOD_FAILURE)
        else:
            raise PlotterError("unsupported method", ErrorCode.BAD_METHOD)

    def fugure_to_image(self, fig: FigureCanvasSVG, svg: bool)->io.BytesIO:
        output = io.BytesIO()
        if svg:
            FigureCanvasSVG(fig).print_svg(output)
        else:
            FigureCanvasAgg(fig).print_png(output)
        return output
