import flet as ft
import sqlite3
import requests
import datetime

#external resources used
#datetime and checkout time - https://www.youtube.com/watch?v=DwBDHsdX6XQ 
#fonts - https://flet.dev/docs/controls/page/#flet.Page.fonts
#scroll - https://flet.dev/docs/controls/scrollablecontrol/#flet.ScrollableControl.scroll

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

createCheckoutTable = """
                CREATE TABLE IF NOT EXISTS Checkout(
                TransactionID INTEGER PRIMARY KEY AUTOINCREMENT,
                UserID INTEGER NOT NULL,
                BookTitle VARCHAR (50) NOT NULL,
                BookAuthor VARCHAR (50) NOT NULL,
                CheckoutDate VARCHAR (50) NOT NULL,
                ReturnDate VARCHAR (50) NOT NULL,
                Status VARCHAR (20) DEFAULT 'Checked Out',
                FOREIGN KEY (UserID) REFERENCES Users(UserID)
                );
                """
cursor.execute(createCheckoutTable)

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
        checkoutBtn.visible = True
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
        
        insertFav = "INSERT INTO Favorites (UserID, BookTitle, BookAuthor) VALUES (?, ?, ?)"
        parameters = (curtUserID, titleText.value, authorText.value)
        cursor.execute(insertFav, parameters)
        conn.commit()

        resultText.value = "Your book has been added to favorites!:)"
        page.update()

    def checkoutBook(e):
        global curtUserID
        
        if curtUserID is None:
            resultText.value = "Please login first!"
            page.update()
            return
        
        if titleText.value == "Title:" or titleText.value == "":
            resultText.value = "You haven't looked up a book to check out yet!:/"
            page.update()
            return
        
        userBkCount = "SELECT BooksChecked FROM Users WHERE UserID = ?"
        parameters = (curtUserID,)
        cursor.execute(userBkCount, parameters)
        results = cursor.fetchone()
        booksChecked = results[0]
        
        if booksChecked >= 3:
            resultText.value = "Oops! It seems that you can't check out more than 3 books at a time!"
            page.update()
            return
        
        checkoutDate = datetime.date.today()
        today = checkoutDate.strftime("%d-%m-%Y")
        
        currDay = checkoutDate.day
        retDay = currDay + 14
        
        if retDay > 30:
            retDay = retDay - 30
            retMonth = checkoutDate.month + 1
        else:
            retMonth = checkoutDate.month
        
        if retMonth > 12:
            retMonth = 1
            return_year = checkoutDate.year + 1
        else:
            return_year = checkoutDate.year
        
        returnDate = f"{retDay}-{retMonth}-{return_year}"

        insertCheckout = "INSERT INTO Checkout (UserID, BookTitle, BookAuthor, CheckoutDate, ReturnDate, Status) VALUES (?, ?, ?, ?, ?, ?)"
        parameters = (curtUserID, titleText.value, authorText.value, today, returnDate, "Checked Out")
        cursor.execute(insertCheckout, parameters)
        conn.commit()

        addBkCount = booksChecked + 1
        
        updateUser = "UPDATE Users SET BooksChecked = ? WHERE UserID = ?"
        parameters = (addBkCount, curtUserID)
        cursor.execute(updateUser, parameters)
        conn.commit()
            
        resultText.value = f"Yay! Book checked out until {returnDate}! Have fun reading!"
        page.update()


    def seeFavs(e):
        favPg(page)
    
    def seeCheckout(e):
        checkedOutPg(page)

    seeFavsBTN = ft.ElevatedButton("See Favorites", on_click=seeFavs, bgcolor="white", color="brown")
    seeCheckoutBTN = ft.ElevatedButton("My Checked Out Books", on_click=seeCheckout, bgcolor="white", color="brown")

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

    checkoutBtn = ft.ElevatedButton("Checkout Book", on_click=checkoutBook, visible=False, bgcolor="white", color="brown")


    content = ft.Column([searchBarTexfield, resultBox, bookImage, titleText, authorBox, publishBox, 
                         ft.Row([favBtn, checkoutBtn], alignment=ft.MainAxisAlignment.CENTER),
                         ft.Row([seeFavsBTN, seeCheckoutBTN], alignment=ft.MainAxisAlignment.CENTER)], 
                        alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)


    background = ft.Stack([
            ft.Image(
                src="book_background.jpg",
                expand=True,
                fit="cover"),
            ft.Container(content=content, padding=20, expand=True, alignment=ft.Alignment.CENTER)])
    
    page.add(background)
    page.update()

