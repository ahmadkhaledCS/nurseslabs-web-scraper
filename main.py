import os
import shutil
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from questions import Answer, Question
import openpyxl
import re

MAIN_PAGE = 'https://nurseslabs.com/'
X_PATHS = ['//*[@id="menu-main-menu-1"]/li[2]/ul/li/a',
           '/html/body/div/div/div/main/article/div/div/ul[1]/li/a',
           '/html/body/div/div/div/main/article/div/div/ol[1]/li/a',
           '/html/body/div[1]/div/div[1]/main/article/div/div[2]/ul[1]/li/strong/a',
           '/html/body/div[1]/div/div[1]/main/article/div/div[2]/ol[1]/li/strong/strong/a', ]
driver = webdriver.Chrome()
driver.set_window_position(0, 0)
# anything
driver.set_window_size(760, 820)


def get_exams_links(main_link):
    pattern = re.compile(main_link + '\\d+/$|' + main_link)
    links = list()
    for i in range(1, 5):
        temp_links = driver.find_elements(By.XPATH, X_PATHS[i])
        if temp_links:
            loop(links, temp_links, pattern)
    return links


def loop(links, _topics, pattern):
    for top in _topics:
        link = top.get_attribute('href')
        if re.match(pattern, link):
            links.append(link)


def get_main_topics():
    driver.get(MAIN_PAGE)
    _topics = list()
    for _topic in driver.find_elements(By.XPATH, X_PATHS[0])[1:24]:
        _topics.append(_topic.get_attribute('href'))
    return _topics


def get_button(_name):
    elements = driver.find_elements(By.TAG_NAME, 'input')
    driver.implicitly_wait(10)
    for element in elements:
        if element.get_attribute('value') == _name:
            return element


def try_to_click(button, wait_for=0):
    time.sleep(wait_for)
    _name = button.get_attribute('value')
    try:
        button.click()
        print(f'found and clicked on {_name}')
    except:
        input(f'cant find the {_name} button go click it and enter any key\n')


def click_buttons(link):
    driver.get(link)
    for button_name in ['Quiz Summary', 'Finish Quiz', 'View Questions']:
        button = get_button(button_name)
        if button:
            try_to_click(button, 2)


def add_data():
    global index
    global number_of_questions
    sheet = work_book['With feedback']
    questions = driver.find_elements(By.CLASS_NAME, 'wpProQuiz_listItem')
    number_of_single_choice = 0
    for question in questions:
        text = question.find_element(By.CLASS_NAME, 'wpProQuiz_question_text')
        answers = question.find_elements(By.CLASS_NAME, 'wpProQuiz_questionListItem')
        response = question.find_element(By.CLASS_NAME, 'wpProQuiz_response')
        q = Question(text.text, [], response.text)
        number_of_correct_answers = 0
        if len(answers) != 4:
            continue
        for answer in answers:
            text = answer.text.split('.')
            if answer.get_attribute('class') == 'wpProQuiz_questionListItem wpProQuiz_answerCorrectIncomplete':
                q.right_answer = Answer('.'.join(text[1:]), text[0], 'correct')
                number_of_correct_answers += 1
            else:
                q.answers.append(Answer('.'.join(text[1:]), text[0], 'wrong'))
        if number_of_correct_answers == 1:
            number_of_single_choice += 1
            index += 1
            q.set_rationals()
            wrongs = q.answers
            sheet[f'B{index}'] = q.text
            sheet[f'C{index}'] = q.right_answer.text
            sheet[f'D{index}'] = q.right_answer.rational
            sheet[f'E{index}'] = wrongs[0].text
            sheet[f'F{index}'] = wrongs[0].rational
            sheet[f'G{index}'] = wrongs[1].text
            sheet[f'H{index}'] = wrongs[1].rational
            sheet[f'I{index}'] = wrongs[2].text
            sheet[f'J{index}'] = wrongs[2].rational
        number_of_questions += 1
    print(f'added {number_of_single_choice} questions from link')


def make_new_file(_name):
    src_dir = os.getcwd()
    dest_dir = src_dir + "/banks"
    src_file = os.path.join(src_dir, 'sheet.xlsx')
    shutil.copy(src_file, dest_dir)
    dst_file = os.path.join(dest_dir, 'sheet.xlsx')
    new_dst_file_name = os.path.join(dest_dir, f'{_name}.xlsx')
    os.rename(dst_file, new_dst_file_name)


if __name__ == '__main__':
    main_topics = get_main_topics()
    for topic in [main_topics[0]]:
        name = str(topic).split("/")[3]
        print(f'adding data to {name}.xlsx')
        make_new_file(name)
        work_book = openpyxl.load_workbook(f'banks/{name}.xlsx')
        driver.get(topic)
        index = 7
        number_of_questions = 0
        for exam in get_exams_links(topic):
            print(f'working on {exam}')
            click_buttons(exam)
            print('adding single choice questions....')
            add_data()

        print(f'added {number_of_questions} questions to {name}.xlsx')
        work_book.save(f'banks/{name}.xlsx')
        print('--------------------------------------')
    driver.close()
