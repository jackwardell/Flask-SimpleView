import re

import flask
import flask.views
from functools import wraps


def camel_case_to_snake_case(word):
    """very simple mechanism for turning CamelCase words into snake_case"""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", word).lower()


def camel_case_to_slug_case(word):
    """very simple mechanism for turning CamelCase words into slug-case"""
    return re.sub(r"(?<!^)(?=[A-Z])", "-", word).lower()


class NoTemplate(Exception):
    """exception for when no template is passed either as a param or in the class"""

    pass


class SkeletonMixin:
    """Mixin for the flask Skeleton (shared methods between Flask and Blueprint)"""

    def add_url_rule(self, *args, **kwargs):
        raise NotImplementedError()

    def add_view(self, view):
        # make all the elements for the adding of a url_rule
        # make rule
        rule = view.make_rule()
        # make endpoint
        endpoint = view.make_endpoint()
        # make view_func
        view_func = view.as_view(endpoint)

        # make a list of all the view functions to add
        view_funcs = []

        # iterate through all the registered methods
        for method in view.methods:
            # get the function itself
            func = getattr(view, method.lower())

            # if the function has been decorated with a __rule_extension__
            # we can grab it and make the extended rule
            if hasattr(func, "__rule_extension__"):
                # make the extended rule
                extended_rule = rule + func.__rule_extension__
                # save the new rule and view func as params for add_url_rule
                params = {"rule": extended_rule, "view_func": view_func}

            else:
                # else we do it without the rule extension
                params = {"rule": rule, "view_func": view_func}

            # append the method to the list of view funcs
            view_funcs.append(params)

        # finally, iterate through the view_funcs and add the url_rule
        for params in view_funcs:
            self.add_url_rule(**params)

    def add_api(self, api):
        return self.add_view(api)


class Flask(flask.Flask, SkeletonMixin):
    """The flask.Flask application"""

    pass


class Blueprint(flask.Blueprint, SkeletonMixin):
    """The flask.Blueprint blueprint"""

    pass


class ViewConstructor:
    """mechanism for construction of endpoint and rule"""

    methods = []

    @classmethod
    def get_name(cls):
        return getattr(cls, "name", cls.__name__)

    @classmethod
    def make_endpoint(cls):
        return getattr(cls, "endpoint", camel_case_to_snake_case(cls.get_name()))

    @classmethod
    def make_rule(cls):
        return getattr(cls, "rule", "/" + camel_case_to_slug_case(cls.get_name()))

    @classmethod
    def iter_methods(cls):
        for method in cls.methods:
            func = getattr(cls, method.lower())


def extends_rule(rule):
    def extend_rule(func):
        # assert False
        # cls, method = func.__qualname__.split('.')
        func.__rule_extension__ = rule
        return func

        # @wraps(func)
        # def decorator(*args, **kwargs):
        #     return func(*args, **kwargs)
        #
        # return decorator

    return extend_rule


class SimpleView(flask.views.MethodView, ViewConstructor):
    def render_template(self, *optional_template_name_or_list, **context):
        if not hasattr(self, "template") and not optional_template_name_or_list:
            raise NoTemplate("No template passed or found on the view")

        template_name_or_list = (
            optional_template_name_or_list[0]
            if optional_template_name_or_list
            else self.template
        )
        return flask.render_template(template_name_or_list, **context)

    def __getattr__(self, attr):
        return getattr(flask, attr)

    def __repr__(self):
        rv = '<{}(rule="{}", endpoint="{}", methods={})>'.format(
            self.__class__.__name__, self.rule, self.endpoint, self.methods
        )
        return rv


API = View = SimpleView
