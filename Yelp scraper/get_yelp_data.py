import requests
import decimal
import csv

available_cuisines = ['french', 'chinese', 'japanese', 'italian', 'spanish', 'indian', 'mexican']
location = 'manhattan'
restaurants = {}

file = open('yelp_data.csv', 'a', encoding='utf-8')
writer = csv.writer(file)
id = []

for cuisine in available_cuisines:
    for offset in range(0, 999, 50):
        params = {
            'term': cuisine,
            'location': location,
            'offset': offset,
            'limit': 50
        }

        headers = {
            'Authorization': 'Bearer zXFRtmYmszpOYrzgpsVCnWuQ1xmyWlQu9jYtRrrg_TLdLVpC9oxevFPkhTMEHeiJp0_FItPCmtAXHhuVMrBbOhRVHGJv_XhbD4OlxGprOfu_qewAEhx24PEKh5H1Y3Yx'
        }

        response = requests.get(url='https://api.yelp.com/v3/businesses/search', params=params, headers=headers)
        restaurants = response.json()['businesses']
        for restaurant in restaurants:
            if restaurant['id'] not in id:
                id.append(restaurant['id'])
                writer.writerow([restaurant['id'], restaurant['name'], cuisine, ", ".join(restaurant['location']['display_address']),
                                 decimal.Decimal(str(restaurant['coordinates']['latitude'])), decimal.Decimal(str(restaurant['coordinates']['longitude'])),
                                 decimal.Decimal(str(restaurant['rating'])), restaurant['review_count'], restaurant['location']['zip_code']])
