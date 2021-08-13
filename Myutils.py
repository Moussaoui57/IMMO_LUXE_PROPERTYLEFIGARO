# -*- coding: utf-8 -*-
from collections import OrderedDict
from parsel import Selector
import os
import phonenumbers
import re
import datetime

def cpORdept(cp, dept):
    cod = ['','']
    try:
        if (len(str(dept)) == 2) and (len(str(cp)) != 5):
            cod = [str(dept)+"000", dept]
        if (len(str(dept)) != 2) and (len(str(cp)) == 5):
            cod = [cp, str(dept)[0:2]]
    except:
        cod = [cp, dept]
    return cod


def format_item( item):
    row_dict = "\""+item['ANNONCE_LINK']+"\","+  \
        "\""+item['FROM_SITE'].replace('\"','')+"\","+ \
        "\""+item['ID_CLIENT'].replace('\"','')+"\","+ \
        "\""+item['ANNONCE_DATE'].replace('\"','')+"\","+ \
        "\""+item['ACHAT_LOC'].replace('\"','')+"\","+ \
        "\""+item['MAISON_APT'].replace('\"','')+"\","+ \
        "\""+item['CATEGORIE'].replace('\"','')+"\","+ \
        "\""+item['NEUF_IND'].replace('\"','')+"\","+ \
        "\""+item['NOM'].replace('\"','')+"\","+ \
        "\""+item['ADRESSE'].replace('\"','')+"\","+ \
        "\""+item['CP'].replace('\"','')+"\","+ \
        "\""+item['VILLE'].replace('\"','')+"\","+ \
        "\""+item['QUARTIER'].replace('\"','')+"\","+ \
        "\""+item['DEPARTEMENT'].replace('\"','')+"\","+ \
        "\""+item['REGION'].replace('\"','')+"\","+ \
        "\""+item['PROVINCE'].replace('\"','')+"\","+ \
        "\""+item['ANNONCE_TEXT'].replace('\"','')+"\","+ \
        "\""+item['ETAGE'].replace('\"','')+"\","+ \
        "\""+item['NB_ETAGE'].replace('\"','')+"\","+ \
        "\""+item['LATITUDE'].replace('\"','')+"\","+ \
        "\""+item['LONGITUDE'].replace('\"','')+"\","+ \
        "\""+item['M2_TOTALE'].replace('\"','')+"\","+ \
        "\""+item['SURFACE_TERRAIN'].replace('\"','')+"\","+ \
        "\""+item['NB_GARAGE'].replace('\"','')+"\","+ \
        "\""+item['PHOTO'].replace('\"','')+"\","+ \
        "\""+item['PIECE'].replace('\"','')+"\","+ \
        "\""+item['PRIX'].replace('\"','')+"\","+ \
        "\""+item['PRIX_M2'].replace('\"','')+"\","+ \
        "\""+item['URL_PROMO'].replace('\"','')+"\","+ \
        "\""+item['PAYS_AD'].replace('\"','')+"\","+ \
        "\""+item['PRO_IND'].replace('\"','')+"\","+ \
        "\""+item['SELLER_TYPE'].replace('\"','')+"\","+ \
        "\""+item['MINI_SITE_URL'].replace('\"','')+"\","+ \
        "\""+item['MINI_SITE_ID'].replace('\"','')+"\","+ \
        "\""+item['AGENCE_NOM'].replace('\"','')+"\","+ \
        "\""+item['AGENCE_ADRESSE'].replace('\"','')+"\","+ \
        "\""+item['AGENCE_CP'].replace('\"','')+"\","+ \
        "\""+item['AGENCE_VILLE'].replace('\"','')+"\","+ \
        "\""+item['AGENCE_DEPARTEMENT'].replace('\"','')+"\","+ \
        "\""+item['EMAIL'].replace('\"','')+"\","+ \
        "\""+item['WEBSITE'].replace('\"','')+"\","+ \
        "\""+item['AGENCE_TEL'].replace('\"','')+"\","+ \
        "\""+item['AGENCE_TEL_2'].replace('\"','')+"\","+ \
        "\""+item['AGENCE_TEL_3'].replace('\"','')+"\","+ \
        "\""+item['AGENCE_TEL_4'].replace('\"','')+"\","+ \
        "\""+item['AGENCE_FAX'].replace('\"','')+"\","+ \
        "\""+item['AGENCE_CONTACT'].replace('\"','')+"\","+ \
        "\""+item['PAYS_DEALER'].replace('\"','')+"\","+ \
        "\""+item['FLUX'].replace('\"','')+"\","+ \
        "\""+item['SITE_SOCIETE_URL'].replace('\"','')+"\","+ \
        "\""+item['SITE_SOCIETE_ID'].replace('\"','')+"\","+ \
        "\""+item['SITE_SOCIETE_NAME'].replace('\"','')+"\","+ \
        "\""+item['SIREN'].replace('\"','')+"\","+ \
        "\""+item['SPIR_ID']+"\","+ \
        "\""+item['STOCK_NEUF']+"\"," + \
        "\""+item['SOLD']+"\""
    return row_dict

