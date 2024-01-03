import requests
import os
from bs4 import BeautifulSoup
import json
import time
import sys
all_clues = []
automated_game_id_start = int(sys.argv[1])

def get_final_jeopardy_clue(fj_block, final_jep_block_with_answer):
    final_jep_clue = fj_block.find('td', class_='clue_text')

    final_jep_clue_text = final_jep_block_with_answer.find("td")

    fj_correct_response_em = fj_block.find('em', {'class': 'correct_response'})
    fj_correct_response = None
    if fj_correct_response_em:
        fj_correct_response = fj_correct_response_em.get_text()

    # final_jep_souper = final_jep_clue_text.find("div")
    # final_jep_within_div = final_jep_souper['onmouseover']
    # final_jep_div_souper = BeautifulSoup(final_jep_within_div, 'html.parser')
    # final_jep_em = final_jep_div_souper.find('em', {'class': 'correct_response'}).get_text()

    return [final_jep_clue.get_text(), fj_correct_response] #Return final clue, final answer


def get_jeopardy_question_and_answer(clue_div, clue_snippet):


    rj_correct_response_em = clue_snippet.find('em', {'class': 'correct_response'})
    rj_correct_response = None
    if rj_correct_response_em:
        rj_correct_response = rj_correct_response_em.get_text()
    
    answer_in_td = BeautifulSoup(clue_snippet.find("td", class_="clue_text").get_text()) #gets the answer (question in general trivia term) of the clue in the <td>
    
    if not rj_correct_response:
        question_onmouseover = clue_div['onmouseover']
        question_souper = BeautifulSoup(question_onmouseover, 'html.parser')
        correct_response = question_souper.find('em', {'class': 'correct_response'})
        answer_in_td = BeautifulSoup(clue_snippet.find("td", class_="clue_text").get_text())

        return [answer_in_td.get_text(), correct_response.get_text()]

    return [answer_in_td.get_text(), rj_correct_response] #return clue question, clue answer

def get_category_names(full_html):
    #Get the Categories
    categories_html = full_html.find_all(class_='category_name')
    #keep the final seperate
    final_jeopardy_category = categories_html.pop().text
    categories = [] #Convert the HTML to just the text of the categories
    for category in categories_html:
        categories.append(category.text)

    return (categories, final_jeopardy_category) #return categories, FJ category

def check_if_double_jeopardy(clue_div):
    td_tag = clue_div.find('td', {'class': 'clue_unstuck'})
    td_id = td_tag['id']
    
    if "DJ" in td_id:
        return True

    return False

def check_valid_page(full_html):
    error_exists = full_html.find("p", class_='error')
    if (error_exists):
        print("ERROR!")
    else:
        print("NO ERROR")

def update_category_index(curr_index):
    if curr_index == 5:
        return 0
    else:
        curr_index += 1
        return curr_index

