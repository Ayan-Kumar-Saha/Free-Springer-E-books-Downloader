from bs4 import BeautifulSoup
import requests
import os
import time
import pprint

URL = 'https://docs.google.com/spreadsheets/d/1HzdumNltTj2SHmCv3SRdoub8SvpIEn75fa4Q23x0keU/htmlview#gid=793911758'

pdf_base_URL = 'https://link.springer.com'

response = requests.get(URL)
response.raise_for_status()

soup = BeautifulSoup(response.content, 'lxml')

book_shelf = soup.find_all('tr')


def get_user_choice(books):

    print('---Welcome to Free Springer Book Store---')
    print('-----------------------------------------')
    print('******* Available E-Book Packages *******')
    print('-----------------------------------------')
    

    for package_name in books:
        print('| {} '.format(package_name), end = '\n\n')

    while True:
        print('\nPress 1: Download E-Books from ALL packages')
        print('Press 2: Download E-Books from SPECIFIC packages')
        print('Press 0: Quit')

        choice = int(input('\nEnter your choice: '))

        if choice not in (1, 2, 0):
            print('\nWrong choice!! Enter again!!\n')
        else:
            break

    return choice


def collect_books_data():

    books = dict()

    for row in book_shelf[3:]:

        columns = row.find_all('td')
        book_title = columns[0].text
        author = columns[1].text
        package_name = columns[2].text
        book_download_link = columns[3].text
        
        if package_name not in books:

            books[package_name] = dict()

        if book_title not in books[package_name]:

            books[package_name][book_title] = {
                        'Author': author,
                        'Book Download Link': book_download_link
                }

    return books
    

def download_books(books):

    global pdf_base_URL

    for package_name in books:

        directory_path = os.path.join(os.getcwd(), package_name)

        if not os.path.exists(directory_path):
            os.mkdir(directory_path)

        for book_title in books[package_name]:

            file_name = book_title + '_by_' + books[package_name][book_title]['Author'] + '.pdf'
            
            if len(file_name.split('/')) > 1:
                        file_name = ' or '.join(file_name.split('/'))

            file_path = os.path.join(directory_path, file_name)

            print('\nChecking STATUS for {} -> '.format(book_title), end = '')
            time.sleep(1)

            try :

                if not os.path.exists(file_path):

                    print("NOT FOUND\n")
                    time.sleep(1)

                    print('Downloading {}...'.format(book_title))

                    download_site_response = requests.get(books[package_name][book_title]['Book Download Link'])
                    download_site_response.raise_for_status()

                    soup2 = BeautifulSoup(download_site_response.content, 'lxml')

                    links = soup2.select('a[data-track-action="Book download - pdf"]')

                    pdf_query_URL = links[0]['href']

                    pdf_response = requests.get(pdf_base_URL + pdf_query_URL, 'lxml')
                    pdf_response.raise_for_status()

                    with open(file_path, 'wb') as pdf_file:
                        
                        for chunk in pdf_response.iter_content(100000):
                            pdf_file.write(chunk)

                    print('{} DOWNLOAD STATUS: OK!!'.format(book_title))

                else:

                    print('FOUND\n')
                    time.sleep(1)

            except Exception as e:

                print('\nSome ERROR occurred while downloading {}'.format(book_title))

def main():

    books = collect_books_data()

    choice = get_user_choice(books)

    if choice == 0:   
        exit()

    elif choice == 1:
        download_books(books)

    else: 

        print("\n* Enter package names carefully!! Names are CASE SENSITIVE!!")
        print("* PUT Comma(,) between in case of multiple package names !!")
        packages = input('\nEnter package name(s): ')

        packages = packages.split(',')

        for i in range(len(packages)):
            packages[i] = packages[i].strip()

        books2 = dict()

        for package_name in packages:

            books2[package_name] = books[package_name]

        download_books(books2)

    print('Download complete successfully!!')

main()


