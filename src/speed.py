from db import db

class Speed(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return self.name

class Variant(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name

    def __str__(self):
        return self.name

class SpeedAndVariant(object):
    def __init__(speed_id, variant_id):
        self.speed = speeds[speed_id]
        self.variant = variants[speed_id]

speeds = {}
variants = {}
def init():
    for row in db.get_speeds():
        speeds[row['speed_id']] = Speed(row['speed_id'], row['speed_name'])
    for row in db.get_variants():
        variants[row['variant_id']] = Variant(row['variant_id'],
            row['variant_name'])

# vim: expandtab tabstop=4 softtabstop=4 shiftwidth=4 smarttab autoindent
