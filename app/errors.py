# -*- coding: utf-8 -*-

# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""
    pass


class ToManyShortURL(Error):
    """Raised when the input value is too small"""
    pass


class NoSupportShortURLCharacter(Error):
    """Raised when the input value is too small"""
    pass


class NoSupportURL(Error):
    """Raised when the input value is too small"""
    pass


class SameDomin(Error):
    """Raised when the input value is too small"""
    pass


class InvalidInput(Error):
    pass
