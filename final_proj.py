import secrets
import sqlite3
import plotly
import plotly.plotly as py
import plotly.graph_objs as go
import requests
import json

PLOTLY_USERNAME = secrets.PLOTLY_USERNAME
PLOTLY_API_KEY = secrets.PLOTLY_API_KEY
plotly.tools.set_credentials_file(username=PLOTLY_USERNAME, api_key=PLOTLY_API_KEY)

DBNAME = 'art.db'
#create culture bar chart
def make_culture_bar():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    flag = True
    while flag == True:
        user_cultures = input("Please enter a list of cultures to compare, separated by a comma: ")
        cultures = user_cultures.split(", ")
        cult_counts = []
        for cult in cultures:
            statement = '''SELECT Name, ObjectCount FROM Cultures WHERE Name="'''+cult+'''"'''
            cur.execute(statement)
            results = cur.fetchall()
            for i in results:
                cult_counts.append(i)
        if len(cult_counts) > 0:
            x_ax = [str(i[0]) for i in cult_counts]
            y_ax = [i[1] for i in cult_counts]
            data = [go.Bar(
                x=x_ax,
                y=y_ax,
                text=["{} objects".format(i[1]) for i in cult_counts],
                hoverinfo = ['text'],
                textposition = 'auto',
                textfont = dict(color = 'black', size = 24),
                marker=dict(
                    color='rgb(221, 190, 51)',
                    line=dict(
                        color='rgb(86, 77, 36)',
                        width=2.5),
                    ),
                opacity=0.5
            )]
            layout = go.Layout(
                title = '<b>Object Count per Culture - Harvard Art Museum</b>',
                titlefont = dict(color = 'black', size = 28),
                yaxis=dict(
                range = [0, max(y_ax)]
                )
            )

            fig = go.Figure(data=data, layout=layout)
            py.plot(fig, filename='culture-bar')
            flag = False
        else:
            response = input("We could not find any results based on the cultures you entered. Check spelling or search for different cultures. Would you like to try again (Yes/No)?")
            if response == "Yes":
                continue
            else:
                flag = False

# Make artist from culture active during various time periods
def artists_from_culture():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    flag = True
    while flag == True:
        desired_cult = input("Specify a culture from which to search for artists: ")
        statement = '''SELECT People.Name, People.StartDate, People.EndDate FROM People JOIN Cultures ON People.Culture=Cultures.Id WHERE Cultures.Name="'''+desired_cult+'''" AND People.StartDate <> "0" AND People.EndDate <> "0"'''
        cur.execute(statement)
        results = cur.fetchall()
        if len(results) > 0:
            min = 0
            max = 0
            for i in results:
                if i[2] > max and i[2] < 2018:
                    max = i[2]
                if i[1] < min:
                    min = i[1]
            min_yr = int(min/100)*100
            max_yr = int(max/100)*100
            categories = []
            for i in range(int((max_yr-min_yr)/100)):
                min_end = min_yr
                min_yr+=99
                categories.append(str(min_end)+'_'+str(min_yr))
                min_yr+=1
            counts = {}
            for i in results:
                for x in categories:
                    if x not in counts:
                        counts[x] = 1
                    if i[1] > int(x.split("_")[0]) and i[1] < int(x.split("_")[1]):
                        counts[x] += 1
            labels = list(counts.keys())
            values = list(counts.values())
            colors = ['#ed5555', '#ed9c2a', '#f2e44d', '#81fc6f', '#6fddfc', '#6f88fc', '#b37cff']
            trace0 = go.Scatter(
                x = labels,
                y = values,
                mode = 'lines+markers',
                name = 'Works Created',
                line = dict(
                    color = ('rgb(205, 12, 24)'),
                    width = 4)
                )
            layout = dict(title = 'Number of Works Created Across Time by {} Artists'.format(desired_cult),
                titlefont = dict(color = 'black', size = 28),
                xaxis = dict(title = 'Time Period'),
                yaxis = dict(title = 'Number of Works Created'))
            data = [trace0]
            fig = dict(data=data, layout=layout)
            py.plot(fig, filename='styled-line')
            flag = False
        else:
            response = input("The culture you specified returned 0 results. Check spelling or try again with a different culture. Would you like to try again (Yes/No)?")
            if response == "Yes":
                continue
            else:
                flag = False

