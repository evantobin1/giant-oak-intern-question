from bs4 import BeautifulSoup
import json
import requests
import re
import os


os.chdir(os.path.dirname(os.path.abspath(__file__)))



def scrape_website(website_name, main_url):
    main_page = requests.get(main_url)

    info = {
        "source_code": os.path.basename(__file__),
        "source_name": website_name,
        "source_url": main_url,
        "persons": []
    }

    soup = BeautifulSoup(main_page.content, 'html.parser')


    # On the main website, there is a list of the most wanted. To view the attributes, 
    # the code must enter each sub_page. This will be done here.
    for person in soup.find_all(class_='views-row'):

        # Get the html from each subpage
        subPage = requests.get(person.find('a', href=True)['href'])
        soup = BeautifulSoup(subPage.content, 'html.parser')
        subPageContent = str(soup.find(class_='wanted_top_right'))


        # Every field that is provided about an individual is provided in the naming convention: 'field field-name-FIELD_GOES_HERE'
        # Get a list of the provided field names to use as keys for the dictionary
        fields = []
        pretext = 'field field-name-'
        for match in re.finditer(pretext, subPageContent):
            fields.append(subPageContent[match.end():subPageContent.find('wrapper', match.end()) + len('wrapper')])


        # Every field's value will be placed within this dict
        # We will update the final 'info' dict with this entry later
        info_on_person = {
            'firstname': '',
            'lastname': '',
            'about': {
                "date-of-birth": "unknown",
                "ethnic-origin": "unkown",
                "nationality": "unkown",
                "gender": "unkown"
            },
            'other': {}
        }

        for field in fields:
            # Get datafield
            data_in_field = soup.find(class_='field field-name-' + field)
            if data_in_field == None:
                continue

            # Beautify the field names
            field = field[:field.index(' ')].replace('field-', '').replace('-field', '')

            # Convert to string
            data_in_field = str(data_in_field).encode('UTF-8', errors='backslashreplace').decode('UTF-8')

            # All of the values that we will search for will be listed after one of the following strings
            pretext = '"field-item even">|"field-item odd">|<h2>|"dc:date">'

            # Look for the data corresponding to the field
            for match in re.finditer(pretext, data_in_field):

                value = data_in_field[match.end(): data_in_field.find('</', match.end())]

                # In the HTML, the name is provided in the format {title: 'LASTNAME, FIRSTNAME'}
                # Change the format to {firstname: 'FIRSTNAME', lastname: 'LASTNAME'}
                if field == 'title':
                    try:
                        info_on_person.update({'firstname': value[value.index(', ') + 2:]})
                        info_on_person.update({'lastname': value[:value.index(',')]})
                        break
                    except ValueError as e:
                        # The 'last, first' format is not applicable, simply place the entire provided name in the 'lastname' portion
                        info_on_person.update({'lastname': value})
                        break

                # Where in the dict should this info be placed
                if field in info_on_person['about']:
                    info_on_person['about'].update({field: value})
                else:
                    info_on_person['other'].update({field: value})
        
        # Place the data into the main dict
        print('Adding the info for ' + info_on_person['firstname'] + ' ' + info_on_person['lastname'])
        info['persons'].append(info_on_person)

    return info


if __name__ == '__main__':
    main_url = 'https://eumostwanted.eu/'
    
    # Get the info from the website in the form of a dict
    info = scrape_website(website_name='EU Most Wanter', main_url=main_url)

    # Place the data from the 'info' dict into the jsonFile
    jsonFile = open("results.json", "w", encoding="utf-8")
    json.dump(info, jsonFile, indent=4, ensure_ascii=False)
    jsonFile.close()



    

