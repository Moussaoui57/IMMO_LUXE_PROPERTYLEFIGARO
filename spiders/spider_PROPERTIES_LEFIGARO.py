# -*- coding: utf-8 -*-
import re
import scrapy 
from urlparse import urlsplit, urlunsplit
from Myutils import *
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from .items import *
#/home/w.oueslati/addancO/SELOGER_IMMOFR/PROPRIETES_LEFIGARO/proprietes_lefigaro_fr
#time scrapy crawl figaro022018  -o /home/w.oueslati/022018/figaro102017_MARS.csv > /home/w.oueslati/022018/figaro102017_MARS.shell
class DirSpider(CrawlSpider):
    custom_settings = {
        'DOWNLOAD_DELAY': '1.5',
        ##'HTTPCACHE_GZIP': 'False',

        ##'COMPRESSION_ENABLED': 'False',
        #'LOG_ENABLED': 'False',
        #'CONCURRENT_REQUESTS_PER_DOMAIN': '1000',
        #'CONCURRENT_REQUESTS': '1000',
           }    
    rotate_user_agent = True
    rotate_ip_addresses = True
  
    #start_urls =open("/home/w.oueslati/pf07").read().splitlines()
    #start_urls = [
    #        'https://proprietes.lefigaro.fr/',
    #        'https://proprietes.lefigaro.fr/annonces/',
    #        'https://proprietes.lefigaro.fr/location/immobilier-location-prestige-france/',
    #        'https://proprietes.lefigaro.fr/location-vacances/location-vacances-luxe-france/',
    #]

    name = "PROPRIETESLEFIGARO_2021_02"
    rotate_user_agent = True
    # rotate_ip_addresses = True
    
    #start_urls = open("pf10.seeds").read().splitlines()
     

    start_urls = [
                'https://proprietes.lefigaro.fr/',
                'https://proprietes.lefigaro.fr/annonces/',
                'https://proprietes.lefigaro.fr/location/immobilier-location-prestige-france/',
                'https://proprietes.lefigaro.fr/location-vacances/location-vacances-luxe-france/',
        ]

    def parse(self,response):
        base_url="https://proprietes.lefigaro.fr"

        list_announce=response.xpath("//a[@class='itemlist js-itemlist']/@href").extract()
        for link in list_announce:
            annonce=base_url+link
            yield scrapy.Request(url=annonce,callback=self.parse_details)

        next_page=response.xpath("//a[@class='wrap-pagination-item js-page-next']/@href").extract_first()
        if next_page:
            next_link=base_url+next_page
            yield scrapy.Request(url=next_link,callback=self.parse)

    def parse_details(self, response):
        print(response.url,"======>")
        if "/location-vacances/" in response.url:
            print("parse_item_vacance")
            i = {}
            for key, val in vacances.iteritems():
                try:
                    i[key] = self.extract(val, response)
                except:
                    i[key] = ""
            i['ANNONCE_LINK'] = response.url
            i['FROM_SITE'] = 'http://proprietes.lefigaro.fr/'
            i['ACHAT_LOC'] = 8
            i['URL_PROMO'] = self.get_url_pro(i['URL_PROMO'])  # Done
            try:
                i['AGENCE_VILLE'] = " ".join(
                    response.xpath('//p[@class="agency-localisation"]/text()').extract()[1].split())
            except:
                i['AGENCE_VILLE'] = ""
            i['PIECE'] = self.get_piece_num2(response)
            try:
                i['MINI_SITE_ID'] = re.findall('agence=(\d+)', i['URL_PROMO'])[0]  # Done
            except:
                i['MINI_SITE_ID'] = ""
            i['AGENCE_CP'] = self.match_and_apply('[0-9]{5}', i['AGENCE_ADRESSE'])  # Done
            #telf_xpath=response.xpath("//*[@class='mobile-only anchor anchor-phone js-clickphone-mobile midwidth-anchor']/a/@href").extract_first().replace("tel:","")
            telf_xpath= response.xpath("//li[@class='agency-phone-content']/span/a/@href").extract_first().replace("tel:","") 
            print(telf_xpath) 
            i['AGENCE_TEL'] = self.format_phone_num(telf_xpath)  # Done
            tel_agence = get_phones(i['AGENCE_TEL'])[0]
            if len(str(tel_agence)) > 5:
                i['AGENCE_TEL'] = get_phones(i['AGENCE_TEL'])[0]

            i['M2_TOTALE'] = self.get_m2_totale(response)  # Done
            i['ID_CLIENT'] = self.match_and_apply('/([0-9-]+)/', response.url)  # Done
            ad = " ".join(response.xpath('//*[@itemprop="addressLocality"]/text()').extract())
            i['AGENCE_DEPARTMENT'] = " ".join(re.findall('\((\d+)\)', ad))  # Done
            i['AGENCE_VILLE'] = re.sub('\(?\d+\)?', "", i['AGENCE_VILLE'])  # Done
            i['MINI_SITE_URL'] = i['URL_PROMO']  # Done
            i['ANNONCE_DATE'] = self.match_and_apply('data-tc-date-mel="(.*)"', response.body)  # Done
            i['SELLER_TYPE'] = "Pro"  # Done
            i['PIECE'] = self.get_piece_num2(response)  # Done
            # i['SIREN'] = self.match_and_apply('^(.*) -',
            # " ".join(response.xpath('//p[@class="ref-annonce"]/text()').extract()))
            i['SIREN'] = " ".join(re.findall('annonceur : ([a-zA-Z0-9-_+]+)', i['SIREN']))  # Done
            ville = " ".join(response.xpath('//*[@itemprop="addressLocality"]/text()').extract())
            i['VILLE'] = " ".join(re.sub('\(\d+\)', '', ville).split())  # Done
            # i['PRIX'] = " ".join(" ".join(i['PRIX']).split())
            i['PAYS_AD'] = " ".join(re.findall('-([a-zA-Z+]+)/', response.url)).title()  # Done
            i['PRIX'] = " ".join(re.findall('(\d.*\d+)', i['PRIX']))
            i['DEPARTEMENT'] = extract_item("(//div/@data-tc-departement)[1]", response)
            if len(i["AGENCE_CP"]) > 3:
                i["AGENCE_DEPARTEMENT"] = (i["AGENCE_CP"].strip())[0:2]
            i['PAYS_AD'] = i['PAYS_AD'].replace("Vacances", "")
            i['PAYS_AD'] = i['PAYS_AD'].replace("Cnr", "Espagne")
            i['PAYS_AD'] = i['PAYS_AD'].replace("Deu", "Allemagne")
            if "ANNONCEUR PARTICULIER" in response.body:
                i['SELLER_TYPE'] = "Part"
            i = liss(i)
            i["CATEGORIE"] = extract_re("o.fr/\w+\-?\w+?/(\w+)-", response.url)
            i['NOM'] = extract_item("//h1/span/text()", response)
            #i['NOM'] = extract_re("http://proprietes.lefigaro.fr/[^/]*/([^/]*)/.*", response.url)
            #i['NOM'] = i['NOM'].replace("-", " ").replace("+", " ")
            if(i["CATEGORIE"] == ""):
                i["CATEGORIE"] = "maison - appartement"
            if (i["PHOTO"]==""):
                i["PHOTO"]=response.xpath("//div[@class='container-medias']/div/span/text()").extract_first()
                print(i["PHOTO"])  
            yield i
        if "/annonces/" in response.url:
            print("parse_item_achat")
            i = {}
            for key, val in achat.iteritems():
                try:
                    i[key] = self.extract(val, response)
                except:
                    i[key] = ""
            i['ANNONCE_LINK'] = response.url
            i['FROM_SITE'] = 'http://proprietes.lefigaro.fr/'
            i['ACHAT_LOC'] = 1
            i['URL_PROMO'] = self.get_url_pro(i['URL_PROMO'])  # Done
            try:
                i['AGENCE_VILLE'] = " ".join(response.xpath('//p[@class="agency-localisation"]/text()').extract()[1].split())
            except:
                i['AGENCE_VILLE'] = ""
            i['PIECE'] = self.get_piece_num2(response)
            try:
                i['MINI_SITE_ID'] = re.findall('agence=(\d+)', i['URL_PROMO'])[0]  # Done
            except:
                i['MINI_SITE_ID'] = ""
            i['AGENCE_CP'] = self.match_and_apply('[0-9]{5}', i['AGENCE_ADRESSE'])  # Done
            i['M2_TOTALE'] = self.get_m2_totale(response)  # Done
            i['ID_CLIENT'] = self.match_and_apply('/([0-9-]+)/', response.url)  # Done
            ad = " ".join(response.xpath('//*[@itemprop="addressLocality"]/text()').extract())
            i['AGENCE_DEPARTMENT'] = " ".join(re.findall('\((\d+)\)', ad))  # Done
            i['AGENCE_VILLE'] = re.sub('\(?\d+\)?', "", i['AGENCE_VILLE'])  # Done
            i['MINI_SITE_URL'] = i['URL_PROMO']  # Done
            i['ANNONCE_DATE'] = self.match_and_apply('data-tc-date-mel="(.*)"', response.body)  # Done
            i['SELLER_TYPE'] = "Pro"  # Done
            i['PIECE'] = self.get_piece_num2(response)  # Done
            # i['SIREN'] = self.match_and_apply('^(.*) -',
            # " ".join(response.xpath('//p[@class="ref-annonce"]/text()').extract()))
            i['SIREN'] = " ".join(re.findall('annonceur : ([a-zA-Z0-9-_+]+)', i['SIREN']))  # Done
            ville = " ".join(response.xpath('//*[@itemprop="addressLocality"]/text()').extract())
            i['VILLE'] = " ".join(re.sub('\(\d+\)', '', ville).split())  # Done
            # i['PRIX'] = " ".join(" ".join(i['PRIX']).split())
            i['PAYS_AD'] = " ".join(re.findall('-([a-zA-Z+]+)/', response.url)).title()  # Done
            i['PRIX'] = " ".join(re.findall('(\d.*\d+)', i['PRIX']))
            i['DEPARTEMENT'] = extract_re("(\d{2})",extract_item("//div[@class='main-title-annonce']/*",response))
            if len(i["AGENCE_CP"]) > 3:
                i["AGENCE_DEPARTEMENT"] = (i["AGENCE_CP"].strip())[0:2]
            #i['AGENCE_TEL'] = self.format_phone_num(" ".join(re.findall('href="tel:(.*)"', response.body)))  # Done
            #telf_xpath=response.xpath("//*[@class='mobile-only anchor anchor-phone js-clickphone-mobile midwidth-anchor']/a/@href").extract_first().replace("tel:","")
            telf_xpath = response.xpath("//li[@class='agency-phone-content']/span/a/@href").extract_first().replace("tel:","")
            i['AGENCE_TEL'] = self.format_phone_num(telf_xpath) #my modif
            tmp_tel = i['AGENCE_TEL'].split('-')[0]
            i['AGENCE_TEL'] = get_phones(tmp_tel)[0]
            if len(i["AGENCE_TEL"]) < 3:
                i['AGENCE_TEL'] = self.format_phone_num(telf_xpath) #my modif
                #i['AGENCE_TEL'] = self.format_phone_num(" ".join(re.findall('href="tel:(.*)"', response.body)))
            tel_agence = get_phones(i['AGENCE_TEL'])[0]
            if len(str(tel_agence)) > 5:
                i['AGENCE_TEL'] = get_phones(i['AGENCE_TEL'])[0]            
            if len(i["PRIX"]) < 3:
                i["PRIX"] = extract_item('//div[@class="prix-annonce"]/descendant-or-self::*/text()',response)
            if len(i["AGENCE_CP"]) > 3:
                i["AGENCE_DEPARTEMENT"] = (i["AGENCE_CP"].strip())[0:2]
            i['PAYS_AD'] = i['PAYS_AD'].replace("Vacances", "")
            i['PAYS_AD'] = i['PAYS_AD'].replace("Cnr", "Espagne")
            i['PAYS_AD'] = i['PAYS_AD'].replace("Deu", "Allemagne")
            if "ANNONCEUR PARTICULIER" in response.body:
                i['SELLER_TYPE'] = "Part"
            '''
            if "ANNONCEUR PARTICULIER" in response.body:
                i['SELLER_TYPE'] = "Part"
            i['PAYS_AD'] = i['PAYS_AD'].replace("Cnr", "Espagne")
            i['PAYS_AD'] = i['PAYS_AD'].replace("Deu", "Allemagne")
            '''
            i = liss(i)
            #i['CATEGORIE'] = extract_re( "http://proprietes.lefigaro.fr/[^/]*/(\w+).*/.*", response.url)
            #i['NOM'] = extract_re("http://proprietes.lefigaro.fr/[^/]*/([^/]*)/.*", response.url)
            #i['NOM'] = i['NOM'].replace("-", " ").replace("+", " ")
            i["CATEGORIE"] = extract_re("o.fr/\w+\-?\w+?/(\w+)-", response.url)
            i['NOM'] = extract_item("//h1/span/text()", response)
            if(i["CATEGORIE"] == ""):
                i["CATEGORIE"] = "maison - appartement"            
            if (i["PHOTO"]==""):
                i["PHOTO"]=response.xpath("//div[@class='container-medias']/div/span/text()").extract_first()
                print(i["PHOTO"])  
            yield i

        if "/location/" in response.url:
            print("parse_item_location")
            i = {}
            for key, val in location.iteritems():
                try:
                    i[key] = self.extract(val, response)
                except:
                    i[key] = ""
            i['ANNONCE_LINK'] = response.url
            i['FROM_SITE'] = 'http://proprietes.lefigaro.fr/'
            i['ACHAT_LOC'] = 2
            i['URL_PROMO'] = self.get_url_pro(i['URL_PROMO'])  # Done
            try:
                i['AGENCE_VILLE'] = " ".join(
                    response.xpath('//p[@class="agency-localisation"]/text()').extract()[1].split())
            except:
                i['AGENCE_VILLE'] = ""
            i['PIECE'] = self.get_piece_num2(response)
            try:
                i['MINI_SITE_ID'] = re.findall('agence=(\d+)', i['URL_PROMO'])[0]  # Done
            except:
                i['MINI_SITE_ID'] = ""
            i['AGENCE_CP'] = self.match_and_apply('[0-9]{5}', i['AGENCE_ADRESSE'])  # Done

            i['M2_TOTALE'] = self.get_m2_totale(response)  # Done
            i['ID_CLIENT'] = self.match_and_apply('/([0-9-]+)/', response.url)  # Done
            ad = " ".join(response.xpath('//*[@itemprop="addressLocality"]/text()').extract())
            i['AGENCE_DEPARTMENT'] = " ".join(re.findall('\((\d+)\)', ad))  # Done
            i['AGENCE_VILLE'] = re.sub('\(?\d+\)?', "", i['AGENCE_VILLE'])  # Done
            i['MINI_SITE_URL'] = i['URL_PROMO']  # Done
            i['ANNONCE_DATE'] = self.match_and_apply('data-tc-date-mel="(.*)"', response.body)  # Done
            i['SELLER_TYPE'] = "Pro"  # Done
            i['PIECE'] = self.get_piece_num2(response)  # Done
            # i['SIREN'] = self.match_and_apply('^(.*) -',
            # " ".join(response.xpath('//p[@class="ref-annonce"]/text()').extract()))
            i['SIREN'] = " ".join(re.findall('annonceur : ([a-zA-Z0-9-_+]+)', i['SIREN']))  # Done
            ville = " ".join(response.xpath('//*[@itemprop="addressLocality"]/text()').extract())
            i['VILLE'] = " ".join(re.sub('\(\d+\)', '', ville).split())  # Done
            # i['PRIX'] = " ".join(" ".join(i['PRIX']).split())
            i['PAYS_AD'] = " ".join(re.findall('-([a-zA-Z+]+)/', response.url)).title()  # Done
            i['PRIX'] = " ".join(re.findall('(\d.*\d)', i['PRIX']))
            i['AGENCE_TEL'] = self.format_phone_num(" ".join(re.findall('href="tel:(.*)"', response.body))).split('-')[0]
            tel_agence = get_phones(i['AGENCE_TEL'])[0]
            if len(str(tel_agence)) > 5:
                i['AGENCE_TEL'] = get_phones(i['AGENCE_TEL'])[0]
            if len(i["AGENCE_CP"]) > 3:
                i["AGENCE_DEPARTEMENT"] = (i["AGENCE_CP"].strip())[0:2]
            i['PAYS_AD'] = i['PAYS_AD'].replace("Vacances", "")
            i['PAYS_AD'] = i['PAYS_AD'].replace("Cnr", "Espagne")
            i['PAYS_AD'] = i['PAYS_AD'].replace("Deu", "Allemagne")
            #i['DEPARTEMENT'] = extract_item("(//div/@data-tc-departement)[1]", response)
            i['DEPARTEMENT'] = extract_re("(\d{2})",extract_item("//div[@class='main-title-annonce']/*",response))
            if "ANNONCEUR PARTICULIER" in response.body:
                i['SELLER_TYPE'] = "Part"
            i = liss(i)
            #i['CATEGORIE'] = extract_re("http://proprietes.lefigaro.fr/[^/]*/(\w+).*/.*", response.url)
            #i["CATEGORIE"] = extract_re("o.fr/\w+\-?\w+?/(\w+)-", response.url)
            #i['NOM'] = extract_re("http://proprietes.lefigaro.fr/[^/]*/([^/]*)/.*", response.url)
            #i['NOM'] = i['NOM'].replace("-", " ").replace("+", " ")
            i["CATEGORIE"] = extract_re("o.fr/\w+\-?\w+?/(\w+)-", response.url)
            i['NOM'] = extract_item("//h1/span/text()", response)
            if(i["CATEGORIE"] == ""):
                i["CATEGORIE"] = "maison - appartement"  
            if (i["PHOTO"]==""):
                i["PHOTO"]=response.xpath("//div[@class='container-medias']/div/span/text()").extract_first()
                print(i["PHOTO"])  

            yield i   


    


    def get_url_pro(self, url):
        if isinstance(url, unicode):
            scheme, host, path, query, fragment = urlsplit(url)
            if url.startswith('/'):
                return urlunsplit(
                    ("http",
                        "proprietes.lefigaro.fr", "/annonces/", query, ''))
            else:
                return urlunsplit((scheme, host, "/annonces/", query, ''))
        else:
            return ""

    def extract(self, val, response):
        return " ".join(" ".join(response.xpath(val).extract()).split())

    def match_and_apply(self, pat, text):
        l = re.findall(pat, text)
        if not l:
            return ""
        return re.findall(pat, text)[0].strip()

    def get_m2_totale(self, response):
        l = response.xpath('//span[@class="txt"]/text()').extract()
        if "m" in l:
            i = l.index("m")
            l2 = response.xpath('//span[@class="nb"]/text()').extract()
            return l2[i]
        #return ""

    def get_piece_num(self, response):
        l = response.xpath('//span[@class="txt"]/text()').extract()
        if u"pi\xe8ces" in l:
            i = l.index(u"pi\xe8ces")
            l2 = response.xpath('//span[@class="nb"]/text()').extract()
            return l2[i]
        return ""

    def get_piece_num2(self, response):
        l = extract_item("//ul[@class='hz-list']/li/span/text()", response)
        if u"mbres" in l:
            return extract_re("(\d+)\s+chambre", l)
        if u"ces" in l:
            return extract_re("(\d+)\s+p", l)
        return ""

    def format_phone_num(self, phone):
        _l = ["(", ")", "."]
        for j in _l:
            phone = phone.replace(j, "")
        if phone.startswith("+33 "):
            return phone.replace("+33 ", "").replace(" ", "")
        else:
            return phone.replace("+", "00").replace(" ", "")


