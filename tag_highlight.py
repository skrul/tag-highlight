import collections
import cgi
import flask
from html5lib import tokenizer
from html5lib import constants
import requests

app = flask.Blueprint('tag-highlight', __name__, template_folder='templates',
                      static_folder='static')

class TagLoc(object):
    def __init__(self, name, type, offset, length):
        self.name = name
        self.type = type
        self.offset = offset
        self.length = length

    def __repr__(self):
        return '<%s> %d @%d,%d' % (self.name, self.type, self.offset, self.length)


def parse_tag_locations(html):
    row_start_offsets = []
    pos = 0
    for line in html.split('\n'):
        row_start_offsets.append(pos)
        pos += len(line) + 1
    
    tok = tokenizer.HTMLTokenizer(html)
    tag_locations = []
    tag_types = (constants.tokenTypes['StartTag'], constants.tokenTypes['EndTag'])
    for token in tok:
        if not token['type'] in tag_types:
            continue

        # The tokenizer needs to be manually switched to different
        # states when certain tags are encountered.
        if (token['type'] == constants.tokenTypes['StartTag']):
            if (token['name'] == 'script'):
                tok.state = tok.scriptDataState
            elif (token['name'] == 'textarea'):
                tok.state = tok.rcdataState
            elif (token['name'] == 'plaintext'):
                tok.state = tok.plaintextState

        # The stream position tells us the next character after the
        # current tag.  Search backwards from this point to find
        # the beginning of the tag.
        row, col = tok.stream.position()
        tag_end_pos = row_start_offsets[row - 1] + col
        tag_start_chars = '<'
        if token['type'] == constants.tokenTypes['EndTag']:
            tag_start_chars += '/'
        tag_start_chars += token['name']
        tag_start_pos = html.rfind(tag_start_chars, 0, tag_end_pos)
        # If we don't find the start of the tag (which shouldn't
        # happen if the tokenizer is correct) then skip this tag.
        if tag_start_pos < 0:
            continue
            
        tl = TagLoc(token['name'], token['type'], tag_start_pos,
                    tag_end_pos - tag_start_pos)
        tag_locations.append(tl)

    return tag_locations


def count_tags(tag_locations):
    counts = collections.Counter()
    for tl in tag_locations:
        if tl.type == constants.tokenTypes['StartTag']:
            counts[tl.name] += 1
    return counts


def add_spans_to_html(html, tag_locations):
    out = []
    pos = 0
    for tl in tag_locations:
        # Add a <span> around each tag whle escaping all other content.
        if tl.offset > pos:
            out.append(cgi.escape(html[pos:tl.offset]))
            pos = tl.offset

        out.append('<span class="tag-%s">' % tl.name)
        out.append(cgi.escape(html[tl.offset:tl.offset + tl.length]))
        pos += tl.length
        out.append('</span>')

    out.append(cgi.escape(html[pos:]))
    return ''.join(out)


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/api/v1/describe-page')
def describe_page():
    url = flask.request.args.get('url')
    r = requests.get(url)
    if r.status_code == requests.codes.ok:
        tag_locations = parse_tag_locations(r.text)
        tag_counts = count_tags(tag_locations)
        highlighted_html = add_spans_to_html(r.text, tag_locations)
        return flask.jsonify({'success': True,
                              'tag_counts': tag_counts,
                              'highlighted_html': highlighted_html})
    else:
        return flask.jsonify({'success': False})
