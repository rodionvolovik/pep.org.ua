# coding: utf-8
from __future__ import unicode_literals

import logging
from django.contrib import messages


class AbstractLogger(object):
    def debug(self, message):
        raise NotImplementedError()

    def info(self, message):
        raise NotImplementedError()

    def success(self, message):
        raise NotImplementedError()

    def warning(self, message):
        raise NotImplementedError()

    def error(self, message):
        raise NotImplementedError()


class NoOpLogger(AbstractLogger):
    def debug(self, message):
        pass

    def info(self, message):
        pass

    def success(self, message):
        pass

    def warning(self, message):
        pass

    def error(self, message):
        pass


class PythonLogger(AbstractLogger):
    def __init__(self, logger_name):
        self.logger = logging.getLogger(logger_name)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def success(self, message):
        self.logger.success(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)


class MessagesLogger(AbstractLogger):
    def __init__(self, request):
        self.request = request

    def debug(self, message):
        messages.debug(self.request, message)

    def info(self, message):
        messages.info(self.request, message)

    def success(self, message):
        messages.success(self.request, message)

    def warning(self, message):
        messages.warning(self.request, message)

    def error(self, message):
        messages.error(self.request, message)
