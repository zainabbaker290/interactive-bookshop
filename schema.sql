DROP TABLE IF EXISTS books;

CREATE TABLE books 
(
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    author TEXT NOT NULL,
    price REAL NOT NULL, 
    stars REAL NOT NULL,
    release_date TEXT,
    photo TEXT
);

INSERT INTO books (name, author, price, stars, release_date, photo)
VALUES  ('East of Eden', 'John Steinbeck', 4.99, 4.5, '1952-01-12', 'rsz_1rsz_eastofeden.jpg'),
        ('Mythos', 'Stephen Fry', 14.50, 3.2, '2017-09-02', 'rsz_2rsz_1mythos.jpg'),
        ('The Kite Runner', 'Khaled Housseini', 8.99, 4.4, '2003-05-29', 'rsz_1rsz_kiterunner.jpg'),
        ('The Reader', 'Bernard Schlink', 8.99, 3.5, '2002-06-27','rsz_1rsz_thereader.jpg'),
        ('Atonement', 'Ian McEwan', 12.50, 4.5, '1999-01-12','rsz_1rsz_atonement.jpg'),
        ('The Cockroach', 'Ian McEwan', 4.99, 2, '2017-06-17','rsz_1rsz_cockroach.jpg'),
        ('The Childrens Act', 'Ian McEwan', 9.99, 4.5, '2009-01-12','rsz_1rsz_childrensact.jpg'),
        ('The Great Gatsby', 'F. Scott. Fitzgerald', 4.99, 4.8, '1925-07-14','rsz_1rsz_gatsby.jpg'),
        ('A Thousand Splendid Suns', 'Khaled Housseini', 9.99, 4.5, '2008-06-12','rsz_1rsz_thousandsplendid.jpg');




DROP TABLE IF EXISTS users;

CREATE TABLE users
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    security_question TEXT NOT NULL,
    security_question_answer TEXT NOT NULL
);

DROP TABLE IF EXISTS events;

CREATE TABLE events
(
    event_name TEXT NOT NULL,
    event_date TEXT NOT NULL
);


INSERT INTO events (event_name, event_date)
VALUES ('Roald Dahl Reading for Children', '2021-08-12'),
       ('Book Swap', '2021-01-14'),
       ('World Book Day', '2021-02-10'),
       ('Local Poetry Readings', '2021-06-20'),
       ('Monthly Book Club Meeting', '2021-04-26'),
       ('Writing Work Shop', '2021-03-07');


DROP TABLE IF EXISTS reviews;

CREATE TABLE reviews
(
    book_name TEXT NOT NULL,
    author TEXT NOT NULL,
    stars REAL NOT NULL,
    review TEXT
);


INSERT INTO reviews (book_name, author, stars, review)
VALUES  ('East of Eden', 'John Steinbeck', 4.5, 'Steinbecks best work'),
        ('Mythos', 'Stephen Fry', 3.2, 'Easy read and captivating'),
        ('The Kite Runner', 'Khaled Housseini', 4.4, 'Remarkable and honest story'),
        ('East of Eden', 'John Steinbeck', 4.5, 'A thrilling classic');


DROP TABLE IF EXISTS orders;

CREATE TABLE orders
(
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NO NULL,
    title TEXT NOT NULL,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    address TEXT NOT NULL,
    country TEXT NOT NULL,
    card_name TEXT NOT NULL,
    card_number TEXT,
    expired TEXT,
    CVV TEXT,
    cart TEXT
);

SELECT *
FROM users;

