# -*- coding: utf-8 -*-
"""
Created on Tue May  4 14:17:27 2021

@author: SHernandez
"""
import  pandas as pd 
from numpy import where
from flask import Flask
from flask import render_template
from flask_jsonpify import jsonpify


app = Flask(__name__)


"""  variable de stop-loss y  strategy"""
stop='-0.67'
cmp='-1.00'
vnd='-4.00'

"""lectura de archivo csv"""
df1=pd.read_csv("C:\\Users\\shernandez.LAFABRICA\\.spyder-py3\\UNG_Trading.csv",sep=",",header=None,names=['Fecha','Hora','Open','High','low','Close'])

"""creacion de un nuevo dataframe para sacar la pertura y cierre por la hora de apertura de cada dia"""
df2=df1[(df1.Hora ==930)]
df2.drop(['Hora','High','low'],axis=1,inplace=True)
df2.rename(columns={'Open':'Apertura','Close':'Cierre'},inplace=True)
df=pd.merge(df1, df2, how='inner',on=['Fecha','Fecha'])
""" estrateia de compra"""
df['apertura%']=(((df.Open/df.Apertura)-1)*100).round(0)
df['apertura%'] =pd.Series(["{0:.2f}".format(val) for val in df['apertura%']], index = df.index)
df['Buy']=where(((df['apertura%']==stop) | (df['apertura%']==cmp )),1,0)
""" estrategia de  venta"""
df['cierre%']=(((df.Open/df.Cierre)-1)*100).round(0)
df['cierre%'] =pd.Series(["{0:.2f}".format(val) for val in df['cierre%']], index = df.index)
df['Sell']=where(df['cierre%']==vnd,-1,0)

"""columna estatus para venta y/o compra"""
df['status']=where ((df['Buy'] ==1) & (df['Sell']==-1),2,0)
df['status']=where ((df['Buy'] ==1) & (df['Sell']==0),1,0)
df['status']=where ((df['Buy'] ==0) & (df['Sell']==-1),-1,df['status'])


""" creacion de nuevo dataframe para conocer cuantas veces existe la estrategia compra y venta """
df3=df[(df.Buy =='compro')]
df4=df[(df.Sell =='vendo')]
buy=len(df3)
sell=len(df4) 


@app.route('/')
def trading():   
    return render_template('trading.html',tables=[df.to_html(classes='table table-striped')], titles=df.columns.values)

if __name__ == '__main__':
    app.run()
