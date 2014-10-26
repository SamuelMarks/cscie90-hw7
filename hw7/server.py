from json import dumps, loads
from uuid import uuid4

from collections import OrderedDict
from klein import Klein


class CustomerStore(object):
    app = Klein()

    def __init__(self):
        self.customers = OrderedDict(dict())  # Trivial to swap out for some simple k/v store or SimpleDB

    @app.route('/', methods=['GET', 'POST'])
    def create_customer(self, request):
        request.setHeader('Content-Type', 'application/json')

        if request.method == 'POST':
            body = loads(request.content.read())
            if body.keys() != ['first_name', 'last_name', 'country']:
                request.setResponseCode(400)
                return dumps({'error': 'ValidationError',
                              'error_message': 'You must include `first_name` and `last_name` keys'})
            pk = '{0} {1}'.format(body['first_name'], body['last_name'])
            if pk in self.customers:
                request.setResponseCode(400)
                return dumps({'error': 'UniqueKeyError',
                              'error_message': 'First name + last_name combination must be unique'})
            body['id'] = uuid4().get_hex()
            self.customers[pk] = body
            return dumps({'created': body})
        else:
            if not request.args or 'limit' in request.args:
                if not self.customers:
                    request.setResponseCode(404)
                    return dumps({'error': 'NotFound',
                                  'error_message': 'No customers in collection'})
                return dumps(self.customers[:request.args.get('limit', 2)])  # Show only two records by default
            elif request.args.keys() != ['first_name', 'last_name']:
                request.setResponseCode(400)
                return dumps({'error': 'ValidationError',
                              'error_message': 'You must include `first_name` and `last_name` keys'})
            pk = '{0} {1}'.format(request.args['first_name'][0], request.args['last_name'][0])
            if pk not in self.customers:
                request.setResponseCode(404)
                return dumps({'error': 'NotFound',
                              'error_message': 'First name + last_name combination not found in collection'})

            return dumps(self.customers[pk])

    @app.route('/<string:name>', methods=['PUT'])
    def save_customer(self, request, name):
        request.setHeader('Content-Type', 'application/json')
        body = loads(request.content.read())
        # You can also edit the pk here, which might not be a good idea:
        if {'first_name', 'last_name', 'id'}.issubset(set(body.keys())):  # Allow you to edit `id` here
            request.setResponseCode(400)
            return dumps({'error': 'ValidationError',
                          'error_message': 'You must include `first_name`, `last_name`, `country` and/or `id` key(s)'})
        if name not in self.customers:
            request.setResponseCode(404)
            return dumps({'error': 'NotFound',
                          'error_message': '"{0}" not found in customers collection'.format(name)})

        self.customers[name].update(body)
        return dumps(self.customers[name])

    @app.route('/<string:name>', methods=['GET'])
    def retrieve_customer(self, request, name):
        request.setHeader('Content-Type', 'application/json')
        if name not in self.customers:
            request.setResponseCode(404)
            return dumps({'error': 'NotFound',
                          'error_message': '"{0}" not found in customers collection'.format(name)})
        return dumps(self.customers[name])

    @app.route('/<string:name>', methods=['DELETE'])
    def delete_customer(self, request, name):
        request.setHeader('Content-Type', 'application/json')
        if name not in self.customers:
            request.setResponseCode(404)
            return dumps({'error': 'NotFound',
                          'error_message': '"{0}" not found in customers collection'.format(name)})
        return dumps({'deleted': self.customers.pop(name)})


if __name__ == '__main__':
    store = CustomerStore()
    store.app.run('0.0.0.0', 8080)
