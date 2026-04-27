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
            resultText.value = "Something went wrong!"
        else:
            resultText.value = "Book found!"

    page.update()


    searchBarTexfield = ft.TextField(
            hint_text="Look for your book", width=250, 
            text_align="center", border_radius=20,bgcolor="white",
            font_family="Norge",
            on_submit=searchBook
        )
    resultText = ft.Text(value="")
    bookImage = ft.Image(src="noImage.png", height=500, width=500)
    authorText = ft.Text(value="Author:")
    titleText = ft.Text(value="Title:")
    publishYear = ft.Text(value="Published:")

    background = ft.Stack([
            ft.Image(
                src="book_background.jpg",
                expand=True,
                fit="cover"),
            ft.Container(content=ft.Column([searchBarTexfield,resultText, bookImage,authorText, titleText, publishYear ]), padding=20)])

    page.add(background)
ft.app(target=main)