#make gender bar graph
def gender_bar():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    flag = True
    while flag == True:
        culture = input("Enter the culture from which you would like to compare the number of male and female artists: ")
        statement = '''SELECT People.Name, People.Gender FROM People JOIN Cultures ON People.Culture = Cultures.Id WHERE Cultures.Name="'''+culture+'''"'''
        cur.execute(statement)
        results = cur.fetchall()
        if len(results) > 0:
            male = 0
            female = 0
            unknown = 0
            for i in results:
                if i[1] == 'male':
                    male += 1
                elif i[1] == 'female':
                    female += 1
                else:
                    unknown += 1
            x_ax = ['Male', 'Female']
            y_ax = [male, female]
            data = [go.Bar(
                x=x_ax,
                y=y_ax,
                text=["<b>{} male artists</b>".format(y_ax[0]), "<b>{} female artists</b>".format(y_ax[1])],
                textposition = 'auto',
                hoverinfo = 'x',
                textfont = dict(color = 'black', size = 24),
                marker=dict(
                    color='rgb(180, 133, 234)',
                    line=dict(
                        color='rgb(51, 5, 104)',
                        width=3.0)
                    ),
                opacity=0.5
            )]
            layout = go.Layout(
                title = '<b>Gender Comparison for Artists from Given Culture<br>(Number of artists where gender is not recorded is '+str(unknown)+')</b>',
                titlefont = dict(color = 'black', size = 28),
                yaxis=dict(
                range = [0, max(y_ax)]
                ),
                xaxis = dict(
                )
            )

            fig = go.Figure(data=data, layout=layout)
            py.plot(fig, filename='culture-bar')
            flag = False
        else:
            response = input("Sorry the culture you searched for did not match any represented in our database. Make sure the spelling is correct, or search for a different culture. Would you like to try again (Yes/No)?")
            if response == "Yes":
                continue
            else:
                flag = False
#get object data about artist
def get_objects():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    flag = True
    while flag == True:
        name = input("Enter an artist's name to search for objects they created: ")
        statement = '''SELECT Objects.Title, Objects.Date, Objects.Medium FROM People JOIN Objects ON People.Id = Objects.Artist WHERE People.Name="'''+name+'''"'''
        cur.execute(statement)
        results = cur.fetchall()
        if len(results) > 0:
            titles = []
            dates = []
            mediums = []
            for item in results:
                titles.append(item[0])
                dates.append(item[1])
                mediums.append(item[2])
            trace0 = go.Table(
                columnorder = [1,2,3],
                columnwidth = [80,80,80],
                name = "Objects created by {}".format(name),
                header = dict(
                values = [['<b>Title</b>'],
                        ['<b>Date</b>'],
                        ['<b>Medium</b>']],
                line = dict(color = '#000000'),
                fill = dict(color = '#506784'),
                font = dict(color = 'white', size = 20),
                height = 40),
            cells = dict(
                values = [titles, dates, mediums],
                line = dict(color = '#6a6a6b'),
                fill = dict(color = '#cfbedb'),
                font = dict(color = '#000000', size = 18),
                height = 30
            ))
            layout = dict(
                width=950,
                height=800,
                autosize=True,
                title='Objects created by {}'.format(name),
                margin = dict(t=100),
                font = dict(color = 'black', size = 20),
                )

            data = [trace0]
            fig = go.Figure(data=data, layout=layout)
            py.plot(fig, filename = "artist-objects")
            flag = False
        else:
            response = input("The artist you searched for returned no results. They are not represented in this museum or you need to check spelling. Would you like to try again (Yes/No)?")
            if response == "Yes":
                continue
            else:
                flag = False
