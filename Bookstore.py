import flet as ft
import sqlite3
import requests

conn = sqlite3.connect("Library.db")

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

addFavoritesTable = """
                    CREATE TABLE IF NOT EXISTS Favorites(
                    FavoriteID INTEGER PRIMARY KEY AUTOINCREMENT,
                    UserID INTEGER NOT NULL,
                    BookTitle VARCHAR (50) NOT NULL, 
                    BookAuthor VARCHAR (50) NOT NULL
                    );
                    """
cursor.execute(addFavoritesTable)

curtUserID = None



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
            authorText.value = infoResponse.json()["docs"][0]["author_name"][0]
            titleText.value = infoResponse.json()["docs"][0]["title"]


        except:
            resultText.value = "Something went wrong, we don't have that book!"
            authorText.value = "Author not found!"
            publishYear.value = "Publishing year not found!"
            bookImage.src = "empty_book.jpg"
        else:
            resultText.value = "Book found!"

        page.update()

        favBtn.visible = True
        page.update()

    def addfav(e):
        global curtUserID

        if curtUserID is None:
            resultText.value = "You must login first!"
            page.update()
            return

        if titleText.value == "Title:" or titleText.value == "":
            resultText.value = "You haven't searched for a book to add to favorites yet!"
            page.update()
            return
        
        cursor.execute("INSERT INTO Favorites (UserID, BookTitle, BookAuthor) VALUES (?, ?, ?)",
                       (curtUserID, titleText.value, authorText.value))
        conn.commit()

        resultText.value = "Your book has been added to favorites!:)"
        page.update()

    def seeFavs(e):
            favPg(page)

    seeFavsBTN = ft.ElevatedButton("See Favorites", on_click=seeFavs, bgcolor="white", color="brown")


    searchBarTexfield = ft.TextField(
            hint_text="Look for your book", width=250, 
            text_align="center", border_radius=20,bgcolor="white",
            color="brown",
            on_submit=searchBook)
    
    resultText = ft.Text(value="", color="brown", text_align="center")

    resultBox = ft.Container(content=resultText, width=250, border_radius=20, bgcolor="white", padding=20)

    bookImage = ft.Image(src="noImage.png", height=250, width=250)

    authorText = ft.Text(value="Author:", color="brown")

    authorBox = ft.Container(content=authorText,width=250, border_radius=20, bgcolor="white", padding=20)

    titleText = ft.Text(value="Title:", color="brown")

    publishYear = ft.Text(value="Published:", color="brown")
    
    publishBox = ft.Container(content=publishYear,width=250, border_radius=20, bgcolor="white", padding=20)

    favBtn = ft.ElevatedButton("Add to favorites", on_click=addfav, visible=False, bgcolor="white", color="brown")


    background = ft.Stack([
            ft.Image(
                src="book_background.jpg",
                expand=True,
                fit="cover"),
            ft.Container(content=ft.Column([searchBarTexfield,resultBox, bookImage,authorBox, publishBox, ft.Row([favBtn, seeFavsBTN], alignment=ft.MainAxisAlignment.CENTER)]), padding=20)])
    page.add(background)
    page.update()

def favPg(page):
    page.controls.clear()

    def remveFav(e, BookTitle, BookAuthor):
        cursor.execute("DELETE FROM Favorites WHERE UserID = ? AND BookTitle = ?",
                       (curtUserID, BookTitle, BookAuthor))
        conn.commit()
        favPg(page)

    def b2search(e):
        mainbookpg(page)

    cursor.execute("SELECT BookTitle, BookAuthor FROM Favorites WHERE UserID = ?", 
                   (curtUserID,))   

    favBooks = cursor.fetchall()

    if not favBooks:
        noFavMSG = ft.Text("You haven't found your favorite books yet!", size=30, color="brown", text_align="center")
        goback = ft.ElevatedButton("Back to Search", on_click=b2search)
        content = ft.Column([noFavMSG, ft.Container(height=20), goback], alignment=ft.MainAxisAlignment.CENTER)

    else:
        favList = []

        def removeBookFunc(BookTitle, BookAuthor):

            def actualBookRmv(e):
                cursor.execute("DELETE FROM Favorites WHERE UserID = ? AND BookTitle = ? AND BookAuthor = ?", 
                               (curtUserID, BookTitle, BookAuthor))
                
                conn.commit()
                favPg(page)

            return actualBookRmv
            
        for book in favBooks:
                BookTitle, BookAuthor = book

                removeBtn = ft.ElevatedButton("Remove Book", on_click=removeBookFunc(BookTitle, BookAuthor), bgcolor="red", color="white")

                bookContainer = ft.Container(content=ft.Column([ft.Text(f"Title: {BookTitle}"), ft.Text(f"Author: {BookAuthor}"), removeBtn]), bgcolor="white", padding=10,
                                              border_radius=10, margin=5)
                
                favList.append(bookContainer)

        goback = ft.ElevatedButton("Back to Search", on_click=b2search, bgcolor="white", color="brown")
        content = ft.Column([ft.Text("Your Favortie Books: ")] + favList + [goback])

        bg = ft.Stack([ft.Image(src="book_background.jpg", expand=True, fit="cover"), ft.Container(content=content, padding=20)])
        page.add(bg)
        page.update()
    



#Login stuff and welcome page
def welcome(page):

    page.controls.clear()

    welcome = ft.Text("Welcome to Isabella's Library!", size=45, color = "white", text_align="center")
    addUser = ft.TextField(hint_text="Username", width=250)
    addPassword = ft.TextField(hint_text="Password", password=True, width=250)
    successornot = ft.Text("", color="white", size=16)

    def login(e):
        global curtUserID

        userin = addUser.value
        passin = addPassword.value
        cursor.execute("SELECT * FROM Users WHERE UserName = ? AND Password = ?", 
                    (userin, passin))
        userFound = cursor.fetchone()

        if userFound:
            curtUserID = userFound[0]
            print(f"User ID set to: {curtUserID}")
            successornot.value = f"Welcome back to Isa's Bookshop, {userin}!"
            page.update()
            mainbookpg(page)

        else: 
            successornot.value = "Your username or password is wrong:("
        page.update()


    def signup(e):
        global curtUserID

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

            cursor.execute("SELECT UserID FROM Users WHERE UserName = ?", (userin,))
            newUser = cursor.fetchone()
            curtUserID = newUser[0]


            print(f"New User ID set to: {curtUserID}")
            successornot.value = f"A new account has been created. Let's get to reading, {userin}!"
            page.update()
            mainbookpg(page)


        page.update()

    loginButton = ft.ElevatedButton("Login", on_click=login)
    signinButton = ft.ElevatedButton("Sign Up", on_click=signup)

    allstuff = ft.Column([
        welcome, ft.Container(height=20), addUser, addPassword, successornot, ft.Row([loginButton, signinButton], alignment=ft.MainAxisAlignment.CENTER)
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

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
