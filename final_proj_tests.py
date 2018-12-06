import unittest
from final_proj import *

class TestDatabase(unittest.TestCase):

    def test_cultures_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql1 = 'SELECT Name FROM Cultures'
        results1 = cur.execute(sql1)
        results1_list = cur.fetchall()
        self.assertIn(('Malaysian',), results1_list)
        self.assertEqual(len(results1_list), 255)

        sql2 = '''SELECT Name, ObjectCount FROM Cultures WHERE Name="Scottish"'''
        results2 = cur.execute(sql2)
        results2_list = cur.fetchall()
        self.assertEqual(results2_list[0][0], "Scottish")
        self.assertEqual(results2_list[0][1], 184)

        conn.close()

    def test_people_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql3 = '''SELECT Name FROM People WHERE StartDate <> 0 AND EndDate <> 0'''
        results3 = cur.execute(sql3)
        results3_list = cur.fetchall()
        self.assertEqual(results3_list[0][0], 'Sadajiro Yamanaka')
        self.assertEqual(len(results3_list), 16062)

        sql4 = '''SELECT Name, Gender FROM People WHERE Culture=235 AND Gender="female"'''
        results4 = cur.execute(sql4)
        results4_list = cur.fetchall()
        self.assertIn(('Cindy Sherman', 'female'), results4_list)

        conn.close()

    def test_objects_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql5 = '''SELECT Title, Date, Medium FROM Objects WHERE Artist=2648'''
        results5 = cur.execute(sql5)
        results5_list = cur.fetchall()
        self.assertTrue(len(results5_list), 22)
        self.assertEqual(results5_list[3][1], "July 10, 1956")
        conn.close()

    def test_books_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql6 = '''SELECT Title From Books'''
        results6 = cur.execute(sql6)
        results6_list = cur.fetchall()
        self.assertTrue(len(results6_list), 1970)

        sql7 = '''SELECT Title FROM Books WHERE Description LIKE "%Bauhaus%"'''
        results7 = cur.execute(sql7)
        results7_list = cur.fetchall()
        self.assertEqual(results7_list[4][0], "Bauhaus 1919-1933")
        self.assertTrue(len(results7_list), 22)
        conn.close()

class TestCultureBar(unittest.TestCase):

    def test_bar_results(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql8 = '''SELECT Name, ObjectCount FROM Cultures WHERE Name='German' OR Name='Dutch' '''
        results8 = cur.execute(sql8)
        results8_list = cur.fetchall()
        x_ax = [i[0] for i in results8_list]
        y_ax = [i[1] for i in results8_list]
        self.assertEqual(x_ax, ['Dutch', 'German'])
        self.assertEqual(y_ax, [4917, 32996])

        conn.close()

class TestArtistsCulturePie(unittest.TestCase):

    def test_Artists_Pie(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql9 = '''SELECT People.Name, People.StartDate, People.EndDate FROM People JOIN Cultures ON People.Culture=Cultures.Id WHERE Cultures.Name='English' AND People.StartDate <> 0 AND People.EndDate <> 0'''
        results9 = cur.execute(sql9)
        results9_list = cur.fetchall()
        min = 0
        max = 0
        for i in results9_list:
            if i[2] > max and i[2] < 2018:
                max = i[2]
            if i[1] < min:
                min = i[1]
        min_yr = int(min/100)*100
        max_yr = int(max/100)*100
        self.assertTrue(min_yr == 0 and max_yr == 1900)

        conn.close()

class TestGenderBar(unittest.TestCase):

    def test_gender_bar(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql10 = '''SELECT People.Name, People.Gender FROM People JOIN Cultures ON People.Culture = Cultures.Id WHERE Cultures.Name='American' '''
        results10 = cur.execute(sql10)
        results10_list = cur.fetchall()
        male = 0
        female = 0
        unknown = 0
        for i in results10_list:
            if i[1] == 'male':
                male += 1
            elif i[1] == 'female':
                female += 1
            else:
                unknown += 1
        self.assertEqual(male, 673)
        self.assertEqual(female, 461)
        self.assertEqual(unknown, 4054)

class TestObjectTable(unittest.TestCase):

    def test_object_table(self):
        conn = sqlite3.connect(DBNAME)
        cur = conn.cursor()

        sql11 = '''SELECT Objects.Title, Objects.Date, Objects.Medium FROM People JOIN Objects ON People.Id = Objects.Artist WHERE People.Name="Ellsworth Kelly"'''
        results11 = cur.execute(sql11)
        results11_list = cur.fetchall()
        titles = []
        dates = []
        mediums = []
        for item in results11_list:
            titles.append(item[0])
            dates.append(item[1])
            mediums.append(item[2])
        self.assertEqual(titles[2], 'Untitled (green)')
        self.assertEqual(len(dates), 31)
        self.assertEqual(mediums[11], 'Graphite on cream wove paper')

        conn.close()

unittest.main()
