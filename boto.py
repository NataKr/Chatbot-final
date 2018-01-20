"""
This is the template server side for ChatBot
"""
from bottle import route, run, template, static_file, request, response
from datetime import datetime, timedelta
import json
import random
import requests
from weather import Weather
import urllib2
import wikipedia
import names
from bs4 import BeautifulSoup


@route('/', method='GET')
def index():
    return template("chatbot.html")


@route("/chat", method='POST')
def chat():
    user_message = request.POST.get('msg')
    response_swear=handleSwearWords(user_message)
    print response_swear
    if response_swear:
        #return json.loads(response_swear) # if we want to return the json object
        return json.dumps({"animation": "no", "msg": response_swear})
    elif "joke" in user_message.lower():
        return json.loads(getJoke())
    elif "weather" in user_message.lower():
        return json.loads(getWeather(user_message))
    elif "temperature" in user_message.lower():
        return json.loads(getTemperature(user_message))
    elif "name" in user_message.lower():
        return json.loads(handleUserName(user_message))
    elif (all(word in user_message.lower() for word in ["tell", "me", "about"])) or (all(word in user_message.lower() for word in ["tell", "about"])):
        return json.loads(handleAbout(user_message))
    elif user_message.lower()=="nothing":
        return json.loads(handleNothing())
    elif user_message.lower()=="anything" or user_message.lower()=="something" or user_message.lower()=="whatever":
        user_name=getCookie("user_name")
        return json.dumps({
            "animation":"bored",
            "msg":user_name.capitalize()+", be specific or I will just keep repeating your message like a parrot. "+user_message
        })
    elif len(user_message.split())==1:
        user_name = getCookie("user_name")
        return json.dumps({
            "animation": "money",
            "msg": user_name.capitalize() + ", if you want to learn more about word {0}, write [tell about {0}].".format(user_message)
        })
    else:
        func_list=[handleRandomQuestion(user_message), handleCompliment(user_message)]
        chosen_func=random.choice(func_list)
        return json.loads(chosen_func)
        #return json.loads(repeatMessage(user_message))
        #return json.dumps({"animation": "inlove", "msg": user_message})


@route("/test", method='POST')
def chat():
    user_message = request.POST.get('msg')
    #made a cookie to track if the chatbot has been visited already
    date_last_visited = request.get_cookie("last_visited")
    if not date_last_visited:
        response.set_cookie(name="last_visited",
                            value=str(datetime.now().date()),
                            expires=datetime.now() + timedelta(days=30))
        print request.get_cookie("last_visited")

    return json.dumps({"animation": "inlove", "msg": user_message})

@route('/js/<filename:re:.*\.js>', method='GET')
def javascripts(filename):
    return static_file(filename, root='js')


@route('/css/<filename:re:.*\.css>', method='GET')
def stylesheets(filename):
    return static_file(filename, root='css')


@route('/images/<filename:re:.*\.(jpg|png|gif|ico)>', method='GET')
def images(filename):
    return static_file(filename, root='images')


def handleCompliment(user_message):
    user_name=getCookie("user_name")
    try:
        theurl = "https://www.happier.com/blog/nice-things-to-say-100-compliments"
        thepage = urllib2.urlopen(theurl)
        soup = BeautifulSoup(thepage, "html.parser")
        print soup.title
        questions_list = soup.findAll("li")
        #print questions_list
        questions_text_list = []
        for i in range(3,len(questions_list)):
            questions_text_list.append(questions_list[i].text)
        random_question=random.choice(questions_text_list)
        print random_question
        return json.dumps({
            "animation": "giggling",
            "msg":user_name.capitalize()+", " + random_question
        })
    except:
        return repeatMessage(user_message)
    #print requests.get('http://localhost:7000/chat', headers={"Request Headers": "Cookie"})

def handleRandomQuestion(user_message):
    user_name=getCookie("user_name")
    try:
        theurl = "https://www.conversationstarters.com/101.htm"
        thepage = urllib2.urlopen(theurl)
        soup = BeautifulSoup(thepage, "html.parser")
        print soup.title
        questions_list = soup.findAll("li")
        #print questions_list
        questions_text_list = []
        for question in questions_list:
            questions_text_list.append(question.text)
        random_question=random.choice(questions_text_list)
        print random_question
        return json.dumps({
            "animation": "waiting",
            "msg":user_name.capitalize()+", " + random_question
        })
    except:
        return repeatMessage(user_message)