#get books user is interested in
def get_books():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    books_search = input("What topic of books are you looking for? ")
    search_term = '%'+books_search+'%'
    statement = '''SELECT Title, Author, Link FROM Books WHERE Title LIKE "'''+search_term+'''" UNION SELECT Title, Author, Link FROM Books WHERE Description LIKE "'''+search_term+'''" UNION SELECT Title, Author, Link FROM Books WHERE Subtitle LIKE "'''+search_term+'''" UNION SELECT Title, Author, Link FROM Books WHERE Categories LIKE "'''+search_term+'''"'''
    cur.execute(statement)
    results = cur.fetchall()
    if len(results) > 0:
        titles = []
        authors = []
        links = []
        for item in results:
            titles.append(item[0])
            if item[1] == '':
                authors.append("No Author Provided")
            else:
                authors.append(item[1])
            links.append(item[2])
        trace0 = go.Table(
            columnorder = [1,2,3],
            columnwidth = [80,80,80],
            header = dict(
            values = [['<b>Title</b>'],
                      ['<b>Author</b>'],
                      ['<b>Find the book here:</b>']],
                      line = dict(color = '#000000'),
                      fill = dict(color = '#506784'),
                      font = dict(color = 'white', size = 20),
                      height = 40
                      ),
        cells = dict(
            values = [titles, authors, links],
            line = dict(color = '#6a6a6b'),
            fill = dict(color = '#cfbedb'),
            font = dict(color = '#000000', size = 18),
            height = 30
            ))
        layout = dict(
            width=950,
            height=800,
            autosize=True,
            title='Books about {}'.format(books_search),
            margin = dict(t=100),
            )

        data = [trace0]
        fig = go.Figure(data=data, layout=layout)
        py.plot(fig, filename = "Books Search Results")
    else:
        response = input("Sorry, we found no books in our database matching your search. Would you like to search the broader web? (Enter Yes/No): ")
        if response == 'Yes':
            base = "https://www.googleapis.com/books/v1/volumes?maxResults=40&q=subject+"+books_search.replace(" ", "")
            resp = requests.get(base).text
            book_json = json.loads(resp)
            titles = []
            authors = []
            links = []
            for item in book_json["items"]:
                titles.append(item["volumeInfo"]["title"])
                try:
                    if item["volumeInfo"]["authors"] == "":
                        authors.append("No Author Provided")
                    else:
                        authors.append(item["volumeInfo"]["authors"])
                except:
                    authors.append("No Auhtor Provided")
                links.append(item["volumeInfo"]["canonicalVolumeLink"])
            trace0 = go.Table(
                columnorder = [1,2,3],
                columnwidth = [80,80,80],
                header = dict(
                values = [['<b>Title</b>'],
                          ['<b>Author</b>'],
                          ['<b>Find the book here:</b>']],
                          line = dict(color = '#000000'),
                          fill = dict(color = '#506784'),
                          font = dict(color = 'white', size = 14),
                          height = 40
                          ),
            cells = dict(
                values = [titles, authors, links],
                line = dict(color = '#6a6a6b'),
                fill = dict(color = '#cfbedb'),
                font = dict(color = '#000000', size = 12),
                height = 30
                ))

            data = [trace0]

            py.plot(data, filename = "Books Search Results")
        else:
            print("Thanks!")

#interactive part to get what user wants to search for:

def load_help_text():
    with open('help.txt') as f:
        return f.read()

def interactive_prompt():
    help_text = load_help_text()
    flag = True
    while flag == True:
        response = input('What kind of information would you like to see (Enter "help" for options)? ')
        if response == 'quit':
            flag = False
        elif response == 'object counts':
            make_culture_bar()
        elif response == 'gender comparison':
            gender_bar()
        elif response == 'artists work periods':
            artists_from_culture()
        elif response == 'objects from an artist':
            get_objects()
        elif response == 'find books':
            get_books()
        elif response == 'help':
            print(help_text)
        else:
            print("Sorry, the command you entered could not be processed. Type 'help' to see valid commands.")
if __name__=="__main__":
    interactive_prompt()
