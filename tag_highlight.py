#!/usr/bin/env python
import cgi
import flask
import flask_bootstrap
import html5lib
from html5lib import tokenizer
from html5lib import constants

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
            
        tag_location = TagLoc(token['name'], token['type'], tag_start_pos,
                              tag_end_pos - tag_start_pos)
        tag_locations.append(tag_location)

    return tag_locations

def add_spans_to_html(html, tag_locations):
    out = []
    pos = 0
    for tag_location in tag_locations:
        # Add a <span> around each tag whle escaping all other contnet.
        if tag_location.offset > pos:
            out.append(cgi.escape(html[pos:tag_location.offset]))
            pos = tag_location.offset

        name = tag_location.name
        out.append('<span class="tag-%s">' % name)
        out.append(cgi.escape(
            html[tag_location.offset:tag_location.offset + tag_location.length]))
        pos += tag_location.length
        out.append('</span>')

    out.append(cgi.escape(html[pos:]))
    return ''.join(out)


app = flask.Flask(__name__)

@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/api/v1/describe-page')
def describe_page():
    return flask.jsonify({})



if __name__ == '__main__':
    flask_bootstrap.Bootstrap(app)
    app.run(debug=True)
    
