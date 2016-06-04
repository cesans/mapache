import mapache

from bs4 import BeautifulSoup, NavigableString
import urllib.request

from dateutil.parser import parse

from tqdm import tqdm

def poll_from_table(table, date_column, party_columns, name=None, party_names=None, 
                    error_column=None, pollster_column=None, poll_rows=None):
    #TODO deal with multicolumns        
    # TODO: report errors correctly
    
    if not poll_rows:
        # TODO, is it a good guess?
        poll_rows = (2,-0)

    row = wikitable_get_rows(table)[0]
    cells = wikitable_get_cells(row)
    n_cells = len(cells)
    # TODO if wrong columns in args?

    if error_column is not None:
        polls = mapache.PollsList(name)
        
    
    if not party_names: #Try to extract the names from the first row...
        party_names = []
        row = wikitable_get_rows(table)[0]
        cells = wikitable_get_cells(row)
        
        for c in cells[party_columns[0]:party_columns[1]]:
            _, party_name = wikitable_get_url(c)
            if name == None:
                # TODO 
                return None
            party_names.append(party_name)
            
    rows = wikitable_get_rows(table)[poll_rows[0]: poll_rows[1]]
    
    for row in tqdm(rows):
        cells = wikitable_get_cells(row)

        if len(cells) <= 3:
            # TODO ??
            continue
            
        pollster=None
        if pollster_column is not None:
            pollster = cells[pollster_column].text
        
        err = None
        if error_column is not None:
            err = cells[-3].text
            if err:
                err = float(err[1:].split(' ')[0])

        date = cells[date_column].text
        date = parse(date)            

        votes = {}
        for i, p in enumerate(cells[party_columns[0]: party_columns[1]]):
            v = p.text
            if v:
                try:
                    v = float(v)
                except:
                    # Multiple parties in the cell, fix?
                    continue
                votes[party_names[i]] = v

        poll = mapache.Poll(votes, date, pollster, err)
                
        polls.add(poll)
        
    return polls

def wikitable_get_rows(table):
    return table.findAll("tr")

def wikitable_get_cells(row):
    return row.findAll("th")  + row.findAll("td")
    
def wikitable_get_url(c):
    a = c.find("a")
        
    url, name = None, None
    if a:
        url = "http://wikipedia.org" + a.attrs["href"]
        name = a.attrs["title"]
                
    return url,name
    
def wikitable_get_imgurl(c):
    img = c.find("img")
    
    imgurl = None
    if img:
        imgurl = "http:" + img.attrs["src"]

    return imgurl
    
def tables_from_wiki(url):
    #TODO Add title of the section to identify the table?
    page = urllib.request.urlopen(url)
    soup = BeautifulSoup(page, "html.parser")
    tables = soup.findAll("table", class_="wikitable")
    return tables
def party_from_wiki(url, name=None):

    # The party wiki page is fetched to get the full name and full logo
    page = urllib.request.urlopen(url)
    party_soup = BeautifulSoup(page, "html.parser")
    infobox = party_soup.find("table", {"class": "infobox vcard"})
    logo = "http:" + infobox.find("td", {"class":"logo"}).find("img").attrs["src"]

    # If both the English and Spanish name are present the Spanish one
    # has class "nickname", otherway it has "fn org"
    full_name = infobox.find("span", {"class":"nickname"})
    if full_name:
        full_name = full_name.text
    else:
        full_name = infobox.find("span", {"class":"fn org"}).text

    if not name:
        name = full_name
    
    short_name = None
    abbreviation = infobox.find("td", {"class":"nickname"})
    if abbreviation:
        short_name = abbreviation.text

    # With the data obtained from the wiki a new party is created and added
    # to the party set
    party = mapache.Party(name, logo_url=logo, short_name=short_name,
                   # The abbreviation/short name will be created automatically  
                   # if the name provided is too long and short_name=None                    
                   full_name = full_name)
    return party
