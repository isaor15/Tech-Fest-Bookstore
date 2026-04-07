import flet
import sqlite3

conn = sqlite3.connect("BookStore.db")

cursor = conn.cursor()

createBooksTable = """
                CREATE TABLE IF NOT EXISTS Books(
                BookID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                BookTitle VARCHAR (50) NOT NULL,
                BookPrice REAL NOT NULL,
                BookQuantity INTEGER NOT NULL
                );
                """

cursor.execute(createBooksTable)

while True:
    print("Isabella's Bookstore")
    print("1. View books")
    print("2. Add new book")
    print("3. Update book")
    print("4. Delete book")
    print("5. Exit")
    decision = input("What will you be doing? ")
    print("------------------------------------")

    match decision:
        case "1":
            selectBooks = "SELECT * FROM Books"
            cursor.execute(selectBooks)

            results = cursor.fetchall()
            for r in results:
                print (r)

        case "2":
            BookTitle = input("What is the book's title? ")
            BookPrice = float(input("What is the book's price? "))
            BookQuantity = int(input("What is the amount of copies of the book? "))
            
            insertBooks = "INSERT INTO Books (BookTitle, BookPrice, BookQuantity) VALUES (?,?,?)"
            parameters = (BookTitle, BookPrice, BookQuantity)

            cursor.execute(insertBooks, parameters)

        case "3":
            BookID = input("Insert the ID of the book you'd like to update: ")

            BookTitle = input("What is the book's title?")
            BookPrice = float(input("What is the book's price?"))
            BookQuantity = int(input("What is the amount of copies of the book?"))

            updateBooks = """
                            UPDATE Books SET
                            BookTitle = ?,
                            BookPrice = ?,
                            BookQuantity = ?
                            WHERE BookID = ?
                            """
            
            parameters = (BookTitle, BookPrice, BookQuantity, BookID)
            cursor.execute(updateBooks, parameters)

        case "4":
            BookID = input("Insert the ID of the book you'd like to delete: ")
            deleteBook = "DELETE FROM Books WHERE BookID = ?"
            parameters = (BookID, )

            cursor.execute(deleteBook, parameters)

        case "5":
            break

        case _: 
            print("This isn't an option")

conn.commit()
print("------------------------------------")