def repeatMessage(user_message):
    #user_name = getCookie("user_name")
    return json.dumps({"animation": "inlove",
                       "msg": user_message})

def handleNothing():
    nothing_array=["Nothing lasts forever.", "Nothing comes from nothing.","Nothing is more sad than the death of an illusion",
                   "Better to fight for something than live for nothing", "Saying nothing... sometimes says the most"]
    return json.dumps({
        "animation": "bored",
        "msg": random.choice(nothing_array)
    })

def getCookie(cookie_name):
    cookie=request.get_cookie(cookie_name)
    if cookie:
        return cookie
    else:
        return ""

def getWordsInMessage(user_message):
    words_in_message=user_message.lower().replace("!", "").replace(",", "").replace(".", "").replace("?", "").replace(":", "").replace(";", "").replace("/", "").replace("\\", "").split()
    return words_in_message

def handleAbout(user_message):
    words_in_message = getWordsInMessage(user_message)
    ind_tell = words_in_message.index("tell")
    user_name=getCookie("user_name")
    topic=""
    print ind_tell
    print user_name

    if len(words_in_message)>2:
        if "about" in words_in_message[ind_tell+1]:
            try:
                topic=words_in_message[ind_tell+2]

            except:
                return json.dumps({
                    "animation": "confused",
                    "msg": "{} I am not sure what you want to know. Try asking again".format(user_name)
                })

        elif "about" in words_in_message[ind_tell+2]:
            try:
                topic=words_in_message[ind_tell+3]
            except:
                return json.dumps({
                    "animation": "confused",
                    "msg": "{} I am confused. Try finishing the sentence".format(user_name)
                })

        try:
            contents=wikipedia.summary(topic, sentences=2)
            return json.dumps({
                "animation": "ok",
                "msg": contents
            })

        except:
            return json.dumps({
                "animation": "confused",
                "msg": "{} I am not sure what you are asking. Try again".format(user_name.capitalize())
            })

    else:
        return json.dumps({
            "animation": "confused",
            "msg": "{} I am not sure what you are asking. Try again".format(user_name.capitalize())
        })


def handleUserName(user_message):
    words_in_message=user_message.lower().replace("!","").replace(",", "").replace(".","").replace("?","").replace(":","").replace(";","").replace("/","").replace("\\","").split()
    ind_name=words_in_message.index("name")
    user_name=""

    if len(words_in_message)>2 and ind_name>0 and words_in_message[ind_name-1]=="my" and words_in_message[ind_name+1]=="is":
        try:
            user_name=words_in_message[ind_name+2]
            response.set_cookie(name="user_name",
                                value=user_name,
                                expires=datetime.now() + timedelta(days=30))
            return json.dumps({
                "animation": "dog",
                "msg": "Nice to meet you, "+user_name.capitalize()+". What would you like to talk about?"
            })

        except IndexError:
            user_name=request.get_cookie("user_name")
            if user_name:
                return json.dumps({
                    "animation": "confused",
                    "msg": "Do you have a problem finishing lines? {}, which name are you talking about?".format(user_name.capitalize())
                })
            else:
                user_name=names.get_first_name()
                response.set_cookie(name="user_name",
                                    value=user_name,
                                    expires=datetime.now() + timedelta(days=30))
                return json.dumps({
                    "animation": "confused",
                    "msg": "Do you have a problem finishing lines? I will call you {0}. He-he-he. So, {0}, what would you like to talk about?".format(user_name)
                })
    else:
        user_name = request.get_cookie("user_name")
        if user_name:
            return json.dumps({
                "animation": "confused",
                "msg": "Do you have a problem finishing lines? {}, which name are you talking about?".format(user_name.capitalize())
            })
        else:
            user_name = names.get_first_name()
            response.set_cookie(name="user_name",
                                value=user_name,
                                expires=datetime.now() + timedelta(days=30))
            return json.dumps({
                "animation": "confused",
                "msg": "Cannot write full sentences? I will call you {0}. He-he-he. So, {0}, what would you like to talk about?".format(user_name.capitalize())
            })