def extract_sel(item_xpath, resp):
    #sel = Selector(resp)
    sel= resp
    extr = sel.xpath(item_xpath).extract()
    extr = " ".join(" ".join(extr).split())
    return extr

def extract_item( item_xpath, resp):
    return " ".join(" ".join(resp.xpath(item_xpath).extract()).split())

def toLoc( text):
    if 'vendre' in text:
        return '1'
    return '2'

def extract_re( pat, text):
    l = re.findall(pat, text)
    if not l:
        return ""
    return re.findall(pat, text)[0]

def format_tel( exp):
    exp = exp.replace('+ 33 (0)', '').replace('+33 (0)', '').replace('+33(0)', '').replace('+ 33 (0)', '')
    tel = re.findall('\d+', exp)
    return " ".join("".join(tel).split())

def extract_tel( exemple):
    tel = {}
    tel['AGENCE_TEL'] = exemple
    tel['AGENCE_TEL_2'] = ''
    tel['AGENCE_FAX'] = ''
    tel['SITE_SOCIETE_URL'] = ''
    m0 = re.search('Tel :(.*\d )Tel :(.*\d )Fax :(.*\d)( ?.*)', tel['AGENCE_TEL'])
    m2 = re.search('Tel :(.*\d )Tel :(.*\d)( ?.*)', tel['AGENCE_TEL'])
    m1 = re.search('Tel :(.*\d )Fax :(.*\d)( ?.*)', tel['AGENCE_TEL'])
    m4 = re.search('Tel :(.*\d)$', tel['AGENCE_TEL'])
    m3 = re.search('Tel :(.*\d)( ?.*)', tel['AGENCE_TEL'])
    if m0:
        tel['AGENCE_TEL'] = m0.group(1)
        tel['AGENCE_TEL_2'] = m0.group(2)
        tel['AGENCE_FAX'] = m0.group(3)
        tel['SITE_SOCIETE_URL'] = m0.group(4) if m0.group(4) is not None else ""
    elif m2:
        tel['AGENCE_TEL'] = m2.group(1)
        tel['AGENCE_TEL_2'] = m2.group(2)
        tel['SITE_SOCIETE_URL'] = m2.group(3) if m2.group(3) is not None else ""
    elif m1:
        tel['AGENCE_TEL'] = m1.group(1)
        tel['AGENCE_FAX'] = m1.group(2)
        tel['SITE_SOCIETE_URL'] = m1.group(3) if m1.group(3) is not None else ""
    elif m3:
        tel['AGENCE_TEL'] = m3.group(1)
        tel['SITE_SOCIETE_URL'] = m3.group(2) if m3.group(2) is not None else ""
    elif m4:
        tel['AGENCE_TEL'] = m4.group(1)
    tel['AGENCE_TEL'] = format_tel(tel['AGENCE_TEL'])
    tel['AGENCE_TEL_2'] = format_tel(tel['AGENCE_TEL_2'])
    tel['AGENCE_FAX'] = format_tel(tel['AGENCE_FAX'])
    return tel

def getEnsemble2( ulist1):
    ulist = ulist1.split()
    l = []
    [l.append(x) for x in ulist if x not in l]
    if len(l) > 0:
        return l[0]
    else:
        return ''

