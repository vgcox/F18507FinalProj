import secrets
import requests
import json
API_KEY= secrets.HARVARD_API_KEY
cult_base="https://api.harvardartmuseums.org/culture?size=100&apikey={}".format(API_KEY)
people_base="https://api.harvardartmuseums.org/person?size=100&apikey={}".format(API_KEY)
obj_base = "https://api.harvardartmuseums.org/object?size=100&apikey={}".format(API_KEY)

CULT_FNAME = 'cultures.json'
PEOPLE_FNAME = 'people.json'
OBJ_FNAME = 'objects.json'
try:
    cache_file = open(CULT_FNAME, 'r')
    cache_contents = cache_file.read()
    CULT_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CULT_DICTION = {}

try:
    cache_file = open(PEOPLE_FNAME, 'r')
    cache_contents = cache_file.read()
    PEOPLE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    PEOPLE_DICTION = {}

try:
    cache_file = open(OBJ_FNAME, 'r')
    cache_contents = cache_file.read()
    OBJ_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    OBJ_DICTION = {}

def get_unique_key(url):
  return url

def cult_cache(url):
    unique_ident = get_unique_key(url)
    if unique_ident in CULT_DICTION:
        # print("Getting cached data...")
        return CULT_DICTION[unique_ident]
    else:
        # print("Making a request for new data...")
        resp = requests.get(url)
        CULT_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CULT_DICTION)
        fw = open(CULT_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CULT_DICTION[unique_ident]

def people_cache(url):
    unique_ident = get_unique_key(url)
    if unique_ident in PEOPLE_DICTION:
        # print("Getting cached data...")
        return PEOPLE_DICTION[unique_ident]
    else:
        # print("Making a request for new data...")
        resp = requests.get(url)
        PEOPLE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(PEOPLE_DICTION)
        fw = open(PEOPLE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return PEOPLE_DICTION[unique_ident]
def obj_cache(url):
    unique_ident = get_unique_key(url)
    if unique_ident in OBJ_DICTION:
        # print("Getting cached data...")
        return OBJ_DICTION[unique_ident]
    else:
        # print("Making a request for new data...")
        resp = requests.get(url)
        OBJ_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(OBJ_DICTION)
        fw = open(OBJ_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return OBJ_DICTION[unique_ident]
#get cultures
# cult_data = cult_cache(cult_base)
# cult_json_data = json.loads(cult_data)
# cult_pages = cult_json_data["info"]["pages"]
# for page in range(cult_pages-1):
#     page = page+2
#     resp = cult_cache(cult_base+"&page="+str(page))
# # get people
# people_data = people_cache(people_base)
# people_json_data = json.loads(people_data)
# people_pages = people_json_data["info"]["pages"]
# for page in range(people_pages-1):
#     page = page+2
#     resp = people_cache(people_base+"&page="+str(page))
#get object data
obj_data = obj_cache(obj_base)
obj_json_data = json.loads(obj_data)
obj_pages = obj_json_data["info"]["pages"]
for page in range(obj_pages-1):
    page = page+2
    resp = obj_cache(obj_base+"&page="+str(page))

#get google data
#searching for generic books about harvard art museum to populate database - user can search these volumes first and
#if no satisfactory results based on artist they are looking for, make new call API
book_base = "https://www.googleapis.com/books/v1/volumes?maxResults=40&q=subject+harvardartmuseum&startIndex="

BOOK_FNAME = 'harvardBooks.json'
try:
    cache_file = open(BOOK_FNAME, 'r')
    cache_contents = cache_file.read()
    BOOK_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    BOOK_DICTION = {}

def book_cache(url):
    unique_ident = get_unique_key(url)
    if unique_ident in BOOK_DICTION:
        # print('Getting cached data...')
        return BOOK_DICTION[unique_ident]
    else:
        # print('Making request for new data')
        resp = requests.get(url)
        BOOK_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(BOOK_DICTION)
        fw = open(BOOK_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return BOOK_DICTION[unique_ident]
book_data = book_cache(book_base+"0")
book_json = json.loads(book_data)
total_pages = int(book_json["totalItems"]/40)
index = 0
for i in range(total_pages):
  index+=1
  ind=str(index+1)
  resp = book_cache(book_base+ind)
DBNAME = 'art.db'
def create_art_db():
    try:
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()
        conn.commit()
        print("Database initiated")
    except:
        print("Error, database not created correctly")
    statement = '''DROP TABLE IF EXISTS 'Cultures';'''
    cur.execute(statement)
    statement = '''DROP TABLE IF EXISTS 'People';'''
    cur.execute(statement)
    statement = '''DROP TABLE IF EXISTS 'Books';'''
    cur.execute(statement)
    conn.commit()
    statement = '''DROP TABLE IF EXISTS 'Objects';'''
    cur.execute(statement)
    conn.commit()
    conn.close()
    
def populate_art_db():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = '''PRAGMA foregin_keys'''
    cur.execute(statement)
    conn.commit()
    statement = ''' CREATE TABLE Cultures (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT,
    ObjectCount INTEGER,
    CultureId INTEGER)'''
    cur.execute(statement)
    conn.commit()
    statement = '''CREATE TABLE People(
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Name TEXT,
    Gender TEXT,
    StartDate INTEGER,
    EndDate INTEGER,
    Culture INTEGER,
    FOREIGN KEY (Culture) REFERENCES Cultures (Id)
    )'''
    cur.execute(statement)
    conn.commit()
    statement = ''' CREATE TABLE Books (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT,
    Subtitle TEXT,
    Author TEXT,
    Description TEXT,
    Categories TEXT,
    Link TEXT
    )
    '''
    cur.execute(statement)
    conn.commit()
    statement = '''CREATE TABLE Objects (
    Id INTEGER PRIMARY KEY AUTOINCREMENT,
    Title TEXT,
    Date TEXT,
    Medium TEXT,
    Artist INTEGER,
    FOREIGN KEY (Artist) REFERENCES People (Id)
    )'''
    cur.execute(statement)
    conn.commit()
    with open('cultures.json') as f:
        data =json.loads(f.read())
        for key in data:
          data_json = json.loads(data[key])
          records = data_json["records"]
          for item in records:
            statement = '''INSERT INTO Cultures (Name, ObjectCount, CultureId) VALUES (?,?,?)'''
            cur.execute(statement, (item["name"], item["objectcount"], item["id"]))
            conn.commit()
    with open('people.json') as f:
        data =json.loads(f.read())
        for key in data:
          data_json = json.loads(data[key])
          records = data_json["records"]
          for item in records:
            culture_id = item["culture"]
            # print(culture_id)
            try:
                cult_statement = '''SELECT Id FROM Cultures WHERE Name="'''+culture_id+'''"'''
                cur.execute(cult_statement)
                results = cur.fetchall()
                # print(results)
                culture_value = results[0][0]
            except:
                culture_value = "NULL"
            statement = '''INSERT INTO People (Name, Gender, StartDate, EndDate, Culture) VALUES (?,?,?,?,?)'''
            cur.execute(statement, (item["displayname"], item["gender"], item["datebegin"], item["dateend"], culture_value))
            conn.commit()
    with open('harvardBooks.json') as f:
        book_data = json.loads(f.read())
        for key in book_data:
            items = json.loads(book_data[key])
            for item in items["items"]:
                try:
                    subtitle = item["volumeInfo"]["subtitle"]
                except:
                    subtitle = "NULL"
                authors = ""
                categories = ""
                try:
                    for auth in item["volumeInfo"]["authors"]:
                        authors = authors+auth+", "
                except:
                    pass
                try:
                    description = item["volumeInfo"]["description"]
                except:
                    description = "No description available"
                try:
                    for cat in item["volumeInfo"]["categories"]:
                        categories = categories+cat+", "
                except:
                    pass
                statement = '''INSERT INTO Books (Title, Subtitle, Author, Description, Categories, Link) VALUES (?,?,?,?,?,?)'''
                cur.execute(statement, (item["volumeInfo"]["title"], subtitle, authors, description, categories, item["volumeInfo"]["canonicalVolumeLink"]))
                conn.commit()
    with open('objects.json') as f:
        data =json.loads(f.read())
        counter = 0
        for key in data:
          data_json = json.loads(data[key])
          records = data_json["records"]
          for item in records:
            try:
                artist_id = item["people"][0]["name"]
                artist_statement = '''SELECT Id FROM People WHERE Name="'''+artist_id+'''"'''
                cur.execute(artist_statement)
                results = cur.fetchall()
                artist_value = results[0][0]
            except:
                artist_value = "Unknown Artist"
            try:
                title = item["title"]
            except:
                title = "Untitled"
            statement = '''INSERT INTO Objects (Title, Date, Medium, Artist) VALUES (?,?,?,?)'''
            cur.execute(statement, (title, item["dated"], item["medium"], artist_value))
            conn.commit()
            counter+=1
            print(counter)
    conn.close()
