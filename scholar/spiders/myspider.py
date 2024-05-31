import csv
import json

import scrapy
from urllib.parse import urlparse

class MyspiderSpider(scrapy.Spider):
    name = "myspider"
    allowed_domains = ["google.com"]

    def __init__(self, *args, **kwargs):
        super(MyspiderSpider, self).__init__(*args, **kwargs)
        self.data_from_csv = []
        with open('input/input.csv', 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            next(csvreader)
            for row in csvreader:
                print(row[0])
                self.data_from_csv.append(row[0])
    def start_requests(self):
        body = 'json=1'
        # url="https://scholar.google.com/citations?hl=en&user=6af0v1IAAAAJ"
        for url in self.data_from_csv:
            yield scrapy.Request(url, method='POST', body=body, callback=self.parse,
                                 meta={'url': url,
                                       'cstart': 0})
    def parse(self,response):
        url = response.meta['url']
        cstart = int(response.meta['cstart'])+10
        body = 'json=1'
        json_data=json.loads(response.text)
        # print(response.text)
        yield scrapy.Request(response.url,callback=self.parse_send,    meta={'url': url},)
        if json_data.get('N'):
            cstart += 10
            new_page = f"{url}&cstart={cstart}&pagesize=100"
            yield scrapy.Request(
                new_page,
                method='POST',
                body=body,
                meta={'url': url, 'cstart': cstart},
                callback=self.parse,
                dont_filter=True
            )

    def parse_send(self, response):
        base_page=response.meta['url']
        list_ = response.xpath('//tr[@class="gsc_a_tr"]')
        print(len(list_))

        username = response.xpath('//div[@id="gsc_prf_in"]/text()').get()
        for publication in list_[:]:
            url=publication.xpath('.//td[@class="gsc_a_t"]/a[@class="gsc_a_at"]/@href').get()
            title = publication.xpath('.//td[@class="gsc_a_t"]/a[@class="gsc_a_at"]/text()').get()
            authors = publication.xpath('.//td[@class="gsc_a_t"]/div[1]/text()').get()
            journal_info = publication.xpath('.//td[@class="gsc_a_t"]/div[2]/text()').get()
            cited_by = publication.xpath('.//td[@class="gsc_a_c"]/a[@class="gsc_a_ac gs_ibl"]/text()').get()
            year = publication.xpath('.//td[@class="gsc_a_y"]/span/text()').get()
            author_nike_name=None
            print(url)

            if ',' not in authors:
                result = 1
            else:
                numbers = authors.split(',')

                result = len(numbers)
            data= {
                # 'url':url,
                'author name': username,
                'title': title,
                # 'total_authors': authors,
                # 'number of authors': result,
                'journal_info': journal_info,
                'cited by': cited_by,
                'year': year,
                # "Order in which the author we're interested in appears":author_nike_name
            }
            yield  scrapy.Request('https://scholar.google.com{}'.format(url),callback=self.details,meta={'data':data,'url':base_page})
    def details(self,response):
        data = response.meta['data']
        url=response.meta['url']
        detail_url=response.url
        articale_url=response.xpath('//div[@id="gsc_oci_title"]/a/@href').get()
        authors=response.xpath('//div[@class="gs_scl"]/div[@class="gsc_oci_value"]/text()').get()
        if ',' not in authors:
            result = 1
        else:
            numbers = authors.split(',')

            result = len(numbers)
        author_nike_name=None
        base_url=None
        if articale_url:
            parsed_url = urlparse(articale_url)
            base_url = parsed_url.scheme + "://" + parsed_url.netloc
        print(base_url)
        data['root url'] = base_url
        data['number of authors']=result
        data['Title Url']=url
        try:
            searchs = authors.split(',')
            first_name = data['author name'].rsplit(" ")
            # last_name = data['author name'].rsplit(" ", 1)[1]
            for name in first_name:
                for index,search in enumerate(searchs):
                    if name.lower() in search.lower():
                       author_nike_name = index+1
        except IndexError:
            print("Error")
        data["Order in which the author we're interested in appears"] =author_nike_name
        data['Url'] = url
        data['Title Url'] = detail_url
        data['root url'] = base_url
        yield  data