def getEnsemble( ulist1):
    ulist = ulist1.split()
    l = []
    [l.append(x) for x in ulist if x not in l]
    return ' - '.join(l)

def join_extract( a_list):
    return " ".join(" || ".join(a_list).split())

def get_phones( text):
    tels = ['','','','','','','','','','','']
    i = 0
    #print( "ho   "+text)
    for match in phonenumbers.PhoneNumberMatcher(text, "FR"):
        #exp = match.number
        exp = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.NATIONAL)
        #print(exp)
        #print(match)
        # TODO recheck
        tels[i] = str(" ".join("".join(re.findall('\d+', exp)).split()))
        i = i + 1
    return tels

def get_urls( ss):
    #urls = re.findall("Site : (\w+[.].*[.]\w+) ",ss)
    urls = re.findall("Site : \w{0,5}?[.]|[a-z0-9.\-]+[.][a-z]{2,4}",ss)
    urls= " ".join("".join(urls).split())
    return urls.replace(':','').replace('Site','')

def get_emails( ss):
    email = re.findall("[a-z0-9.\-]+@[a-z0-9.\-]+",ss)
    email = " ".join(" ".join(email).split())
    return email


def liss(item):
        try:
            item["ANNONCE_LINK"] = enquote(item["ANNONCE_LINK"])
        except:
            pass
        # varchar(255)
        try:
            if (len(item["FROM_SITE"]) < 256) :
                item["FROM_SITE"] = enquote(item["FROM_SITE"][0:254])
            else:
                item["FROM_SITE"] = enquote(item["FROM_SITE"])
        except:
            pass
        # varchar(255)
        try:
            item["ID_CLIENT"] = enquote(item["ID_CLIENT"])
        except:
            pass
        # datetime
        try:
            item["ANNONCE_DATE"] = format_date(item["ANNONCE_DATE"])
        except:
            pass
        # smallint(4)
        try:
            item["ACHAT_LOC"] = smallInt(item["ACHAT_LOC"], 2)
        except:
            pass
        # smallint(4)
        try:
            item["MAISON_APT"] = item["MAISON_APT"]
        except:
            pass
        # varchar(255)
        try:
            item["CATEGORIE"] = trimmer(item["CATEGORIE"], 254)
        except:
            pass
        # enum('N', 'Y')
        try:
            item["NEUF_IND"] = enumYN(item["NEUF_IND"])
        except:
            pass
        # varchar(255)
        try:
            item["NOM"] = enquote(item["NOM"])
        except:
            pass
        # varchar(255)
        try:
            item["ADRESSE"] = trimmer(item["ADRESSE"],254)
        except:
            pass
        # varchar(20)
        try:
            item["CP"] = trimmer(item["CP"], 19)
        except:
            pass
        # varchar(255)
        try:
            item["VILLE"] = trimmer(item["VILLE"], 254)
        except:
            pass
        # varchar(255)
        try:
            item["QUARTIER"] = trimmer(item["QUARTIER"], 254)
        except:
            pass
        # varchar(50)
        try:
            item["DEPARTEMENT"] = trimmer(item["DEPARTEMENT"], 49)
        except:
            pass
        # varchar(255)
        try:
            item["REGION"] = trimmer(item["REGION"], 254)
        except:
            pass
        # varchar(255)
        try:
            item["PROVINCE"] = trimmer(item["PROVINCE"], 254)
        except:
            pass
        # text
        #item["ANNONCE_TEXT"] = enquote(item["ANNONCE_TEXT"])
        try:
            item["ANNONCE_TEXT"] = item["ANNONCE_TEXT"]
        except:
            pass
        # smallint(4)
        try:
            item["ETAGE"] = smallInt(item["ETAGE"], 3)
        except:
            pass
        # smallint(4)
        try:
            item["NB_ETAGE"] = smallInt(item["NB_ETAGE"], 3)
        except:
            pass
        # varchar(255)
        try:
            item["LATITUDE"] = trimmer(item["LATITUDE"], 254)
        except:
            pass
        # varchar(255)
        try:
            item["LONGITUDE"] = trimmer(item["LONGITUDE"], 254)
        except:
            pass
        # decimal(8,2)
        try:
            item["M2_TOTALE"] = formatdec(item["M2_TOTALE"])
        except:
            pass
        # decimal(8,2)
        try:
            item["SURFACE_TERRAIN"] = formatdec(item["SURFACE_TERRAIN"])
        except:
            pass
        # smallint(4)
        try:
            item["NB_GARAGE"] = smallInt(item["NB_GARAGE"],3)
        except:
            pass
        # smallint(4)
        try:
            item["PHOTO"] = smallInt(item["PHOTO"], 3)
        except:
            pass
        # smallint(4)
        try:
            item["PIECE"] = smallInt(item["PIECE"], 3)
        except:
            pass
        # int(9) unsigned
        try:
            item["PRIX"] = formatBigInt(item["PRIX"])
        except:
            pass
        # mediumint(9)
        try:
            item["PRIX_M2"] = formatBigInt(item["PRIX_M2"])
        except:
            pass
        # text
        try:
            item["URL_PROMO"] = enquote(item["URL_PROMO"])
        except:
            pass
        # varchar(255)
        try:
            item["PAYS_AD"] = trimmer(item["PAYS_AD"], 254)
        except:
            pass
        # enum('Y', 'N')
        try:
            item["PRO_IND"] = enumYN(item["PRO_IND"])
        except:
            pass
        # varchar(50)
        try:
            item["SELLER_TYPE"] = trimmer(item["SELLER_TYPE"], 49)
        except:
            pass
        # text
        try:
            item["MINI_SITE_URL"] = enquote(item["MINI_SITE_URL"])
        except:
            pass
        # varchar(50)
        try:
            item["MINI_SITE_ID"] = trimmer(item["MINI_SITE_ID"], 49)
        except:
            pass
        # varchar(255)
        try:
            item["AGENCE_NOM"] = trimmer(item["AGENCE_NOM"], 249)
        except:
            pass
        # varchar(255)
        try:
            item["AGENCE_ADRESSE"] = trimmer(item["AGENCE_ADRESSE"], 254)
        except:
            pass
        # varchar(20)
        try:
            item["AGENCE_CP"] = trimmer(item["AGENCE_CP"], 19)
        except:
                pass
        # varchar(255)
        try:
            item["AGENCE_VILLE"] = trimmer(item["AGENCE_VILLE"], 254)
        except:
                pass
        # varchar(50)
        #item["AGENCE_DEPARTEMENT"] = trimmer(item["AGENCE_DEPARTEMENT"], 49)
        try:
            item["AGENCE_DEPARTEMENT"] = trimmer(item["AGENCE_CP"], 49)[0:2]
        except:
                pass
        # varchar(255)
        try:
            item["EMAIL"] = trimmer(item["EMAIL"], 254)
        except:
                pass
        # varchar(255)
        try:
            item["WEBSITE"] = trimmer(item["WEBSITE"], 254)
        except:
                pass
        # varchar(55)
        #item["AGENCE_TEL"] = get_phones(item["AGENCE_TEL"].encode("utf-8"))[0]
        try:
            item["AGENCE_TEL"] = trimmer(item["AGENCE_TEL"], 54)
        except:
                pass
        # varchar(25)
        #item["AGENCE_TEL_2"] = get_phones(item["AGENCE_TEL_2"].encode("utf-8"))[0]
        try:
            item["AGENCE_TEL_2"] = trimmer(item["AGENCE_TEL_2"], 24)
        except:
                pass
        # varchar(25)
        #item["AGENCE_TEL_3"] = get_phones(item["AGENCE_TEL_3"].encode("utf-8"))[0]
        try:
            item["AGENCE_TEL_3"] = trimmer(item["AGENCE_TEL_3"], 24)
        except:
                pass
        # varchar(25)
        #item["AGENCE_TEL_4"] = get_phones(item["AGENCE_TEL_4"].encode("utf-8"))[0]
        try:
            item["AGENCE_TEL_4"] = trimmer(item["AGENCE_TEL_4"], 24)
        except:
                pass
        # varchar(25)
        try:
            item["AGENCE_FAX"] = trimmer(item["AGENCE_FAX"], 24)
        except:
                pass
        # varchar(255)
        try:
            item["AGENCE_CONTACT"] = trimmer(item["AGENCE_CONTACT"], 254)
        except:
                pass
        # varchar(255)
        try:
            item["PAYS_DEALER"] = trimmer(item["PAYS_DEALER"], 254)
        except:
                pass
        # varchar(255)
        try:
            item["FLUX"] = trimmer(item["FLUX"], 254)
        except:
                pass
        # text
        try:
            item["SITE_SOCIETE_URL"] = enquote(item["SITE_SOCIETE_URL"])
        except:
                pass
        # varchar(100)
        try:
            item["SITE_SOCIETE_ID"] = trimmer(item["SITE_SOCIETE_ID"], 99)
        except:
                pass
        # varchar(255)
        try:
            item["SITE_SOCIETE_NAME"] = trimmer(item["SITE_SOCIETE_NAME"], 254)
        except:
                pass
        # varchar(255)
        try:
            item["SIREN"] = trimmer(item["SIREN"], 254)
        except:
                pass
        # varchar(10)
        try:
            item["SPIR_ID"] = trimmer(item["SPIR_ID"], 9)
        except:
                pass
        # mediumint(9)
        try:
            item["STOCK_NEUF"] = smallInt(item["STOCK_NEUF"], 4)
        except:
                pass
        # enum('N','Y')
        try:
            item["SOLD"] = enumYN(item["SOLD"])
        except:
                pass
        return item

