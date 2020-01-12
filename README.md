# Flask and Bokeh on Heroku

This is a TDI project is intended to help you tie together some important concepts and
technologies from the 12-day course, including Git, Flask, JSON, Pandas, Requests, Heroku, and Bokeh for visualization. The provided repository contains a basic template for a Flask configuration that will
work on Heroku. The instructions in the original READM.md (and the linked tutorials) left out a lot of details as well as corner cases in building and deploying the app. Thus this note summarizes the issues that I encountered and the tricks that address them.



A [finished demo example](https://kcguan-tdi-demo2.herokuapp.com/) that demonstrates some basic functionality.

## Step 1: Setup and deploy
* Git clone the existing template repository.
* If one chooses to builds up an app from scratch, after testing the build application in Spyder or terminal:
 - `git init .`
 - `git add . `
 - `git commit -m "Demo" `
* There are some boilerplate HTML in `templates/`, the useful HTML files are `index.html` and  `plot.html`
* `Procfile`, `requirements.txt`, `conda-requirements.txt`, and `runtime.txt`
  contain some default settings.
  - Be very careful with the version of the packages in requirements.txt. For example, I use version 0.12.10 of Bokeh (src="https://cdn.pydata.org/bokeh/release/bokeh-0.12.10.min.js"), so I make sure `bokeh==0.12.10` in the `requirement.txt`, to avoid potential issues caused by version mismatch.
* Create Heroku application with `heroku create <app_name>` or leave blank to
  auto-generate a name.
*  `heroku git:remote -a <app_name>` is needed if the app is build from scratch (not cloned from a repository)
- (Suggested) Use the [conda buildpack](https://github.com/thedataincubator/conda-buildpack).
  If you choose not to, put all requirements into `requirements.txt`. 
  `heroku config:add BUILDPACK_URL=https://github.com/thedataincubator/conda-buildpack.git#py3`

  The advantages of conda include easier virtual environment management and fast package installation from binaries (as compared to the compilation that pip-installed packages sometimes require).
  One disadvantage is that binaries take up a lot of memory, and the slug pushed to Heroku is limited to 300 MB. Another note is that the conda buildpack is being deprecated in favor of a Docker solution (see [docker branch](https://github.com/thedataincubator/flask-framework/tree/docker) of this repo for an example).
  **I choose to put all requirements into `requirements.txt`. The suggested configuration does not work for me. There could be version compatibility issues ? **
  
* Deploy to Heroku: `git push heroku master`
* Test the app locally first `heroku local`. The go to `http://localhost:5000/`
* You should be able to see your site at `https://<app_name>.herokuapp.com`
* A useful reference is the Heroku [quickstart guide](https://devcenter.heroku.com/articles/getting-started-with-python-o).

## Step 2: Get data from API and put it in pandas
* Use the `requests` library to grab some data from a public API. This will
  often be in JSON format, in which case `simplejson` will be useful.
* Build in some interactivity by having the user submit a form which determines which data is requested.
* Create a `pandas` dataframe with the data.

Here I use Quandl API calls to pull the prices time series of last `str_days` number of days, with `str_days` as an input submitted from `index.html` 

```
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
``` 

Note here is an example of JSON output. Be careful with JSON data hierarchy.

```
{'dataset': {'collapse': None,
  'column_index': None,
  'column_names': ['Date', 'Value'],
  'data': [['2020-01-06', 63.27],
   ['2020-01-03', 63.0],
   ['2020-01-02', 61.17],
   ['2019-12-31', 61.14]],
  'database_code': 'EIA',
  'database_id': 661,
  'dataset_code': 'PET_RWTC_D',
  'description': 'Series ID: PET.RWTC.D<br><br>Units: Dollars per Barrel. Cushing, OK WTI Spot Price FOB',
  'end_date': '2020-01-06',
  'frequency': 'daily',
  'id': 11835659,
  'limit': 4,
  'name': 'Cushing, OK WTI Spot Price FOB, Daily',
  'newest_available_date': '2020-01-06',
  'oldest_available_date': '1986-01-02',
  'order': None,
  'premium': False,
  'refreshed_at': '2020-01-12T13:42:11.447Z',
  'start_date': '1986-01-02',
  'transform': None,
  'type': 'Time Series'}}
```

Also, `x = to_datetime(df['Date'])` is necessary to convert string to Pandas datetime format.

## Step 3: Use Bokeh to plot pandas data
* Create a Bokeh plot from the dataframe.
* Consult the Bokeh [documentation](http://bokeh.pydata.org/en/latest/docs/user_guide/embed.html)
  and [examples](https://github.com/bokeh/bokeh/tree/master/examples/embed).
* Make the plot visible on your website through embedded HTML or other methods - this is where Flask comes in to manage the interactivity and display the desired content.
* Some good references for Flask: [This article](https://realpython.com/blog/python/python-web-applications-with-flask-part-i/), especially the links in "Starting off", and [this tutorial](https://github.com/bev-a-tron/MyFlaskTutorial).
* **Most instructions and online tutorials overlooked the following two very important aspects in Bokeh:**
 - `{{ script | safe }} {{ div | safe }}` `|safe` is absolutely necessary, otherwise, Bokeh has difficulty updating new plots (with new submitted input)

 - In `plot.html`, use `https` instead of `http` for linking CSS and Javascript. Otherwise, Heroku will not display the plot. The following is the example:
 
 ```
 <link
    href="https://cdn.pydata.org/bokeh/release/bokeh-0.12.10.min.css"
    rel="stylesheet" type="text/css"
>
<script 
    src="https://cdn.pydata.org/bokeh/release/bokeh-0.12.10.min.js"
></script>
```