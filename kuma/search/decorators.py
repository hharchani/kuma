import logging
from django.db.models.signals import pre_delete
from elasticsearch.exceptions import ConnectionError

from kuma.wiki.signals import render_done

from .signals import render_done_handler, pre_delete_handler


log = logging.getLogger('kuma.search.decorators')


_mapping_types = {}


def register_mapping_type(mapping_type):
    """Registers a mapping type.

    This gives us a way to get all the registered mapping types for
    indexing.

    """
    _mapping_types[mapping_type.get_mapping_type_name()] = mapping_type
    # Enable this to be used as a decorator
    return mapping_type


def requires_good_connection(fun):
    """Decorator that logs an error on connection issues

    9 out of 10 doctors say that connection errors are usually because
    ES_URLS is set wrong. This catches those errors and helps you out
    with fixing it.

    """
    def _requires_good_connection(*args, **kwargs):
        try:
            return fun(*args, **kwargs)
        except ConnectionError:
            log.error('Either your ElasticSearch process is not quite '
                      'ready to rumble, is not running at all, or ES_URLS'
                      'is set wrong in your settings_local.py file.')
    return _requires_good_connection


def register_live_index(model_cls):
    """Register a model and index for auto indexing."""
    uid = str(model_cls) + 'live_indexing'
    render_done.connect(render_done_handler, model_cls, dispatch_uid=uid)
    pre_delete.connect(pre_delete_handler, model_cls, dispatch_uid=uid)
    # Enable this to be used as decorator.
    return model_cls