def handleSwearWords(message):
    words_in_message=getWordsInMessage(message)
    file = open("swears.txt", "r")
    read = file.readlines()
    file.close()
    for word in words_in_message:
        for sentence in read:
            line = sentence.split()
            for each in line:
                line2 = each.lower()
                line2 = line2.strip("!@#.,?/")
                if word.lower() == line2:
                    user_name = request.get_cookie("user_name")
                    if user_name:
                        return user_name.capitalize() + ", stop swearing! Talk nice and we can continue the conversation."
                    else:
                        return "Stop swearing! Talk nice and we can continue the conversation"
    return False

    # swear_list=["fuck","bitch","slut","asshole","ass", "motherfucker", "fucking", "fuck", "fucked"]
    # message_list=message.lower().split()
    # if any(x in swear_list for x in message_list):
    #     #return json.dumps({"animation": "no", "msg": "No swearing"})
    #     user_name=request.get_cookie("user_name")
    #     if user_name:
    #         return user_name.capitalize()+", stop swearing! Talk nice and we can continue the conversation."
    #     else:
    #         return "Stop swearing! Talk nice and we can continue the conversation"
    # else:
    #     return False
    #     #return "No swearing"


@route('/jokes', method='GET')
def getJoke():

    joke = requests.get('http://api.icndb.com/jokes/random')
    #print type(joke.json())
    #print joke.json()
    data = joke.json()
    #print data["type"]
    user_name = request.get_cookie("user_name")
    if not user_name:
        user_name=""
    if data["type"] == "success":
        joke_content = data["value"]
        joke_itself=json.dumps(joke_content["joke"])
        return json.dumps({
            "animation": "laughing",
            "msg":user_name.capitalize()+", here is a joke just for you. "+joke_itself
        })
    else:
        return json.dumps({
            "animation":"heartbroken",
            "msg":"Bad luck, ."+user_name.capitalize()+", No jokes for you today."
        })

@route('/weather', method='GET')
def getWeather(user_message):
    words_in_message=user_message.lower().replace("!","").replace(",", "").replace(".","").replace("?","").replace(":","").replace(";","").replace("/","").replace("\\","").split()
    print words_in_message
    weather=Weather()
    print weather
    current_city=locate_user()
    print "current city " + current_city
    city_in_the_message=""
    weather_condition=""
    weather_animation=""

    #getting potential city name from user message
    ind_weather=words_in_message.index("weather")
    if len(words_in_message)>2 and (len(words_in_message)-ind_weather)>2 and words_in_message[ind_weather+1]=="in":
        city_in_the_message=words_in_message[ind_weather+2]
        print "if condition for message size passed "+city_in_the_message

        if weather.lookup_by_location(city_in_the_message)==None:
            return json.dumps({
                "animation": "confused",
                "msg": "This location does not exist. Please specify the city name"
            })
        else:
            weather_condition = weather.lookup_by_location(city_in_the_message).condition().text()
            weather_animation = getAnimation(weather_condition)
            return json.dumps({
                "animation": weather_animation[0],
                "msg": "it looks like that today in "+city_in_the_message.capitalize()+" is " + weather_condition.lower()+". "+weather_animation[1]
            })
    else:
        weather_condition = weather.lookup_by_location(current_city).condition().text()
        weather_animation = getAnimation(weather_condition)
        return json.dumps({
            "animation": weather_animation[0],
            "msg": "it looks like that today in " + current_city.capitalize() + " is " + weather_condition.lower()
        })

    # try:
    #     weather.lookup_by_location(city_in_the_message)
    #     if weather.lookup_by_location(city_in_the_message)==None:
    #         weather_condition=weather.lookup_by_location(current_city).condition().text()
    #         print weather_condition+" if weather"
    #     else:
    #         weather_condition=weather.lookup_by_location(city_in_the_message).condition().text()
    #         print weather_condition+" else weather"
    # except:
    #     weather_condition = weather.lookup_by_location(current_city).condition().text()
    #     print weather_condition + "  weather exception"
    #
    # weather_animation=getAnimation(weather_condition)
    #
    # return json.dumps({
    #         "animation": weather_animation,
    #         "msg":"it is expected that today will be "+weather_condition.lower()
    #     })

