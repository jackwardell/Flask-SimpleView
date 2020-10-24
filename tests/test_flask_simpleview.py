import flask
import pytest
import flask_simpleview

RULE = '/simple-view'
ENDPOINT = 'simple_view'
GET_RETURNS = "<html><head></head><body>hello</body></html>"
POST_RETURNS = {"goodbye": "world"}


class SimpleView(flask_simpleview.SimpleView):
    rule = RULE
    endpoint = ENDPOINT

    def get(self):
        return GET_RETURNS

    def post(self):
        return POST_RETURNS


class AnotherSimpleView(flask_simpleview.SimpleView):
    def get(self):
        return GET_RETURNS

    @flask_simpleview.extends_rule('/id/')
    def post(self):
        return POST_RETURNS


def test_flask():
    app = flask_simpleview.Flask("test")
    app.add_view(SimpleView)
    app.add_view(AnotherSimpleView)

    with app.test_client() as client:
        assert client.get(RULE).data.decode() == GET_RETURNS
        assert client.post(RULE).json == POST_RETURNS

        assert client.get('/another-simple-view').data.decode() == GET_RETURNS
        assert client.post('/another-simple-view/id/').json == POST_RETURNS


def test_blueprint():
    blueprint = flask_simpleview.Blueprint("test", __name__)
    blueprint.add_view(SimpleView)
    blueprint.add_view(AnotherSimpleView)

    app = flask.Flask("test")
    app.register_blueprint(blueprint)

    with app.test_client() as client:
        assert client.get(RULE).data.decode() == GET_RETURNS
        assert client.post(RULE).json == POST_RETURNS

        assert client.get('/another-simple-view').data.decode() == GET_RETURNS
        assert client.post('/another-simple-view').json == POST_RETURNS


if __name__ == "__main__":
    pytest.main()
