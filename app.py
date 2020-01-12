from flask import Flask, render_template, request, redirect
import numpy as np
#import quandl
import requests

from pandas import DataFrame, Series, to_datetime
#import datetime as dt
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.models.annotations import Title
from bokeh.io import output_file, show, reset_output
from bokeh.models import ColumnDataSource, DatetimeTickFormatter


key = "wFQ1oxYtmjs-EFN68gCn"

#def get_quandl_py(days):
#    
#    # Use Quandl python interface
#    
#    quandl.ApiConfig.api_key = key
#    data = quandl.get("EIA/PET_RWTC_D", rows = days)
#    data.reset_index(inplace = True)
#    x = data.Date
#    y = data.Value
#
#    return x, y



def get_quandl(str_days):
    
   # Use Quandl API calls
   reqURL = "https://www.quandl.com/api/v3/datasets/EIA/PET_RWTC_D.json?" \
        +"limit=" + str_days\
        +"&api_key=" + key
   r=requests.get(reqURL)
   data = r.json()['dataset']['data']
   col_names = r.json()['dataset']['column_names']
   df = DataFrame(data, columns = col_names)
   x = to_datetime(df['Date'])
   y = df['Value']
   
   return x, y

def make_figure(x, y):
    
    # Plot time series (prices)
    
    p=figure(x_axis_type="datetime", width=1200, height=600)
  
    t = Title()
    t.text = 'Price'
    p.circle(x, y, size=10, color='red', legend='Price')
    p.line(x, y, color='blue')
    p.xaxis.formatter=DatetimeTickFormatter(
        hours=["%d %B %Y"],
        days=["%d %B %Y"],
        months=["%d %B %Y"],
        years=["%d %B %Y"],
    )
    p.xaxis.major_label_orientation = np.pi/4
    p.grid.grid_line_alpha=0.4
    p.xaxis.axis_label = 'Date'
    p.yaxis.axis_label = 'Price'
    p.title = t
  
    output_file('plot.html')
    script, div=components(p)
    
    return(script, div)


app = Flask(__name__)

@app.route('/')
def main():
	return redirect('/index')

@app.route('/index', methods=['GET','POST'])
def index():
  return render_template('index.html')

@app.route('/plot_figure', methods=['POST'])
def plot_figure():
    
    day_str=request.form['dayText']
    x,y = get_quandl(day_str)
    
    script,div = make_figure(x,y)
    return render_template('plot.html', script=script, div=div)

 	
if __name__ == '__main__':
 	app.run(port=33507)


