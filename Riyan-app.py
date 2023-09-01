from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.exchange-rates.org/exchange-rate-history/usd-idr')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('table', attrs={"class":"history-rates-data"})
row = table.find_all("a", attrs={"class":"n"})

row_length = len(row)

temp = [] #initiating a list 

for i in range(0, row_length):

    #get periode
    period = table.find_all('a', attrs={'class':'n'})[i].text
    
    #get dollar
    dollar = table.find_all('span', attrs={'class':'n'})[i].text
    dollar = dollar.strip()
    
    #get rupiah
    #rupiah = table.find_all('span', attrs={'class':'w'})[i].text
    #rupiah = rupiah.strip()
    
    temp.append((period, dollar))

temp = temp[::-1]

#change into dataframe
df_ryn = pd.DataFrame(temp, columns = ('period', 'dollar'))

#insert data wrangling here
df_ryn['period'] = df_ryn['period'].astype('datetime64[ns]')
df_ryn['dollar'] = df_ryn['dollar'].str.replace('$1 = Rp', '')
df_ryn['dollar'] = df_ryn['dollar'].str.replace(',', '')
df_ryn['dollar'] = df_ryn['dollar'].astype('int64')
df_ryn = df_ryn.set_index('period')

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df_ryn["dollar"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = df_ryn.plot(figsize = (20,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)