
# useful HTTP response status codes with messages

STATUS_CODES = {
    200 : {
        'status_code' : 200
    },
    400 : {
        'message' : 'Invalid request JSON'
    },
    422 : {
        'message' : 'Request does not conform to API specifications'
    },
    401 : {
        'message' : 'Not authorized'
    },
    500 : {
        'message' : 'An error occurred while updating the database'
    },
}