def formatBigInt(champ):
    champ = translate_special(champ)
    champ = champ.replace(" ", "")
    champ = champ.replace(",", "")
    champ = champ.replace(" ", "")
    champ = champ.replace(".", "")
    #champ = champ.strip()
    champ = "".join(champ.split())
    try:
        champ = re.search('^\d+', champ).group()
        int(champ)
    except:
        champ = ""
    #print(champ)
    return champ

def formatdec(champ):
    champ = translate_special(champ)
    champ = champ.replace(" ", "")
    champ = champ.replace(",", ".")
    champ = champ.strip()
    champ = "".join(champ.split())
    try:
        champ = re.search('^\d+(\.\d+)?', champ).group()
        champ = float(champ)
    except:
        champ = ""
    return champ

def enquote(p):
    return p
    ##print(p)
    #if (len(p)== 0):
    #    return ""
    #return "\""+p+"\""

def smallInt(p, lengthp):
    p = translate_special(p)
    p = p.strip()
    try:
        p = re.search('^\d+', p).group()
    except:
        p = ""
        return ""
    if(len(p) < lengthp):
        return int(p)

def enumYN(champ):
    if champ not in "YN":
        return ""
    return enquote(champ)

def trimmer(champ, longueur):
    champ = champ.strip()
    if(len(champ) == 0):
        return ""
    if (len(champ) <= longueur):
        return enquote(champ)
    if (len(champ) > longueur):
        return enquote(champ[0:longueur])

def format_date(d):
    if len(d) == 10:
        d = datetime.datetime.strptime(d, '%d/%m/%Y')
        return enquote(datetime.date.strftime(d, "%Y-%m-%d"))
    return ""



def translate_special(ex):
    '''
    #ex = ex.encode("utf8")
    try:
        ex = ex.decode("utf-8")
        #ex = ex.encode("utf-8")
    except:
        print("error parsing ")
        return ex if ex else ''
    ex = ex.replace('é','e')
    ex = ex.replace('°','')
    #ex = ex.replace('\xC3\xA9','e')
    ex = ex.replace('à','a')
    ex = ex.replace('è','e')
    ex = ex.replace('ù','u')
    ex = ex.replace('â','a')
    ex = ex.replace('ê','e')
    ex = ex.replace('î','i')
    ex = ex.replace('ô','o')
    ex = ex.replace('û','u')
    ex = ex.replace('ç','c')
    ex = ex.replace('€','')
    ex = ex.replace(',','')
    ex = ex.replace(';','')
    ex = ex.replace('€','')
    ex = ex.replace('²','')
    ex = ex.replace('\'',' ')
    '''
    return ex
