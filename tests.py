import urllib2
import json
import subprocess
import time
import nose.tools as nt

class TestServe(object):

    def setup(self):
        self.p = subprocess.Popen(['python', 'serve.py'])
        time.sleep(1)

    def teardown(self):
        self.p.terminate()

    def test_create_and_get(self):
        # generate a new recipe
        data = _create_new()

        assert 'id' in data
        assert 'ingredients' in data
        assert isinstance(data['ingredients'], dict)
        assert data['ingredients']

        # fetch that recipe
        recipe_id = data['id']
        res2 = urllib2.urlopen('http://localhost:8080/' + recipe_id).read()
        data2 = json.loads(res2)
        assert data == data2

        # fetch a non-existing id
        with nt.assert_raises(urllib2.HTTPError):
            res3 = urllib2.urlopen('http://localhost:8080/not_an_id').read()

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
        with nt.assert_raises(urllib2.HTTPError) as e:
            _rate(id, None, -1)
        assert e.exception.getcode() == 400

def _create_new():
    res = urllib2.urlopen('http://localhost:8080').read()
    return json.loads(res)

def _rate(recipe_id, user, rating):
    data = json.dumps({'user': user, 'rating': rating})
    urllib2.urlopen('http://localhost:8080/%s/ratings' % recipe_id, data)

def _get_ratings(recipe_id):
    ret = urllib2.urlopen('http://localhost:8080/%s/ratings' % recipe_id)
    return json.load(ret)

