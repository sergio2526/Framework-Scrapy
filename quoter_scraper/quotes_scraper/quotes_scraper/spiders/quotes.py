import scrapy

# title = //h1/a/text()
# quotes = //span[@class="text" and @itemprop="text"]/text()
# Top tags = //div/a[@class="tag"]/text()
# next page button = //ul[@class="pager"]/li[@class="next"]/a/@href
# author = //div[@class="quote"]/span/small[@class="author"]/text()

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
            author = kwargs['author']
        quotes.extend(response.xpath('//span[@class="text" and @itemprop="text"]/text()').getall())
        author.extend(response.xpath('//div[@class="quote"]/span/small[@class="author"]/text()').getall())

        next_page_button_link = response.xpath('//ul[@class="pager"]/li[@class="next"]/a/@href').get()
        if next_page_button_link:
            yield response.follow(next_page_button_link, callback=self.parse_only_quotes,  cb_kwargs={'quotes':quotes,'author': author})
        else:
            yield{
                'quotes':quotes,
                'author': author
            }


    def parse(self, response):
        title = response.xpath('//h1/a/text()').get()
        quotes = response.xpath('//span[@class="text" and @itemprop="text"]/text()').getall()
        top_tags = response.xpath('//div/a[@class="tag"]/text()').getall()
        author = response.xpath('//div[@class="quote"]/span/small[@class="author"]/text()').getall()

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
            yield response.follow(next_page_button_link, callback=self.parse_only_quotes, cb_kwargs={'quotes':quotes,'author': author})


if __name__ == '__main__':
    QuotesSpider.parse()
