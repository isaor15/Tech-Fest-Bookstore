import flet as ft
import sqlite3
import requests

conn = sqlite3.connect("BookStore.db")

cursor = conn.cursor()

#SQL tables
createBooksTable = """
                CREATE TABLE IF NOT EXISTS Books(
                BookID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                BookTitle VARCHAR (50) NOT NULL,
                BookAuthor VARCHAR (50) NOT NULL,
                BookGenre VARCHAR (50) NOT NULL
                );
                """
cursor.execute(createBooksTable)

addUsertable = """
                CREATE TABLE IF NOT EXISTS Users(
                UserID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                UserName VARCHAR (50) NOT NULL,
                Password VARCHAR (50) NOT NULL,
                BooksChecked INTEGER DEFAULT 0
                );
                """
cursor.execute(addUsertable)


#booksearch stuff
def mainbookpg(page):

    page.controls.clear()

    def searchBook(e):
        try: 
            bookInfoLink = f"https://openlibrary.org/search.json?q={searchBarTexfield.value}"
            infoResponse = requests.get(bookInfoLink)
            bookData = infoResponse.json()["docs"][0]
            bookCover = "noImage.jpg"

            if "cover_edition_key" in bookData:
                coverID = bookData["cover_edition_key"]
                bookCover = f"https://covers.openlibrary.org/b/olid/{coverID}.jpg"

            elif "cover_i" in bookData:
                coverID = bookData["cover_i"]
                bookCover = f"https://covers.openlibrary.org/b/olid/{coverID}.jpg"

            bookImage.src = bookCover

            publishYear.value = infoResponse.json()["docs"][0]["first_publish_year"]
            authorText.value = infoResponse.json()["docs"][0]["author_name"]
            titleText.value = infoResponse.json()["docs"][0]["title"]


        except:
            resultText.value = "Something went wrong, we don't have that book!"
            authorText.value = "Author not found!"
            publishYear.value = "Publishing year not found!"
            bookImage.src = "empty_book.jpg"
        else:
            resultText.value = "Book found!"

        page.update()


    searchBarTexfield = ft.TextField(
            hint_text="Look for your book", width=250, 
            text_align="center", border_radius=20,bgcolor="white",
            color="black",
            on_submit=searchBook)
    
    resultText = ft.Text(value="", color="black", text_align="center")

    resultBox = ft.Container(content=resultText, width=250, border_radius=20, bgcolor="white", padding=20)

    bookImage = ft.Image(src="noImage.png", height=250, width=250)

    authorText = ft.Text(value="Author:", color="black")

    authorBox = ft.Container(content=authorText,width=250, border_radius=20, bgcolor="white", padding=20)

    titleText = ft.Text(value="Title:", color="black")

    publishYear = ft.Text(value="Published:", color="black")
    
    publishBox = ft.Container(content=publishYear,width=250, border_radius=20, bgcolor="white", padding=20)


    background = ft.Stack([
            ft.Image(
                src="book_background.jpg",
                expand=True,
                fit="cover"),
            ft.Container(content=ft.Column([searchBarTexfield,resultBox, bookImage,authorBox, publishBox]), padding=20)])
    page.add(background)
    page.update()


#Login stuff and welcome page
def welcome(page):

    page.controls.clear()

    welcome = ft.Text("Welcome to Isabella's Bookstore!", size=45, color = "white", text_align="center")
    addUser = ft.TextField(hint_text="Username", width=250)
    addPassword = ft.TextField(hint_text="Password", password=True, width=250)
    successornot = ft.Text("", color="white", size=16)

    def login(e):

        userin = addUser.value
        passin = addPassword.value
        cursor.execute("SELECT * FROM Users WHERE UserName = ? AND Password = ?", 
                    (userin, passin))
        userFound = cursor.fetchone()

        if userFound:
            successornot.value = f"Welcome back to Isa's Bookshop, {userin}!"
            page.update()
            mainbookpg(page)

        else: 
            successornot.value = "Your username or password is wrong:("
        page.update()


    def signup(e):

        userin = addUser.value
        passin = addPassword.value

        if userin == "" or passin == "":
            successornot.value = "Please fill in both requirements!"
            page.update()
            return

        cursor.execute("SELECT * FROM Users WHERE UserName = ?", (userin,))
        takenuser = cursor.fetchone()

        if takenuser:
            successornot.value = "Oh no! It seems that the username is already taken :/"

        else:
            cursor.execute("INSERT INTO Users (UserName, Password) VALUES (?, ?)", (userin, passin))
            conn.commit()
            successornot.value = f"A new account has been created. Let's get to reading, {userin}!"
            page.update()
            mainbookpg(page)


        page.update()

    loginButton = ft.ElevatedButton("Login", on_click=login)
    signinButton = ft.ElevatedButton("Sign Up", on_click=signup)

    allstuff = ft.Column([
        welcome, ft.Container(height=20), addUser, addPassword, successornot, ft.Row([loginButton, signinButton])
    ])

    background = ft.Stack([ft.Image(src="book_background.jpg", expand=True, fit="cover"), ft.Container(content=allstuff, padding=20)])
    page.add(background)
    page.update()

                      
#Main function
def main(page: ft.Page):

    page.fonts = {"Norge": "PlaywriteNO-VariableFont_wght.ttf"}
    page.theme = ft.Theme(font_family="Norge")

    welcome(page)

ft.app(target=main)


#fixes:
#priorities
#add user info page
#change the olid cover image so any book cover can appear CHECK
#add check out and return option
#do the page.clear.controls to create new pages
#one page with the welcome title and user login or sign up as well as the amount of books checked out or saved
#read later list
#another page with favorite, checked out, read later, and return date
#fix the author and publishing year text bubble so it updates if no book is found CHECK 


#just for funsies
#add music so the experience is enjoyable (reference music player from last year)
#find a picture for no book available in case the thing on top happens CHECK 