for curr_game_id in range(automated_game_id_start, automated_game_id_start + 1): #For every single game, we gotta check if cached, GET if not... Etc...
    all_clues = [] #Reset the all clues

    # URL of the web page you want to download
    url = f"https://www.j-archive.com/showgame.php?game_id={curr_game_id}"

    #Directory I am keeping this stuff in
    directory = "html_files"

    #attempt to open if already cached
    attempted_path = os.path.join(directory, f"game_{curr_game_id}.html")

    path_exists = os.path.isfile(attempted_path)

    if not path_exists:
        # Send a GET request to the URL to fetch the web page content
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Create a new directory in the current working directory to store the HTML file
            if not os.path.exists(directory):
                os.mkdir(directory) #Create the directory if it does not exist (Should not have to fire)

            # Write the contents of the response to a new HTML file in the directory
            file_path = os.path.join(directory, f"game_{curr_game_id}.html") #directory and html file with unique game code in it
            with open(file_path, "w", encoding="utf-8") as f: #open the file
                f.write(response.text) #write the response text (the html of the j-archive page)
            print(f"HTML content saved to {file_path}")
        else:
            print(f"Failed to download HTML content from {url}.")
            continue
    else:
        print("was able to cache!")

    test_file_path = os.path.join(directory, f"game_{curr_game_id}.html") #file path directory/game with unique code
    with open(test_file_path, "r", encoding='utf-8') as f: #open this unique game code page
        bsoup = BeautifulSoup(f.read(), "html.parser") #reads the file into a beautiful soup object

        #Check if this is actually a working game
        check_valid_page(bsoup)

        #Get the year, only have to do once
        game_year_title = bsoup.find("title").get_text()
        game_year = game_year_title[-10:-6]        

        categories_arr = get_category_names(bsoup)
        category_index = 0
        clue_order = 0
        regular_categories = categories_arr[0]
        FJ_category = categories_arr[1]
        current_categories = regular_categories[0:6]
        isDoubleJeopardy = False


        for clue_snippet in bsoup.find_all("td", class_='clue'): #looks at each <td> with class=clue one at a time
            
            current_clue_information = {}
            clue_game_id = f"{curr_game_id}"
            current_clue_information['clue_game_id'] = clue_game_id
            current_clue_information['game_year'] = game_year


            #Check for Daily Double instead of in the try-except
            clue_value_DD = clue_snippet.find("td", class_="clue_value_daily_double")
            if (clue_value_DD):
                
                #This is a Daily Double
                daily_double_question = clue_snippet.find("td", {'class': 'clue_text'})
                
                #DD_div = clue_snippet.find("div")
                #DD_onmouseover = DD_div['onmouseover']
                #DD_question_souper = BeautifulSoup(DD_onmouseover, 'html.parser')
                #DD_correct_response = DD_question_souper.find('em', {'class': 'correct_response'})
                

                DD_correct_response_em = clue_snippet.find('em', {'class': 'correct_response'})
                DD_correct_response = None
                if DD_correct_response_em:
                    DD_correct_response = DD_correct_response_em.get_text()

                #Also have to custom make this an object
                current_clue_information['clue_order'] = clue_order
                current_clue_information['category_order'] = category_index
                current_clue_information['clue_category'] = current_categories[category_index]
                current_clue_information['clue_question'] = daily_double_question.get_text()
                current_clue_information['clue_answer'] = DD_correct_response
                current_clue_information['clue_value'] = 'DD'
                current_clue_information['clue_round'] = 'single_jeopardy' if not isDoubleJeopardy else 'double_jeopardy'
                clue_order += 1
                category_index = update_category_index(category_index)
                all_clues.append(current_clue_information)
                continue

            #Check for FJ instead of in the try-except
            final_fj_check = clue_snippet.find('var', id='clue_FJ_stuck') #if this is in the snippet, we have reached final jeopardy
            if final_fj_check:

                #Answer is not in this snippet, bring the table to the function
                final_jep_block_with_answer = bsoup.find("table", {'class': "final_round"})
                final_jeopardy = get_final_jeopardy_clue(clue_snippet, final_jep_block_with_answer)
                final_jeopardy_clue = final_jeopardy[0] #clue
                final_jeopardy_answer = final_jeopardy[1] #answer

                #Make this an object
                current_clue_information['category_order'] = 6
                current_clue_information['clue_category'] = FJ_category
                current_clue_information['clue_question'] = final_jeopardy_clue
                current_clue_information['clue_answer'] = final_jeopardy_answer
                current_clue_information['clue_value'] = 'FINAL'
                current_clue_information['clue_round'] = 'final_jeopardy'
                all_clues.append(current_clue_information)

            try:

                #Getting the question (answer in trivia terms)
                
                clue_value = clue_snippet.find("td", class_="clue_value").get_text()
                current_clue_information['clue_value'] = clue_value
                
                question_div = clue_snippet.find("div") #first div holds the question, also in tandem checks if it exists too
        
                if not isDoubleJeopardy:
                    isDoubleJeopardy = check_if_double_jeopardy(question_div) #now true if is DJ
                    if isDoubleJeopardy:
                        current_categories = regular_categories[6:] #Change the categories to the DJ categories
                        category_index = 0
                
                clue_category = current_categories[category_index]
                current_clue_information['clue_category'] = clue_category
                        
                clue_round = 'single_jeopardy' if not isDoubleJeopardy else "double_jeopardy"
                current_clue_information['clue_round'] = clue_round

                clue_QA = get_jeopardy_question_and_answer(question_div, clue_snippet)
                clue_question = clue_QA[0] #question
                clue_answer = clue_QA[1] #answer

                current_clue_information['category_order'] = category_index
                current_clue_information['clue_question'] = clue_question
                current_clue_information['clue_answer'] = clue_answer
                current_clue_information['clue_order'] = clue_order
                
                all_clues.append(current_clue_information)
                clue_order += 1

                category_index = update_category_index(category_index)

            # Blank clue will do this, not every game has 60 clues, still have to update the category index    
            except (TypeError, AttributeError) as e:
                category_index = update_category_index(category_index)
                print(e)
                pass

    #Final
    json_directory = "json_clues" 
    json_file_path = os.path.join(json_directory, f"game_{curr_game_id}.json")
    with open(json_file_path, 'w') as f:
        json.dump(all_clues, f)
    
    print("game finished, delaying for next one")

    # For a lot of games, delay by 12 seconds
    time.sleep(3)