import urllib2
import json
import subprocess
import time
import nose.tools as nt
import serve
from paste.fixture import TestApp, AppError

class TestServe(object):

    def setup(self):
        serve.lookup = {}

    def test_create_and_get(self):
        # generate a new recipe
        data = _create_new()

        assert 'id' in data
        assert 'ingredients' in data
        assert isinstance(data['ingredients'], dict)
        assert data['ingredients']

        # fetch that recipe
        recipe_id = data['id']
        data2 = _get_recipe(recipe_id)
        assert data == data2

        # fetch a non-existing id
        with nt.assert_raises(AppError):
            _get_recipe('not_an_id')

    def test_rate_negative(self):
        data = _create_new()
        id = data['id']
        rating = -1

        _rate(id, 'elin', rating)
        data = _get_ratings(id)

        assert 'ratings' in data
        assert data['id'] == id
        assert len(data['ratings']) == 1
        assert data['ratings']['elin'] == rating

    def test_ratings_can_be_overwritten(self):
        data = _create_new()
        id = data['id']

        _rate(id, 'elin', -1)
        data = _get_ratings(id)
        assert data['ratings'] == {'elin': -1}

        _rate(id, 'elin', 1)
        data = _get_ratings(id)
        assert data['ratings'] == {'elin': 1}

    def test_each_user_can_rate_a_recipe_once(self):
        data = _create_new()
        id = data['id']

        _rate(id, 'elin', -1)
        _rate(id, 'eskil', 1)
        data = _get_ratings(id)
        assert data['ratings'] == {'elin': -1, 'eskil': 1}

    def test_only_users_can_rate(self):
        data = _create_new()
        id = data['id']
        _rate(id, None, -1, status=400)

def _create_new():
    res = _get('/')
    return json.loads(res.body)

def _rate(recipe_id, user, rating, status='*'):
    data = json.dumps({'user': user, 'rating': rating})
    _post('/%s/ratings' % recipe_id, data, status=status)

def _get_ratings(recipe_id):
    ret = _get('/%s/ratings' % recipe_id)
    return json.loads(ret.body)

def _get_recipe(recipe_id):
    res = _get('/%s' % recipe_id)
    return json.loads(res.body)

def _get(path):
    middleware = []
    testApp = TestApp(serve.app.wsgifunc(*middleware))
    r = testApp.get(path, headers={'Content-Type': 'text/plain'})
    return r

def _post(path, data, status='*'):
    middleware = []
    testApp = TestApp(serve.app.wsgifunc(*middleware))
    r = testApp.post(path, data, status=status)
    return r

