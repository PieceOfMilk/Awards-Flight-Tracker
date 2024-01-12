import json
import requests 
import time
import calendar
import webbrowser


def create_json_string(origin, dest, start):
    data = {
        "metadata": {
            "selectedProducts": [],
            "tripType": "OneWay",
            "udo": {
                "requestHeader": {
                    "clientId": "AAcom"
                },
                "channel": "Booking",
                "event_name": "award",
                "page_name": "Choose Flights",
                "event_action": "View",
                "event_category": "Calendar",
                "spa_session_id": "0aa221f0-90fc-4d46-95d8-c4a296e58797"
            }
        },
        "passengers": [
            {
                "type": "adult",
                "count": 1
            }
        ],
        "requestHeader": {
            "clientId": "AAcom"
        },
        "slices": [
            {
                "allCarriers": True,
                "cabin": "",
                "departureDate": start,
                "destination": dest,
                "destinationNearbyAirports": True,
                "maxStops": None,
                "origin": origin,
                "originNearbyAirports": True
            }
        ],
        "tripOptions": {
            "pointOfSale": "US",
            "searchType": "Award",
            "corporateBooking": False,
            "locale": "en_US"
        },
        "loyaltyInfo": None,
        "version": "",
        "queryParams": {
            "sliceIndex": 0,
            "sessionId": "",
            "solutionSet": "",
            "solutionId": ""
        }
    }

    return data


def build_url(origin, dest, date):
    url = f"https://www.aa.com/booking/search?type=OneWay&searchType=Award&from={origin}&to={dest}&pax=1&cabin=&locale=en_US&nearbyAirports=false&depart={date}&carriers=ALL&pos=US&adult=1"
    webbrowser.open(url)


output_path = "output.txt"
routes_path = "routes.txt"
origin = ""
dest = ""
valid_dates = []
first = True

max_retries = 5  
retry_delay = 10  

with open(routes_path,'r') as file: 
        for line in file:
            valid_dates.append([])

while True:
    count = 0
    days_data = []
    
    with open(routes_path, 'r') as file:
        for line in file:
            route = line.split()
            print(route)
            origin = route[0]
            dest = route[1]

            year = 2024
            day_start = 1
            month_date = 2

            for index in range(12):
                _, day_end = calendar.monthrange(year, month_date)
                formatted_month = f"{month_date:02d}"
                start = f"{year}-{formatted_month}-{day_start:02d}"

                json_data = create_json_string(origin, dest, start)
                json.dumps(json_data)

                url = "https://www.aa.com/booking/api/search/calendar"

                retries = 0
                while retries < max_retries:
                    try:
                        response = requests.post(url, json=json_data)

                        if response.status_code == 200:
                            print("Request successful.")
                            response_JSON = response.json()
                            # Process response_JSON as needed
                            break  # Exit the retry loop on success
                        else:
                            print(f"Request failed with status code: {response.status_code}")
                            break  # Exit the retry loop if a non-retryable error

                    except requests.exceptions.ConnectionError:
                        print("Failed to connect to the server. Retrying...")
                    except Exception as e:
                        print(f"An error occurred: {e}. Retrying...")

                    time.sleep(retry_delay)
                    retries += 1

                if retries >= max_retries:
                    print("Maximum retries reached. Moving to the next task.")

                calendar_months = response_JSON.get('calendarMonths', [])

                for month in calendar_months:
                    for weeks in month.get("weeks", []):
                        for day in weeks.get("days", []):
                            if day.get("solution") != None:
                                solution = day.get("solution")
                                if solution and day.get("date") not in valid_dates[count]:
                                    valid_dates[count].append(day.get("date"))
                                    if not first:
                                        build_url(origin, dest, day.get("date"))
                month_date += 1
                if month_date > 12:
                    year += 1
                    month_date = 1
            count += 1
        first = False
        time.sleep(60 * 15)

