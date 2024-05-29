import scrapy


class MyspiderSpider(scrapy.Spider):
    name = "myspider"
    allowed_domains = ["google.com"]
    start_urls = ["https://scholar.google.com/citations?user=6af0v1IAAAAJ&hl=en&oi=sra&cstart=0&pagesize=80"]

    def parse(self, response):
        list_=response.xpath('//tr[@class="gsc_a_tr"]')
        print(len(list_))

        username=response.xpath('//div[@id="gsc_prf_in"]/text()').get()
        for publication in response.xpath('//tr[@class="gsc_a_tr"]'):
            title = publication.xpath('//td[@class="gsc_a_t"]/a[@class="gsc_a_at"]/text()').get()
            authors = publication.xpath('//td[@class="gsc_a_t"]/div[1]/text()').get()
            journal_info = publication.xpath('//td[@class="gsc_a_t"]/div[2]/text()').get()
            cited_by=publication.xpath('//td[@class="gsc_a_c"]/a[@class="gsc_a_ac gs_ibl"]/text()').get()
            year=publication.xpath('//td[@class="gsc_a_y"]/span/text()').get()
            if ',' not in authors:
                result = 1
            else:
                numbers = authors.split(',')
                result = len(numbers)

            yield {
                'author name':username,
                'title': title,
                'total_authors': authors,
                'number of authors': result,
                'journal_info': journal_info,
                'cited by': cited_by,
                'year':year
            }
