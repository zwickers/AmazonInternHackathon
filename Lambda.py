"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import requests
import json
import apikey


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Alexa Skills Kit sample. " \
                    "Please tell me your favorite color by saying, " \
                    "my favorite color is red"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me your favorite color by saying, " \
                    "my favorite color is red."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_movie_list_attribute(movie_list):
    return {'movieList': movie_list, 'index': 0}


def next_movie_item(session_attributes):
    if 'index' in session_attributes:
        index = session_attributes['index']
        session_attributes['index'] = index + 1
    return session_attributes


def previous_movie_item(session_attributes):
    if 'index' in session_attributes:
        index = session_attributes['index']
        if index > 0:
            session_attributes['index'] = index - 1
    return session_attributes


def get_previous_movie(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "movieList" in session.get('attributes', {}):
        if session['attributes']['index'][0] > 0:
            movie = session['attributes']['movieList'][session['attributes']['index'][0]][0]
            session_attributes = previous_movie_item(session['attributes'])
            speech_output = "The last movie was" + movie
            should_end_session = False
        else:
            speech_output = "There are no previous movies"
            should_end_session = True
    else:
        speech_output = "You have not made a query. Would you like to make one?"
        should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


def get_next_movie(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "movieList" in session.get('attributes', {}):
        if session['attributes']['index'][0] < (len(session['attributes']['movielist']) - 1):
            movie = session['attributes']['movieList'][session['attributes']['index'][0]][0]
            session_attributes = next_movie_item(session['attributes'])
            speech_output = "Another movie is" + movie
            should_end_session = False
        else:
            speech_output = "There are no more movies starring this individual"
            should_end_session = True
    else:
        speech_output = "You have not made a query. Would you like to make one?"
        should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


def get_movie_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    actor = intent['slots']['actor']['value']
    r = requests.get("http://api.tmdb.org/3/search/person?api_key={}&query={}".format(apikey.api_key, actor))

    data = json.loads(r.content)

    results = data['results'][0]

    movies_list = []

    for description in results['known_for']:
        title = description['title']
        rating = description['vote_average']
        tuple = (title, rating)
        movies_list.append(tuple)

    movies_list = sorted(movies_list, key=lambda x: x[1])[::-1]
    session_attributes = create_movie_list_attribute(movies_list)

    if len(movies_list) > 0:
        movie = movies_list[0][0]
        speech_output = "The {} stars in {}".format(actor, movie)
        session_attributes = next_movie_item(session_attributes)
        should_end_session = False
    else:
        speech_output = "No movies were found starring" + actor
        should_end_session = True

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "ActorQueryIntent":
        return get_movie_session(intent, session)
    elif intent_name == "NextIntent":
        return get_next_movie(intent, session)
    elif intent_name == "PreviousIntent":
        return get_previous_movie(intent, session)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])