#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
from web import form
from mako.template import Template
import anydbm
import os.path
import pymongo
import feedparser
import urllib
import datetime
from time import time
import tweepy

web.config.debug = False
       
urls = (
	'/editar', 'editar',
	'/final', 'final',
    '/', 'init',
    '/registro','registro',
    '/log', 'log',
    '/pags','pags',
    '/out','out',
    '/noticia','noticia',
    '/noticia2','noticia2',
    '/editargrafico','editargrafico',
    '/vergrafico','vergrafico',
    '/borrargrafico','borrargrafico',
    '/multimedia','multimedia',
    '/maps','maps',
    '/twitter','twitter'
)

app = web.application(urls, locals())
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'usuario':'','pagina':'','pagantes':'','time':'','tweet':''})


login = form.Form(form.Textbox('Nombre',form.notnull),
				  form.Textbox('Apellidos',form.notnull),
				  form.Textbox('DNI',form.notnull),
				  form.Textbox('email',form.notnull,form.regexp('^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,4}$','correo no valido')),
				  form.Dropdown('dia_nacimiento', [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31], description="Dia de nacimiento"), 
				  form.Dropdown('mes_nacimiento', ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'], description=" mes de nacimiento"),
				  form.Dropdown('anio_nacimiento', [1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,2005], description ="anio de nacimiento"),
				  form.Textarea('direccion',form.notnull),
				  form.Radio('FormaPago', ['Contra reembolso', 'tarjeta VISA'],form.notnull, description="Forma de pago: "),
				  form.Textbox('NumeroVISA', form.notnull, form.regexp('[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]', 'num VISA incorrecto')),
				  form.Checkbox('check', form.Validator("Acepta las clausulas", lambda i: "check" not in i), description="Aceptacion clausulas de contrato"),
				  form.Password('Contrasenia',form.notnull),
				  form.Password('valida_clave', form.notnull, description="Repita la clave"),
				  form.Button('Login'),
				  validators=[form.Validator("La contrasenia no coincide", lambda i: i.Contrasenia == i.valida_clave),
				  form.Validator("Tamanio minimo 7 en contrasenia", lambda i: len(str(i.Contrasenia)) >=7 ),
				  form.Validator("fecha nacimiento incorecta", lambda i: i.mes_nacimiento=="enero" or i.mes_nacimiento=="marzo" or i.mes_nacimiento=="mayo" or i.mes_nacimiento=="julio" or i.mes_nacimiento=="agosto" or i.mes_nacimiento=="octubre" or i.mes_nacimiento=="diciembre" or (i.mes_nacimiento=="abril" and int(i.dia_nacimiento) < 31) or (i.mes_nacimiento=="junio" and int(i.dia_nacimiento) < 31) or (i.mes_nacimiento=="septiembre" and int(i.dia_nacimiento) < 31) or (i.mes_nacimiento=="noviembre" and int(i.dia_nacimiento) < 31) or (i.mes_nacimiento=="febrero" and int(i.dia_nacimiento) < 29) or (i.mes_nacimiento=="febrero" and int(i.anio_nacimiento) % 4 == 0 and int(i.dia_nacimiento) < 30))]
				  )
				  
login2 = form.Form(form.Button('Editar'))		
		  

login3 = form.Form (
	form.Textbox ('Nombre', form.notnull, description='Usuario:'),
	form.Password ('Contrasenia', form.notnull, description='Contrasenia:'),
	form.Button ('Login'))

login4 = form.Form(form.Button('LogOut'))	

login5 = form.Form(
	form.Textbox ('noticia', form.notnull, description='¿Que noticia deseas leer?'),
	form.Button ('Buscar'))
	
login6 = form.Form(
	form.Textbox ('noticia', form.notnull, description='Busque la noticia por terminos: '),
	form.Button ('Buscar'))
	
login7= form.Form(
	 form.Dropdown('ciudad', ['granada','priego','cordoba','malaga','jaen','huelva','cadiz'], description="¿De que ciudad quiere ver tweets?"),
	form.Button ('Buscar'))
	
graficologin = form.Form (
    form.Textbox('etiqueta', form.notnull, description='etiqueta:'),
    form.Textbox('valor', form.notnull, description='valor:'),
    form.Button ('Incluir'),
)

mapslogin = form.Form (
	form.Textbox('origen', form.notnull, description='origen: '),
	form.Textbox('destino', form.notnull, description='destino: '),
	form.Button('Enviar'))

class init:
	
	def GET(self):
		
		if session.time == '':
			t = time()
			session.time = t 
			
		t2 = time()
		tiempo2 = int(t2)
		tiempo = int(session.time) + 600
		print session.time
		print tiempo2
		
		if tiempo >= tiempo2:
			web = urllib.urlretrieve('http://ep00.epimg.net/rss/elpais/portada.xml')
			f = open(web[0],'r')
			f2 = open('elpais.xml','w')
			t = time()
			session.time = t
			f2.write(f.read())
			f2.close()
		
		d = feedparser.parse('elpais.xml')
		rss_portada = d['feed']['title']	
		
		tam = len(d.entries)
		pos = 0
		rss = []
		while pos < tam:
			rss.append(d.entries[pos].title)
			pos = pos + 1
		
				
		foto = d.feed.image.href
		web = urllib.urlretrieve(foto)
		f = open(web[0],'r')
		f2 = open('static/foto.png','w')
		f2.write(f.read())
		f2.close()
		
		form = login5()	
		form2 = login6()
		
		mytemplate=Template(filename='index.html')
		session.pagina = ''
		return mytemplate.render(rss_portada=rss_portada, rss=rss, form=form, form2=form2)
		
class multimedia:
	
	def GET(self):
		mytemplate=Template(filename='multimedia.html')
		session.pagina = 'multimedia'
		return mytemplate.render()
		
class noticia:
	
	def POST(self):
		fb = login5()
		
		if not fb.validates():
			mytemplate=Template(filename='index.html')
			return mytemplate.render(fb=fb)
		else:
			num = fb.d.noticia
			numnoticia = int(num)
			numnoticia = numnoticia - 1
		
			
			d = feedparser.parse('elpais.xml')
			titulo = d.entries[numnoticia].title
			ent = d.entries[numnoticia].content[0].value
			fotop = d.entries[numnoticia].enclosures[0].href
			
			
			mytemplate=Template(filename='noticia.html')
			return mytemplate.render(titulo=titulo,ent=ent,fotop=fotop)
			
class noticia2:
	
	def POST(self):
		fb = login6()
		
		if not fb.validates():
			mytemplate=Template(filename='index.html')
			return mytemplate.render(fb=fb)
		else:
			noti = fb.d.noticia
			
			d = feedparser.parse('elpais.xml')
			
			tam = len(d.entries)
			pos = 0
			while pos < tam:
				if noti in d.entries[pos].title:
					titulo = d.entries[pos].title
					ent = d.entries[pos].content[0].value
					fotop = d.entries[pos].enclosures[0].href
					mytemplate=Template(filename='noticia.html')
					return mytemplate.render(titulo=titulo,ent=ent, fotop=fotop)
					
				else:
					pos = pos + 1
			
			titulo = 'Noticia no encontrada'
			ent = 'Pruebe buscando otro término'
			fotop=0
			mytemplate=Template(filename='noticia.html')
			return mytemplate.render(titulo=titulo,ent=ent,fotop=fotop)
				
						  
class registro:        
    
	def GET(self):
		fa = login()
		
		mytemplate=Template(filename='reg.html')
		return mytemplate.render(form=fa)
		

	def POST(self):
		
		form = login()
		
		if not form.validates():
			mytemplate=Template(filename='reg.html')
			return mytemplate.render(form=form)
		else:
			
			try:
				conn=pymongo.MongoClient()
			except pymongo.errors.ConnectionFailure, e:
				print "Could not connect to MongoDB: %s" % e 
			
			
			db = conn['usuarios']
			collection = db.my_collection
				
			doc = {'usuario': form.d.Nombre, 'apellidos': form.d.Apellidos, 'DNI': form.d.DNI, 'email': form.d.email, 'fecha_nacimiento': form.d.dia_nacimiento+'/'+form.d.mes_nacimiento+'/'+form.d.anio_nacimiento, 'direccion': form.d.direccion, 'pago': form.d.FormaPago, 'visa': form.d.NumeroVISA, 'password': form.d.Contrasenia}

			collection.insert(doc)
			
			session.usuario = form.d.Nombre
			session.pagina = 'registro'	
			session.pagantes = ''
			fu=login4()
			f2=login2()
			consulta = list(db.my_collection.find({"usuario": form.d.Nombre}))
			mytemplate=Template(filename='prueba.html')
			return mytemplate.render(consulta=consulta, form=f2,fu=fu)


class log:
	
	def GET(self):
		form = login3()
		mytemplate=Template(filename='log.html')
		return mytemplate.render(form=form)
	
	def POST(self):
		
		form = login3()
		
		if not form.validates():
			mytemplate=Template(filename='log.html')
			return mytemplate.render(form=form)
		else:
			
			user = form.d.Nombre
			pas = form.d.Contrasenia
			
			try:
				conn=pymongo.MongoClient()
			except pymongo.errors.ConnectionFailure, e:
				print "Could not connect to MongoDB: %s" % e 
			
			
			db = conn['usuarios']
			collection = db.my_collection
			
		
			if db.my_collection.find({'password':form.d.Contrasenia,'usuario':form.d.Nombre}).count() == 1:

				fo = login2()
				fu = login4()
				mytemplate=Template(filename='principal.html')
				session.usuario = form.d.Nombre
				session.pagina = 'log'	
				session.pagantes = ''
				return mytemplate.render(fo=fo, user=user, fu=fu)
			else:
				mytemplate=Template(filename='log.html')
				return mytemplate.render(form=form)
			
			

class editar:
	
	def POST(self):
		
		fa = login()
		session.pagina = 'editar'	
		session.pagantes = 'registro'
		#session.usuario = 'rafael'
		
		try:
			conn=pymongo.MongoClient()
		except pymongo.errors.ConnectionFailure, e:
			print "Could not connect to MongoDB: %s" % e 
			
			
		db = conn['usuarios']
		collection = db.my_collection
		
		consulta = list(db.my_collection.find({"usuario": session.usuario}))
		

		mytemplate=Template(filename='editar.html')
		return mytemplate.render(form=fa, consulta=consulta)
		
class final:
	
	def POST(self):
		form = login()
		
		if not form.validates():
			mytemplate=Template(filename='editar.html')
			return mytemplate.render(form=form)
			
		else:
			
			try:
				conn=pymongo.MongoClient()
			except pymongo.errors.ConnectionFailure, e:
				print "Could not connect to MongoDB: %s" % e 
			
			
			db = conn['usuarios']
			collection = db.my_collection
				
			doc = {'usuario': form.d.Nombre, 'apellidos': form.d.Apellidos, 'DNI': form.d.DNI, 'email': form.d.email, 'fecha_nacimiento': form.d.dia_nacimiento+'/'+form.d.mes_nacimiento+'/'+form.d.anio_nacimiento, 'direccion': form.d.direccion, 'pago': form.d.FormaPago, 'visa': form.d.NumeroVISA, 'password': form.d.Contrasenia}

			collection.insert(doc)
			
			fu=login4()
			f2=login2()
			mytemplate=Template(filename='prueba.html')
			consulta = list(db.my_collection.find({"usuario": form.d.Nombre}))
			return mytemplate.render(consulta=consulta, form=f2, fu=fu)

class out:
	def POST(self):
		mytemplate=Template(filename='index.html')
		session.pagina = ''
		return mytemplate.render()

class pags:
	def GET(self):
		mytemplate=Template(filename='pagi.html')
		
		return mytemplate.render(pagina=session.pagina,pagantes=session.pagantes, user=session.usuario)

class editargrafico:
	
	def GET(self):
		form=graficologin()
		try:
			con=pymongo.Connection()
		except pymongo.errors.ConnectionFailure, e:
			print 'no se puede conectar a MongoDB: %s' % e
			
		db=con.grafica
		coleccion=db.graficas
		graficoetiqueta=[]
		graficovalor=[]
		
		for varn in coleccion.find():
			graficoetiqueta.append(varn['etiqueta'])
			graficovalor.append(varn['valor'])
			
		mytemplate=Template(filename='editargrafico.html')
		return mytemplate.render(graficoetiqueta=graficoetiqueta, graficovalor=graficovalor, form=form)
		
	def POST(self):
		
		graficoetiqueta=[]
		graficovalor=[]
		form=graficologin()
		
		if not form.validates():
			mytemplate=Template(filename='editargrafico.html')
			return mytemplate.render(graficoetiqueta=graficoetiqueta, graficovalor=graficovalor, form=form)
			
		else:
			try:
				con=pymongo.Connection()
			except pymongo.errors.ConnectionFailure, e:
				print 'NOse puede conectar a mongoDB: %s' % e
				
			db=con.grafica
			coleccion=db.graficas
			doc={'etiqueta': form.d.etiqueta, 'valor': form.d.valor}
			coleccion.insert(doc)
			
			mytemplate=Template(filename='insertargrafico.html')
			return mytemplate.render()

class borrargrafico:
	def POST(self):
		try:
			con=pymongo.Connection()
		except pymongo.errors.ConnectionFailure, e:
			print 'NO se puede conectar a mongoDB: %s' % e
		
		db=con.grafica
		coleccion=db.graficas
		coleccion.remove()
		mytemplate=Template(filename='borrargrafico.html')
		return mytemplate.render()
    
class vergrafico:
	def GET(self):
		try:
			con=pymongo.Connection()
		except pymongo.errors.ConnectionFailure, e:
			print 'No se puede conectar a mongoDB: %s' % e
		db=con.grafica
		coleccion=db.graficas
		graficoetiqueta=[]
		graficovalor=[]
		
		for varn in coleccion.find():
			graficoetiqueta.append(varn['etiqueta'])
			graficovalor.append(varn['valor'])
		
		mytemplate=Template(filename='mostrargrafico.html')
		return mytemplate.render(graficoetiqueta=graficoetiqueta, graficovalor=graficovalor)
				
class maps:
	def GET(self):
		form = mapslogin()
		
		mytemplate=Template(filename='maps.html')
		session.pagina = 'maps'
		return mytemplate.render(form=form)
		
	def POST(self):
		
		form=mapslogin()
		
		if not form.validates():
			mytemplate=Template(filename='maps.html')
			return mytemplate.render(form=form)
			
		else:
			mytemplate=Template(filename='maps2.html')
			session.pagina = 'maps2'
			origen = form.d.origen
			destino = form.d.destino
			return mytemplate.render(origen=origen, destino=destino)
			
class twitter:
	def GET(self):
		form = login7()
		mytemplate=Template(filename='twitter.html')
		return mytemplate.render(form=form)
		
	def POST(self):
		fb = login7()
		
		if not fb.validates():
			mytemplate=Template(filename='twitter.html')
			return mytemplate.render(fb=fb)
		else:
			valor = fb.d.ciudad
			
			CONSUMER_KEY = 'jew5DcYN3TuLU6upxn9aA'
			CONSUMER_SECRET = 'mIgYDSUb6sDuAk2XZJnhGSJtfObsh5NALq0nEW3x1w'
			ACCESS_KEY = '278447421-sJAvc30UoxymkQXXV9N74CHQxZ9MQNOSvugGw2e8'
			ACCESS_SECRET = 'vmE16lU85T950yqDqJQ3DpcZLLK6BYa5eMwuQuWJmJ2U8'

			auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
			auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
			api = tweepy.API(auth)
			
			#tweets = api.search(q=valor, count=30)
			if valor == 'granada':
				tweets = api.search(geocode="37.175894,-3.59779,0.5km",count=50)
				
			elif valor == 'priego':
				tweets = api.search(geocode="37.438407,-4.194815,0.5km",count=50)
				
			elif valor == 'cordoba':
				tweets = api.search(geocode="37.88931,-4.779155,0.5km",count=50)
				
			elif valor == 'malaga':
				tweets = api.search(geocode="36.718887,-4.419831,0.5km",count=50)
				
			elif valor == 'jaen':
				tweets = api.search(geocode="37.767803,-3.790772,0.5km",count=50)
				
			elif valor == 'huelva':
				tweets = api.search(geocode="37.261374,-6.944681,0.5km",count=50)
				
			elif valor == 'cadiz':
				tweets = api.search(geocode="36.52714,-6.288859,0.5km",count=50)
			else:
				tweets = api.search(geocode="37.175894,-3.59779,0.5km",count=50)
			
			
			tweet = []
			for result in tweets:
				tweet.append(result.text)

			mytemplate=Template(filename='twitter2.html')
			return mytemplate.render(tweet=tweet)

if __name__ == "__main__":
    app.run()   
