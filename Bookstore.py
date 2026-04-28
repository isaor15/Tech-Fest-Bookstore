import flet as ft
import sqlite3
import requests

conn = sqlite3.connect("BookStore.db")

cursor = conn.cursor()

createBooksTable = """
                CREATE TABLE IF NOT EXISTS Books(
                BookID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                BookTitle VARCHAR (50) NOT NULL,
                BookAuthor VARCHAR (50) NOT NULL,
                BookGenre VARCHAR (50) NOT NULL
                );
                """
cursor.execute(createBooksTable)


def main(page: ft.Page):

    page.fonts = {"Norge": "PlaywriteNO-VariableFont_wght.ttf"}
    page.theme = ft.Theme(font_family="Norge")

    def searchBook(e):
        try: 
            bookInfoLink = f"https://openlibrary.org/search.json?q={searchBarTexfield.value}"
            infoResponse = requests.get(bookInfoLink)
            coverID = infoResponse.json()["docs"][0]["cover_edition_key"]
            bookCoverLink = f"https://covers.openlibrary.org/b/olid/{coverID}.jpg"
            bookImage.src = bookCoverLink

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
ft.app(target=main)


#fixes:
#priorities
#add user info page
#add check out and return option
#fix the author and publishing year text bubble so it updates if no book is found


#just for funsies
#add music so the experience is enjoyable (reference music player from last year)
#find a picture for no book available in case the thing on top happens
