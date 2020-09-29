# Curso de Scrapy

---

### El framework asíncrono: Scrapy

Es el framework de alto nivel que realiza:

- web scraping
- web Crawling : Es ir enlace por enlace en una pagina web, es la forma en que los buscadores anexan los sitios web

Este framework es asíncrono, que cada petición que nosotros realizamos al servidor no necesita esperar la siguiente para completarse.

### Carateristicas:

- Procesador de XPath
- Interactive Shell
- JSON, CSV, etc
- robots.txt controlado : respecta a este archivo, es decir, la etica queda asegurada, no necesitamos ver el archivo para hacer scraping, este framework ya lo tiene presente.

Empezar proyecto:

```python
# Inicializar proyecto

pip3 install scrapy autopep8

scrapy startproject tutorial
cd tutorial

# Correr Spiders
scrapy crawl name

#
fetch('url')
```

```python
# Indicar que no tiene una clase la etiqueta p
//p[not(@class)]/text()
```

## ¿ Que es spiders ?

Spider es una clase de python a la cual le decimos que informacion queremos, que informacion no queremos y como guardar esa informacion.

Para empezar a hacer uso de esta creamos un archivo en la carpeta spider y escribimos el siguiente código:

```python
#1) Importar Scrapy
import scrapy

# 2) Definir la lógica para extraer toda la información que queremos de la 
# página, en este caso, extraer todo el html
# Esta clase hereda de scrapy.Spider
class QuotesSpider(scrapy.Spider):

    # 3) Se definen los atributos name y start_urls (lista de direcciones web a 
    # a las que se quiere apuntar)
    name = 'quotes' # este name debe ser un nombre unico en cada spider
    start_urls = [
        'http: quotes.toscrape.com/'
    ]

    # 4) se define el método parse que recibe self y response (hace referencia
    # a la respuesta http en este caso de http: quotes.toscrape.com/' )
    def parse(self,response):
        with open('resultados.html','w',encoding='utf-8') as f:
            f.write(response.text)
```

---

Usar XPath dentro de Scrapy

```python
scrapy shell 'http://quotes.toscrape.com/page/1/'

>>> response.xpath('//h1/a/text()')
[<Selector xpath='//h1/a/text()' data='Quotes to Scrape'>]
>>> response.xpath('//h1/a/text()').get()
'Quotes to Scrape'
>>> response.xpath('//span[@class="text" and @itemprop="text"]/text()').getall()
```

### Archivos de Scrapy :

