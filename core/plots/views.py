from django.views.generic import TemplateView
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import (Input, Output)
import plotly.graph_objs as go

from django_plotly_dash import DjangoDash

app = DjangoDash('SimpleExample')


class HomeView(TemplateView):
    template_name = "index.html"
