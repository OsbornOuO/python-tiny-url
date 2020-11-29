# -*- coding: utf-8 -*-

from app.extensions import db
from sqlalchemy.sql import func
import json
import re
from app.errors import ToManyShortURL, NoSupportShortURLCharacter, NoSupportURL, InvalidInput, SameDomin

alphabet = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
length = len(alphabet)
regex = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    # domain...
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


class ShortURL(db.Model):
    __tablename__ = 'short_urls'

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(2048), nullable=False)
    created_at = db.Column(db.DateTime(), nullable=False,
                           server_default=func.now())
    short = ""

    def __init__(self):
        self.url = ""

    def init_by_create(self, d: dict):
        if 'url' in d:
            self.url = d['url']
        else:
            raise InvalidInput

    def verify(self):
        if re.match(regex, self.url) is None:
            raise NoSupportURL
        if "https://py-shorten.herokuapp.com/" in self.url:
            raise SameDomin
    
        return None

    def init_by_decode(self, s: str):
        self.short = s
        self.id = self.encode()

    def toJSON(self):
        return json.dumps({
            "id": self.id,
            "url": self.url,
            "short": self.short,
        })

    def decode(self) -> str:
        if self.id == 0:
            return alphabet[0]

        s = ""
        n = self.id
        while n > 0:
            s = alphabet[n % length] + s
            n = n // length
        return s

    def encode(self) -> int:
        n = 0

        for i in self.short:
            index = 0
            try:
                index = alphabet.index(i)
            except:
                raise NoSupportShortURLCharacter

            n = length*n+index
        return n

    def create(self):
        num = db.session.query(ShortURL).count()
        if num > 916132832:
            raise ToManyShortURL

        db.session.add(self)
        db.session.commit()

        self.short = self.decode()

    def get_by_id(self):
        return db.session.query(ShortURL).filter(
            ShortURL.id == self.id).first()