def favPg(page):
    page.controls.clear()

    page.bgcolor = None
    page.background_image_src = "book_background.jpg"
    page.background_image_fit = "cover"

    def b2search(e):
        mainbookpg(page)

    selectFavs = "SELECT BookTitle, BookAuthor FROM Favorites WHERE UserID = ?"
    parameters = (curtUserID,)
    cursor.execute(selectFavs, parameters) 

    favBooks = cursor.fetchall()

    if not favBooks:
        noFavMSG = ft.Text("You haven't found your favorite books yet!", size=30, color="brown", text_align="center")
        goback = ft.ElevatedButton("Back to Search", on_click=b2search, bgcolor="white", color="brown")
        content = ft.Column([noFavMSG, ft.Container(height=20), goback], alignment=ft.MainAxisAlignment.CENTER)
        page.add(content)
        page.update()

    else:
        favList = []

        def removeBookFunc(BookTitle, BookAuthor):

            def actualBookRmv(e):
                deleteFav = "DELETE FROM Favorites WHERE UserID = ? AND BookTitle = ? AND BookAuthor = ?"
                parameters = (curtUserID, BookTitle, BookAuthor)
                cursor.execute(deleteFav, parameters)
                
                conn.commit()
                favPg(page)

            return actualBookRmv
            
        for book in favBooks:
                BookTitle, BookAuthor = book

                removeBtn = ft.ElevatedButton("Remove Book", on_click=removeBookFunc(BookTitle, BookAuthor), bgcolor="red", color="white")

                bookContainer = ft.Container(content=ft.Column([
                    ft.Text(f"Title: {BookTitle}", color="brown"),
                    ft.Text(f"Author: {BookAuthor}", color="brown"),
                    removeBtn]), bgcolor="white", padding=10,
                    border_radius=10, margin=5)
                
                favList.append(bookContainer)

        goback = ft.ElevatedButton("Back to Search", on_click=b2search, bgcolor="white", color="brown")
        favBookTtile = ft.Container(content=ft.Text("Your Favorite Books:", size=30, color="brown", text_align="center"), bgcolor="white", padding=10, border_radius=10, margin=5)
        listView = ft.ListView(controls=[favBookTtile] + favList + [goback], expand=True, spacing=10, padding=20, auto_scroll=True)
        
        page.add(listView)
        page.update()

