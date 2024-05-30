import scrapy


class MyspiderSpider(scrapy.Spider):
    name = "myspider"
    allowed_domains = ["scholar.google.com"]

    start_urls = [
        "https://scholar.google.com/citations?hl=en&user=ksZiJUYAAAAJ&cstart=0&pagesize=100"
    ]

    def parse(self, response):
        url = response.url
        cstart = int(response.meta.get('cstart', 0))

        publications = response.xpath('//tr[@class="gsc_a_tr"]')

        if not publications:
            self.logger.info('No more publications found.')
            return

        for publication in publications:
            relative_url = publication.xpath('.//td[@class="gsc_a_t"]/a[@class="gsc_a_at"]/@href').get()
            title = publication.xpath('.//td[@class="gsc_a_t"]/a[@class="gsc_a_at"]/text()').get()
            authors = publication.xpath('.//td[@class="gsc_a_t"]/div[1]/text()').get()
            journal_info = publication.xpath('.//td[@class="gsc_a_t"]/div[2]/text()').get()
            cited_by = publication.xpath('.//td[@class="gsc_a_c"]/a[@class="gsc_a_ac gs_ibl"]/text()').get()
            year = publication.xpath('.//td[@class="gsc_a_y"]/span/text()').get()

            username = response.xpath('//div[@id="gsc_prf_in"]/text()').get()

            if ',' not in authors:
                result = 1
            else:
                numbers = authors.split(',')
                result = len(numbers)

            data = {
                'author_name': username,
                'title': title,
                'journal_info': journal_info,
                'cited_by': cited_by,
                'year': year,
                'number_of_authors': result,
                'authors_list': authors
            }

            if relative_url:
                absolute_url = response.urljoin(relative_url)
                yield scrapy.Request(absolute_url, callback=self.parse_details, meta={'data': data})

        cstart += 100
        next_page = f"https://scholar.google.com/citations?hl=en&user=ksZiJUYAAAAJ&cstart={cstart}&pagesize=100"
        yield scrapy.Request(next_page, callback=self.parse, meta={'cstart': cstart})

    def parse_details(self, response):
        data = response.meta['data']
        authors = response.xpath('//div[@class="gs_scl"]/div[@class="gsc_oci_value"]/text()').get()

        if authors:
            if ',' not in authors:
                result = 1
            else:
                numbers = authors.split(',')
                result = len(numbers)

            author_nike_name = None
            try:
                searchs = authors.split(',')
                first_name = data['author_name'].rsplit(" ")

                for name in first_name:
                    for search in searchs:
                        if name.lower() in search.lower():
                            author_nike_name = search
                            break
            except IndexError:
                self.logger.error("Error processing author names")

            data["Order in which the author we're interested in appears"] = author_nike_name
            data["number_of_authors"] = result

        yield data
