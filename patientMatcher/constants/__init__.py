
# useful HTTP response status codes with messages

STATUS_CODES = {
    'ok': {
        'status_code' : 200
    },
    'bad_request' : {
        'status_code' : 400,
        'message' : 'Invalid request JSON'
    },
    'unprocessable_entity' : {
        'status_code' : 422,
        'message' : 'Request does not conform to API specifications'
    },
    'unauthorized' : {
        'status_code' : 401,
        'message' : 'Not authorized'
    }
}
