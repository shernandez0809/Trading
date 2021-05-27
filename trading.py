# -*- coding: utf-8 -*-
"""
Created on Tue May  4 14:17:27 2021

@author: SHernandez
"""
import os
import json
import  pandas as pd 
from numpy import where
from flask import Flask, jsonify, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import render_template

#from flask_jsonpify import jsonpify
UPLOAD_FOLDER = os.getcwd()
ALLOWED_EXTENSIONS = {'csv'}




app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



def calcular( file ,cmp, vnd, stop):
    """  variable de stop-loss y  strategy"""
    stop='-0.67'
    cmp='-1.00'
    vnd='-4.00'
    
    """lectura de archivo csv"""
    df1=pd.read_csv( file ,sep=",",header=None,names=['Fecha','Hora','Open','High','low','Close'])
    
    """creacion de un nuevo dataframe para sacar la pertura y cierre por la hora de apertura de cada dia"""
    df2=df1[(df1.Hora ==930)]
    df2.drop(['Hora','High','low'],axis=1,inplace=True)
    df2.rename(columns={'Open':'Apertura','Close':'Cierre'},inplace=True)
    df=pd.merge(df1, df2, how='inner',on=['Fecha','Fecha'])
    """ estrateia de compra"""
    df['apertura%']=(((df.Open/df.Apertura)-1)*100).round(0)
    df['apertura%'] =pd.Series(["{0:.2f}".format(val) for val in df['apertura%']], index = df.index)
    df['Buy']=where(((df['apertura%']==stop) | (df['apertura%']==cmp )),'compro',0)
    """ estrategia de  venta"""
    df['cierre%']=(((df.Open/df.Cierre)-1)*100).round(0)
    df['cierre%'] =pd.Series(["{0:.2f}".format(val) for val in df['cierre%']], index = df.index)
    df['Sell']=where(df['cierre%']==vnd,'vendo',0)
    """ creacion de nuevo dataframe para conocer cuantas veces existe la estrategia compra y venta """
    
    df3=df[(df.Buy =='compro')]
    df4=df[(df.Sell =='vendo')]
    buy=len(df3)
    sell=len(df4) 
    
    result = df.to_json(orient="split")
    parsed = json.loads(result)
    return jsonify(parsed)


@app.route('/',methods=["POST"])
def trading():   
    #return render_template('trading.html',tables=[df.to_html(classes='table table-striped')], titles=df.columns.values)
    if 'file' not in request.files:
        return jsonify( [  "Falta el archivo" ])
        
    file = request.files.get('file')
    if file.filename == '':
        return jsonify(["Falta el archivo"] )
    
    stop = request.values.get('stop')
    
    cmp = request.values.get('cmp')
    vnd = request.values.get('vnd')

    
    return calcular(file, cmp,vnd, stop)


        
        
    
if __name__ == '__main__':
    app.run()
