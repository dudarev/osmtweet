# http://www.openstreetmap.org/browse/changeset/15210559
import datetime
import time
from xml.etree import cElementTree as etree

from get_config import get_config
from models import Changeset
from trim_to_tweet import trim_to_tweet


file_name = "data.osm"
data = open(file_name, 'r')


TIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

config = get_config()
# o,a for lat,lon
# 1,2 for min,max
o1, a1, o2, a2 = map(float, config['bbox'].split(','))
delta_o = o2 - o1
delta_a = a2 - a1

for event, elem in etree.iterparse(data):
    if elem.tag == 'changeset':
        id = elem.attrib.get('id', None)
        if id:
            id = int(id)
            print "<br/>id: %d" % id
        value_str = elem.attrib['created_at']
        created_at = datetime.datetime.fromtimestamp(time.mktime(
            time.strptime(value_str, TIME_FORMAT)))
        print "<br/>created_at: %s" % created_at
        user = elem.attrib.get('user', None)
        if user:
            print "<br/>user: %s" % user
        min_lon = float(elem.attrib.get('min_lon', -180))
        min_lat = float(elem.attrib.get('min_lat', -90))
        max_lon = float(elem.attrib.get('max_lon', 180))
        max_lat = float(elem.attrib.get('max_lat', 90))
        # TODO: move 3 to a global variable
        # 3 is an arbitrary number,
        # we just ignore changesets that 3 times larger than bbox in config
        print "<br/>delta_lon: %f" % (max_lon - min_lon)
        print "<br/>delta_lat: %f" % (max_lat - min_lat)
        if ((max_lon - min_lon) > 3 * delta_o) or ((max_lat - min_lat) > 3 * delta_a):
            print "<br/>changeset BBOX is too large<br/>"
            # go to next element
            continue
        comment = None
        created_by = None
        tags = elem.findall('tag')
        for t in tags:
            if t.attrib['k'] == 'comment':
                comment = t.attrib['v']
            if t.attrib['k'] == 'created_by':
                created_by = t.attrib['v']
        if comment:
            print "<br/>comment: %s" % comment
        if created_by:
            print "<br/>created_by: %s" % created_by
        print "<br/>"
        c = Changeset(
            key_name=str(id),
            id=id,
            created_at=created_at,
            user=user,
            comment=comment,
            created_by=created_by)
        print c
        print trim_to_tweet(c.comment)
