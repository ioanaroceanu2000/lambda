import json
import dateutil.parser
import datetime
import time
import os
import math
import random
import logging
from response_builders import elicit_slot, confirm_intent, close, delegate, build_response_card, build_validation_result

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


""" --- Helpers to build responses which match the structure of the necessary dialog actions --- """



""" --- VAlidatioan and action functions --- """

def validate_book_appointment(meeting_date, meeting_time, meeting_duration, participant, meeting_title):
    #TODO
    """
    if meeting_date <= yesterday:
        ask for another date
    if meeting_date >= 3 monthd ahead:
        ask for another date
    if meeting_date == today and meeting_time < current time:
        ask for another date

    check if time slot is free in calendar, return free timeslots (response card) that day

    check participants is an employee

    if meeting_title is not String:
        ask for meeting title

    """
    return build_validation_result(True, None, None)


def book_meeting(intent_request):
    """
    Performs dialog management and fulfillment for scheduling a meeting.
    """
    meeting_date = intent_request['currentIntent']['slots']['meetingDate']
    meeting_time = intent_request['currentIntent']['slots']['meetingTime']
    meeting_duration = intent_request['currentIntent']['slots']['meetingDuration']
    participant = intent_request['currentIntent']['slots']['participant']
    meeting_title = intent_request['currentIntent']['slots']['meetingTitle']
    source = intent_request['invocationSource']
    output_session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}

    if source == 'DialogCodeHook':
        # Perform basic validation on the supplied input slots.
        slots = intent_request['currentIntent']['slots']
        validation_result = validate_book_appointment(meeting_date, meeting_time, meeting_duration, participant, meeting_title)
        if not validation_result['isValid']:
            slots[validation_result['violatedSlot']] = None
            return elicit_slot(
                output_session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            )

        if not meeting_date:
            return elicit_slot(
                output_session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'meetingDate',
                {'contentType': 'PlainText', 'content': 'What date?'}
            )

        if meeting_date and not meeting_time:
            return elicit_slot(
                output_session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'meetingTime',
                {'contentType': 'PlainText', 'content': 'What time?'}
            )

        if meeting_date and meeting_time and not meeting_duration:
            return elicit_slot(
                output_session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'meetingDuration',
                {'contentType': 'PlainText', 'content': 'For how long?'}
            )
        if meeting_date and meeting_time and meeting_duration and not participant:
            return elicit_slot(
                output_session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'participant',
                {'contentType': 'PlainText', 'content': 'Who with?'}
            )
        if meeting_date and meeting_time and participant and meeting_duration and not meeting_title:
            return elicit_slot(
                output_session_attributes,
                intent_request['currentIntent']['name'],
                intent_request['currentIntent']['slots'],
                'meetingTitle',
                {'contentType': 'PlainText', 'content': 'Meeting Title?'}
            )

        return delegate(output_session_attributes, slots)


    logger.debug('Correct'
                 'We will book this for you')

    return close(
        output_session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Okay, I have scheduled your meeting.  We will see you at {} on {}'.format(meeting_time, meeting_date)
        }
    )


""" --- Intents --- """


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'BookMeeting':
        return book_meeting(intent_request)
    raise Exception('Intent with name ' + intent_name + ' not supported')


""" --- Main handler --- """


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