@route('/temperature', method='GET')
def getTemperature(user_message):
    words_in_message=user_message.lower().replace("!","").replace(",", "").replace(".","").replace("?","").replace(":","").replace(";","").replace("/","").replace("\\","").split()
    print words_in_message
    weather=Weather()
    current_city=locate_user()
    print "current city " + current_city
    city_in_the_message=""
    weather_condition=""
    weather_animation=""

    #getting potential city name from user message
    ind_temp=words_in_message.index("temperature")
    if len(words_in_message)>2 and (len(words_in_message)-ind_temp)>2 and words_in_message[ind_temp+1]=="in":
        city_in_the_message=words_in_message[ind_temp+2]
        print "if condition for message size passed "+city_in_the_message

        if weather.lookup_by_location(city_in_the_message)==None:
            return json.dumps({
                "animation": "confused",
                "msg": "This location does not exist. Please specify the city name"
            })
        else:
            weather_condition = weather.lookup_by_location(city_in_the_message).condition().temp()
            temperature=convert_to_celcius(weather_condition)
            print int(weather_condition)
            print type(weather_condition)
            weather_animation = getAnimation(weather_condition)
            print weather_animation
            return json.dumps({
                "animation": weather_animation[0],
                "msg": "it looks like that today in "+city_in_the_message.capitalize()+" is " + str(temperature)+" degrees Celcius. "+weather_animation[1]
            })
    else:
        weather_condition = weather.lookup_by_location(current_city).condition().temp()
        temperature=convert_to_celcius(weather_condition)
        print temperature
        weather_animation = getAnimation(weather_condition)
        print weather_animation
        return json.dumps({
            "animation": weather_animation[0],
            "msg": "it looks like that today in "+current_city.capitalize()+" is " + str(temperature)+" degrees Celcius. "
        })


def getAnimation(weather_condition):
    weather_condition=weather_condition.lower()
    user_name = request.get_cookie("user_name")
    if not user_name:
        user_name=""
    try:
        weather_condition=int(weather_condition)
        if weather_condition<5:
            return ("afraid",getHorribleWeatherComment())
        elif weather_condition>=5 and weather_condition<32:
            return ("heartbroken", getBadWeatherComment())
        else:
            return ("takeoff", getGoodWeatherComment())
    except ValueError:
        if "tornado" in weather_condition or "thunder" in weather_condition or "hurricane" in weather_condition or "storm" in weather_condition or "freezing" in weather_condition:
            return ("afraid", getHorribleWeatherComment())
        elif "rain" in weather_condition or "showers" in weather_condition or "snow" in weather_condition or "windy" in weather_condition or "cloudy" in weather_condition or "cold" in weather_condition:
            return ("crying", getBadWeatherComment())
        elif "hot" in weather_condition or "sunny" in weather_condition or "clear" in weather_condition:
            return ("dancing", getGoodWeatherComment())
        else:
            return ("ok", "A regular day. {}, if you want to find more about the city write 'tell about [city name]'".format(user_name.capitalize()))

def getBadWeatherComment():
    #ultimately, i can try to scrape them
    user_name = request.get_cookie("user_name")
    if not user_name:
        user_name = ""
    comments=["I would not go there if I were you. ", "Better stay at home. ", "There are nicer places in the world right now. "]
    chosen_comment=random.choice(comments)
    return chosen_comment+"{}, if you want to find more about the city write 'tell about [city name]'".format(user_name.capitalize())

def getHorribleWeatherComment():
    user_name = request.get_cookie("user_name")
    if not user_name:
        user_name = ""
    comments = ["Don't go there unless you are suicidal. ", "Better stay at home. ", "There are nicer places in the world right now. "]
    chosen_comment = random.choice(comments)
    return chosen_comment + "{}, if you want to find more about the city write 'tell about [city name]'".format(user_name.capitalize())

def getGoodWeatherComment():
    user_name = request.get_cookie("user_name")
    if not user_name:
        user_name = ""
    comments = ["Nice day! ", "Good day! Wish I was there. ","Good place for a trip. "]
    chosen_comment = random.choice(comments)
    return chosen_comment + "{}, if you want to find more about the city write 'tell about [city name]'".format(user_name.capitalize())

def convert_to_celcius(temp):
    return (int(temp)-32)*5/9

def locate_user():
    location_city=""
    try:
        f = urllib2.urlopen('http://freegeoip.net/json/')
        json_string = f.read()
        f.close()
        location = json.loads(json_string)
        #print(location)
        location_city = location['city']
        #location_state = location['region_name']
        #location_country = location['country_name']
        #print location_city
    except ValueError:
        location_city="tel-aviv"
        #print location_city
    if not location_city:
        location_city="tel-aviv"
    return location_city

def main():
    run(host='localhost', port=7000)

if __name__ == '__main__':
    main()
