"""
Flask-based REST API for parsing address string into its component parts
"""
from datetime import datetime
from flask import Flask, jsonify, request
import platform
import pytz

class USAddressParser(object):
    """
    Parses address string using usaddress library
    """
    import usaddress

    @staticmethod
    def parse_with_parse(addr_str):
        """
        Translates an address string using usaddress's `parse()` function
    
        See: http://usaddress.readthedocs.org/en/latest/#usage
        """
        # usaddress parses free-text address into an array of tuples...why, I don't know.
        parsed = usaddress.parse(addr_str)
    
        # Converted tuple array to dict
        addr_parts = {addr_part[1]: addr_part[0] for addr_part in parsed}
    
        return addr_parts
    
    @staticmethod
    def parse_with_tag(addr_str):
        """
        Translates an address string using usaddress's `tag()` function
    
        See: http://usaddress.readthedocs.org/en/latest/#usage
        """
        try:
            # FIXME: Consider using `tag()`'s address type for validation?
            # `tag` returns OrderedDict, ordered by address parts in original address string
            addr_parts = usaddress.tag(addr_str)[0]
        except usaddress.RepeatedLabelError:
            # FIXME: Add richer logging here with contents of `rle`
            raise InvalidApiUsage("Could not parse address '{}' with 'tag' method".format(addr_str))
    
        return addr_parts

    __parse_method_dispatch = {'parse': parse_with_parse, 'tag': parse_with_tag}


    def __init__(self, parse_method='parse'):
        try:
            self.parse_method = __parse_method_dispatch[parse_method]
        except KeyError:
            raise ValueError("Parsing method '{}' not supported.".format(method))


    def parse(self, addr_str):
        return self.parser_method(addr_string)


class InvalidApiUsage(Exception):
    """
    Exception for invalid usage of address parsing API

    This is a simplifiled version of Flask's Implementing API Exceptions:
    See: http://flask.pocoo.org/docs/0.10/patterns/apierrors/
    """
    status_code = 400

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


UP_SINCE = datetime.now(pytz.utc).isoformat()
HOSTNAME = platform.node()

app = Flask(__name__)


@app.route('/', methods=['GET'])
def status():
    """
    Provides the current status of the address parsing service
    """

    status = {
        "service": "grasshopper-parser",
        "status": "OK",
        "time": datetime.now(pytz.utc).isoformat(),
        "host": HOSTNAME,
        "upSince": UP_SINCE,
    }

    return jsonify(status)


@app.route('/parse', methods=['GET'])
def parse():
    """
    Parses an address string into its component parts
    """
    req_data = request.args

    try:
        addr_str = req_data['address']
    except KeyError:
        raise InvalidApiUsage("'address' query param is required.")

    method = req_data.get('method', 'parse')

    response = {
        'input': addr_str,
        'parts': addr_parts
    }

    return jsonify(response)


def gen_error_json(message, code):
    return jsonify({'error': message, 'statusCode': code}), code


@app.errorhandler(InvalidApiUsage)
def usage_error(error):
    return gen_error_json(error.message, error.status_code)


@app.errorhandler(404)
def not_found_error(error):
    return gen_error_json('Resource not found', 404)


@app.errorhandler(Exception)
def default_error(error):
    app.logging.exception('Internal server error', error)
    return gen_error_json('Internal server error', 500)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