- [pipelines.py](http://pipelines.py/) : permite modificar los datos desde que entran al *spider* (scripts que extraen información) hasta el final.
- [middlewares.py](http://middlewares.py/): trabaja con un concepto denominado *señales* : controla eventos que suceden entre los requests y la captura de información.
- [items.py](http://items.py/) : transforma los datos que se reciben del requests. _ *init* _.py : define que todos los archivos en la carpeta son un módulo de python.
- Folder spiders : en donde se crearan los scripts.
- [settings.py](http://settings.py/) : archivo con configuraciones del uso de Scrapy.

---

### Convertir datos a formatos json,csv

Si se desea guardar la información en un nuevo formato, solo es se cambiar el formato del archivo

```python
import scrapy

# title = //h1/a/text()
# quotes = //span[@class="text" and @itemprop="text"]/text()
# Top ten tags = //div/a[@class="tag"]/text()

class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    start_urls = [
        'http://quotes.toscrape.com/page/1/'
    ]

    def parse(self, response):
        title = response.xpath('//h1/a/text()').get()
        quotes = response.xpath('//span[@class="text" and @itemprop="text"]/text()').getall()
        top_ten_tags = response.xpath('//div/a[@class="tag"]/text()').getall()

        yield{
            'title': title,
            'quotes': quotes,
            'top_ten_tags': top_ten_tags
        }

if __name__ == '__main__':
    QuotesSpider.parse()

```

```python
#En la consola escribir para guardar la información en .json

scrapy crawl quotes -o quotes.json

#Borrar el archivo y escribirlo nuevamente.

rm quotes.json && scrapy crawl quotes -o quotes.json
```

### response.follow en todas las paginas

```python
import scrapy

# title = //h1/a/text()
# quotes = //span[@class="text" and @itemprop="text"]/text()
# Top ten tags = //div/a[@class="tag"]/text()
# next page button = //ul[@class="pager"]/li[@class="next"]/a/@href

class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    start_urls = [
        'http://quotes.toscrape.com/page/1/'
    ]
    custom_settings = {
        'FEED_URI': 'quotes.json',
        'FEED_FORMAT': 'json'
    }

    def parse(self, response):
        title = response.xpath('//h1/a/text()').get()
        quotes = response.xpath('//span[@class="text" and @itemprop="text"]/text()').getall()
        top_ten_tags = response.xpath('//div/a[@class="tag"]/text()').getall()

        yield{
            'title': title,
            'quotes': quotes,
            'top_ten_tags': top_ten_tags
        }

        next_page_button_link = response.xpath('//ul[@class="pager"]/li[@class="next"]/a/@href').get()
        if next_page_button_link:
            yield response.follow(next_page_button_link, callback=self.parse)

if __name__ == '__main__':
    QuotesSpider.parse()
```

### Multiples Callbacks

```python
import scrapy

# title = //h1/a/text()
# quotes = //span[@class="text" and @itemprop="text"]/text()
# Top ten tags = //div/a[@class="tag"]/text()
# next page button = //ul[@class="pager"]/li[@class="next"]/a/@href

class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    start_urls = [
        'http://quotes.toscrape.com/page/1/'
    ]
    custom_settings = {
        'FEED_URI': 'quotes.json',
        'FEED_FORMAT': 'json'
    }

    def parse_only_quotes(self,response, **kwargs):
        if kwargs:
            quotes = kwargs['quotes']
        quotes.extend(response.xpath('//span[@class="text" and @itemprop="text"]/text()').getall())

        next_page_button_link = response.xpath('//ul[@class="pager"]/li[@class="next"]/a/@href').get()
        if next_page_button_link:
            yield response.follow(next_page_button_link, callback=self.parse_only_quotes, cb_kwargs={'quotes':quotes})
        else:
            yield{
                'quotes':quotes
            }

    def parse(self, response):
        title = response.xpath('//h1/a/text()').get()
        quotes = response.xpath('//span[@class="text" and @itemprop="text"]/text()').getall()
        top_ten_tags = response.xpath('//div/a[@class="tag"]/text()').getall()

        yield{
            'title': title,
            'top_ten_tags': top_ten_tags
        }

        next_page_button_link = response.xpath('//ul[@class="pager"]/li[@class="next"]/a/@href').get()
        if next_page_button_link:
            yield response.follow(next_page_button_link, callback=self.parse_only_quotes, cb_kwargs={'quotes':quotes})

if __name__ == '__main__':
    QuotesSpider.parse()
```

### Pasando argumentos a nuestro Spider

```python
"""
top = getattr(self, 'top', None)
        if top:
            top = int(top)
            top_tags = top_tags[:top]
"""

import scrapy

# title = //h1/a/text()
# quotes = //span[@class="text" and @itemprop="text"]/text()
# Top tags = //div/a[@class="tag"]/text()
# next page button = //ul[@class="pager"]/li[@class="next"]/a/@href

class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    start_urls = [
        'http://quotes.toscrape.com/page/1/'
    ]
    custom_settings = {
        'FEED_URI': 'quotes.json',
        'FEED_FORMAT': 'json'
    }

    def parse_only_quotes(self,response, **kwargs):
        if kwargs:
            quotes = kwargs['quotes']
        quotes.extend(response.xpath('//span[@class="text" and @itemprop="text"]/text()').getall())

        next_page_button_link = response.xpath('//ul[@class="pager"]/li[@class="next"]/a/@href').get()
        if next_page_button_link:
            yield response.follow(next_page_button_link, callback=self.parse_only_quotes, cb_kwargs={'quotes':quotes})
        else:
            yield{
                'quotes':quotes
            }

    def parse(self, response):
        title = response.xpath('//h1/a/text()').get()
        quotes = response.xpath('//span[@class="text" and @itemprop="text"]/text()').getall()
        top_tags = response.xpath('//div/a[@class="tag"]/text()').getall()

        top = getattr(self, 'top', None)
        if top:
            top = int(top)
            top_tags = top_tags[:top]

        yield{
            'title': title,
            'top_tags': top_tags
        }

        next_page_button_link = response.xpath('//ul[@class="pager"]/li[@class="next"]/a/@href').get()
        if next_page_button_link:
            yield response.follow(next_page_button_link, callback=self.parse_only_quotes, cb_kwargs={'quotes':quotes})

if __name__ == '__main__':
    QuotesSpider.parse()

```

### Configuraciones útiles

```python
"""
name = 'quotes'
    start_urls = [
        'http://quotes.toscrape.com/page/1/'
    ]
    custom_settings = {
        'FEED_URI': 'quotes.json',
        'FEED_FORMAT': 'json',
        'CONCURRENT_REQUESTS': 24, # Le decimos que realice 24 peticiones a la vez, como max.
        'MEMUSAGE_LIMIT_MB': 2048, # indicarle cuanta ram utilizara el framework
        'MEMUSAGE_NOTIFY_MAIL': {'sergio@hotmail.com'}, # Si mi spider llega a superar los mb indicados
                                                        # Nos avisara con una notificación al mail
        'ROBOTSTXT_OBEY': True, # Respectar las reglas del sitio
        'USER_AGENT': 'Sergio', # Indicamos la persona que hizo la petición
        'FEED_EXPORT_ENCODING': 'utf-8' # Caracteres de forma correcta
    }

"""

import scrapy

# title = //h1/a/text()
# quotes = //span[@class="text" and @itemprop="text"]/text()
# Top tags = //div/a[@class="tag"]/text()
# next page button = //ul[@class="pager"]/li[@class="next"]/a/@href

class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    start_urls = [
        'http://quotes.toscrape.com/page/1/'
    ]
    custom_settings = {
        'FEED_URI': 'quotes.json',
        'FEED_FORMAT': 'json',
        'CONCURRENT_REQUESTS': 24, # Le decimos que realice 24 peticiones a la vez, como max.
        'MEMUSAGE_LIMIT_MB': 2048, # indicarle cuanta ram utilizara el framework
        'MEMUSAGE_NOTIFY_MAIL': {'sergio@hotmail.com'}, # Si mi spider llega a superar los mb indicados
                                                        # Nos avisara con una notificación al mail
        'ROBOTSTXT_OBEY': True, # Respectar las reglas del sitio
        'USER_AGENT': 'Sergio', # Indicamos la persona que hizo la petición
        'FEED_EXPORT_ENCODING': 'utf-8' # Caracteres de forma correcta
    }

    def parse_only_quotes(self,response, **kwargs):
        if kwargs:
            quotes = kwargs['quotes']
        quotes.extend(response.xpath('//span[@class="text" and @itemprop="text"]/text()').getall())

        next_page_button_link = response.xpath('//ul[@class="pager"]/li[@class="next"]/a/@href').get()
        if next_page_button_link:
            yield response.follow(next_page_button_link, callback=self.parse_only_quotes, cb_kwargs={'quotes':quotes})
        else:
            yield{
                'quotes':quotes
            }

    def parse(self, response):
        title = response.xpath('//h1/a/text()').get()
        quotes = response.xpath('//span[@class="text" and @itemprop="text"]/text()').getall()
        top_tags = response.xpath('//div/a[@class="tag"]/text()').getall()

        top = getattr(self, 'top', None)
        if top:
            top = int(top)
            top_tags = top_tags[:top]

        yield{
            'title': title,
            'top_tags': top_tags
        }

        next_page_button_link = response.xpath('//ul[@class="pager"]/li[@class="next"]/a/@href').get()
        if next_page_button_link:
            yield response.follow(next_page_button_link, callback=self.parse_only_quotes, cb_kwargs={'quotes':quotes})

if __name__ == '__main__':
    QuotesSpider.parse()
```

---

### Proyecto

La función **starts-with ()** comprueba si un atributo String comienza con una cadena específica.

```python
//a[starts-with(@href, "collection")

//a[starts-with(@href, "collection") and (parent::h3|parent::h2)]/@href').getall()
```