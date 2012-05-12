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
        data = _select_juice('elin')

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
        data = _select_juice('elin')
        id = data['id']
        rating = -1

        _rate(id, 'elin', rating)
        data = _get_ratings(id)

        assert 'ratings' in data
        assert data['id'] == id
        assert len(data['ratings']) == 1
        assert data['ratings']['elin'] == rating

    def test_ratings_can_be_overwritten(self):
        data = _select_juice('elin')
        id = data['id']

        _rate(id, 'elin', -1)
        data = _get_ratings(id)
        assert data['ratings'] == {'elin': -1}

        _rate(id, 'elin', 1)
        data = _get_ratings(id)
        assert data['ratings'] == {'elin': 1}

    def test_each_juicer_can_rate_a_recipe_once(self):
        data = _select_juice('elin')
        id = data['id']

        _rate(id, 'elin', -1)
        _rate(id, 'eskil', 1)
        data = _get_ratings(id)
        assert data['ratings'] == {'elin': -1, 'eskil': 1}

    def test_only_juicers_can_rate(self):
        data = _select_juice('elin')
        id = data['id']
        _rate(id, None, -1, status=400)

    def test_has_max_10_active_juices(self):
        existing = [_select_juice('elin')['id'] for i in range(10)]
        assert _select_juice('eskil')['id'] in existing

    def test_max_active_juices_does_not_restrict_for_single_user(self):
        existing = [_select_juice('elin')['id'] for i in range(11)]
        assert len(existing) == 11


def _select_juice(juicer):
    res = _get('/', params={'juicer': juicer})
    return json.loads(res.body)

def _rate(recipe_id, juicer, rating, status='*'):
    data = json.dumps({'juicer': juicer, 'rating': rating})
    _post('/%s/ratings' % recipe_id, data, status=status)

def _get_ratings(recipe_id):
    ret = _get('/%s/ratings' % recipe_id)
    return json.loads(ret.body)

def _get_recipe(recipe_id):
    res = _get('/%s' % recipe_id)
    return json.loads(res.body)

def _get(path, **kwargs):
    middleware = []
    testApp = TestApp(serve.app.wsgifunc(*middleware))
    r = testApp.get(path, headers={'Content-Type': 'text/plain'}, **kwargs)
    return r

def _post(path, data, status='*'):
    middleware = []
    testApp = TestApp(serve.app.wsgifunc(*middleware))
    r = testApp.post(path, data, status=status)
    return r