def checkedOutPg(page):
    page.controls.clear()

    page.bgcolor = None
    page.background_image_src = "book_background.jpg"
    page.background_image_fit = "cover"

    def b2search(e):
        mainbookpg(page)

    selectCheckout = "SELECT BookTitle, BookAuthor, CheckoutDate, ReturnDate FROM Checkout WHERE UserID = ? AND Status = 'Checked Out'"
    parameters = (curtUserID,)
    cursor.execute(selectCheckout, parameters) 

    checkedBooks = cursor.fetchall()

    if not checkedBooks:
        noBooksMSG = ft.Text("You don't have any books checked out right now!", size=30, color="brown", text_align="center")
        goback = ft.ElevatedButton("Back to Search", on_click=b2search, bgcolor="white", color="brown")
        content = ft.Column([noBooksMSG, ft.Container(height=20), goback], alignment=ft.MainAxisAlignment.CENTER)
        page.add(content)
        page.update()

    else:
        bookList = []

        def returnBook(BookTitle, BookAuthor):

            def actualReturn(e):
                updateStatus = "UPDATE Checkout SET Status = 'Returned' WHERE UserID = ? AND BookTitle = ? AND BookAuthor = ? AND Status = 'Checked Out'"
                parameters = (curtUserID, BookTitle, BookAuthor)
                cursor.execute(updateStatus, parameters)
                conn.commit()
                
                getBooksChecked = "SELECT BooksChecked FROM Users WHERE UserID = ?"
                cursor.execute(getBooksChecked, (curtUserID,))
                result = cursor.fetchone()
                currentBooks = result[0]
                
                newBookCount = currentBooks - 1
                
                updateUser = "UPDATE Users SET BooksChecked = ? WHERE UserID = ?"
                parameters = (newBookCount, curtUserID)
                cursor.execute(updateUser, parameters)
                conn.commit()

                checkedOutPg(page)

            return actualReturn
            
        for book in checkedBooks:
            BookTitle, BookAuthor, CheckoutDate, ReturnDate = book

            returnBtn = ft.ElevatedButton("Return Book", on_click=returnBook(BookTitle, BookAuthor), bgcolor="green", color="white")

            bookContainer = ft.Container(content=ft.Column([ft.Text(f"Title: {BookTitle}", color="brown"),ft.Text(f"Author: {BookAuthor}", color="brown"),ft.Text(f"Checked Out: {CheckoutDate}", color="brown"),ft.Text(f"Due Date: {ReturnDate}", color="brown"),
                returnBtn]), bgcolor="white", padding=10,
                border_radius=10, margin=5)
            
            bookList.append(bookContainer)

        goback = ft.ElevatedButton("Back to Search", on_click=b2search, bgcolor="white", color="brown")
        checkedOutTitle = ft.Container(content=ft.Text("Your Checked Out Books:", size=30, color="brown", text_align="center"), bgcolor="white", padding=10, border_radius=10, margin=5)
        listView = ft.ListView(controls=[checkedOutTitle] + bookList + [goback], expand=True, spacing=10, padding=20, auto_scroll=True)
        
        page.add(listView)
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
        selectUser = "SELECT * FROM Users WHERE UserName = ? AND Password = ?"
        parameters = (userin, passin)
        cursor.execute(selectUser, parameters)
        userFound = cursor.fetchone()

        if userFound:
            curtUserID = userFound[0]
            print(f"User ID set to: {curtUserID}")
            successornot.value = f"Welcome back, {userin}!"
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

        checkUser = "SELECT * FROM Users WHERE UserName = ?"
        parameters = (userin,)
        cursor.execute(checkUser, parameters)
        takenuser = cursor.fetchone()

        if takenuser:
            successornot.value = "Oh no! It seems that the username is already taken :/"

        else:
            insertUser = "INSERT INTO Users (UserName, Password) VALUES (?, ?)"
            parameters = (userin, passin)
            cursor.execute(insertUser, parameters)
            conn.commit()

            selectUserID = "SELECT UserID FROM Users WHERE UserName = ?"
            parameters = (userin,)
            cursor.execute(selectUserID, parameters)
            newUser = cursor.fetchone()
            curtUserID = newUser[0]


            print(f"New User ID set to: {curtUserID}")
            successornot.value = f"A new account has been created. Let's get to reading, {userin}!"
            page.update()
            mainbookpg(page)


        page.update()

    loginButton = ft.ElevatedButton("Login", on_click=login, bgcolor="white", color="brown")
    signinButton = ft.ElevatedButton("Sign Up", on_click=signup, bgcolor="white", color="brown")

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
#have the add favorite books part only let you add one book
#add user info page
#add check out and return option
#one page with the welcome title and user login or sign up as well as the amount of books checked out or saved
#read later list
#another page with favorite, checked out, read later, and return date

#just for funsies
#add music so the experience is enjoyable (reference music player from last year)
#find a picture for no book available in case the thing on top happens CHECK 
