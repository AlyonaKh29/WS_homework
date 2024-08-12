import requests
from bs4 import BeautifulSoup
import fake_headers
import time
import re
import json


def add_keys_to_url(*args):
    # Добавляем ключевые слова для поиска вакансий в строку url.
    text = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'.split('&')
    keywords = '+'.join(args)
    return f'{text[0]}+{keywords}&{text[1]}&{text[2]}'


def parse_website_hh(url):
    # Парсим страницу hh.ru с поиском по "Python" и городами "Москва" и "Санкт-Петербург".
    headers = fake_headers.Headers(browser='chrome', os='win')
    main_html = requests.get(url, headers=headers.generate()).text
    main_soup = BeautifulSoup(main_html, features='lxml')
    data_list = main_soup.find_all(class_="vacancy-card--z_UXteNo7bRGzxWVcL7y font-inter")
    return data_list    # Получаем список всех блоков с вакансиями.


def parse_vacancies(data_list):
    parsed_data = []
    # Итерируем по списку с блоками вакансий: находим ссылки на страницы с описанием вакансий.
    for element in data_list:
        time.sleep(2)
        link = element.find('a', class_="bloko-link")['href']
        # На странице с описанием вакансии находим все нужные данные и записываем в словарь.
        data_dict = get_vacancy_info(link)
        if data_dict:
            parsed_data.append(data_dict)    # Словарь добавляем в общий список с информацией обо всех вакансиях.
    return parsed_data


def get_vacancy_info(url):
    #  Парсим страницу с описанием вакансии.
    headers = fake_headers.Headers(browser='chrome', os='win')
    html = requests.get(url, headers=headers.generate()).text
    soup = BeautifulSoup(html, features='lxml')
    time.sleep(1)
    # Сохраняем название вакансии.
    vacancy = soup.find('h1', class_='bloko-header-section-1').text.strip()
    # Сохраняем название компании.
    company = soup.find('span', class_='bloko-header-section-2 bloko-header-section-2_lite').text.strip().replace('\xa0', ' ')
    time.sleep(1)
    # Сохраняем указанные данные о зарплате.
    salary = soup.find('span', class_='magritte-text___pbpft_3-0-13 magritte-text_style-primary___AQ7MW_3-0-13 magritte-text_typography-label-1-regular___pi3R-_3-0-13').text
    # Находим тэги, в которых может быть указан город.
    loc = soup.find('div', class_='vacancy-company-redesigned')
    location_1 = loc.find(class_='magritte-text___pbpft_3-0-13 magritte-text_style-primary___AQ7MW_3-0-13 magritte-text_typography-paragraph-2-regular___VO638_3-0-13')
    location_2 = loc.find(class_='magritte-text___tkzIl_4-2-4')
    # Проверяем, соответствует ли город условиям поиска.
    city = select_city(location_1, location_2)
    if city:   # Если город правильный, возвращаем словарь с данными о вакансии.
        return {vacancy: {"url": url, "company": company, "city": city, "salary": salary.replace('\xa0', ' ')}}


def select_city(*args, pattern='Москва|Санкт-Петербург'):
    # Проверяем, соответствует ли город условиям поиска.
    city = []
    for el in args:
        loc = re.findall(pattern, f'{el}')
        city.extend(loc)
    return city[0] if city else None


def create_json_file(file_path, parsed_data):
    # Сохраняем список с данными о найденных вакансиях в json-файл.
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(parsed_data, file, ensure_ascii=False, indent=2)


def main():
    try:
        html = add_keys_to_url('Django', 'Flask')
        data = parse_website_hh(html)
        dict_info = parse_vacancies(data)
        create_json_file('vacancies.json', dict_info)
        print('Парсинг завершён')
    except TypeError or AttributeError:
        # Ошибка, которая может бессистемно возникнуть. Не знаю, что с ней делать.
        print(f"Попробуйте ещё")


if __name__ == "__main__":
    main()
