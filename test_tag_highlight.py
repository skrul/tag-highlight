import tag_highlight

import unittest

class ParseTagLocationsTestCase(unittest.TestCase):
    def test_simple(self):
        html = '<i>hey</i><a><b/>'
        tls = tag_highlight.parse_tag_locations(html)
        self.assertEqual(4, len(tls))
        self.assertEqual((0, 3), (tls[0].offset, tls[0].length))
        self.assertEqual('i', tls[0].name)
        self.assertEqual((6, 4), (tls[1].offset, tls[1].length))
        self.assertEqual('i', tls[1].name)
        self.assertEqual((10, 3), (tls[2].offset, tls[2].length))
        self.assertEqual('a', tls[2].name)
        self.assertEqual((13, 4), (tls[3].offset, tls[3].length))
        self.assertEqual('b', tls[3].name)

class AddSpansToHtmlTestCase(unittest.TestCase):
    def test_simple(self):
        html = '<i a="b">'
        tls = tag_highlight.parse_tag_locations(html)
        formatted = tag_highlight.add_spans_to_html(html, tls)
        self.assertEqual('<span class="tag-i">&lt;i a="b"&gt;</span>', formatted)
        
    def test_content(self):
        html = '1<i>2</i>3'
        tls = tag_highlight.parse_tag_locations(html)
        formatted = tag_highlight.add_spans_to_html(html, tls)
        self.assertEqual(
            '1<span class="tag-i">&lt;i&gt;</span>2<span class="tag-i">' +
            '&lt;/i&gt;</span>3', formatted)

    def test_escaping(self):
        html = '&amp;<p/>&lt;<p/>&gt;'
        tls = tag_highlight.parse_tag_locations(html)
        formatted = tag_highlight.add_spans_to_html(html, tls)
        self.assertEqual('&amp;amp;<span class="tag-p">&lt;p/&gt;</span>' +
            '&amp;lt;<span class="tag-p">&lt;p/&gt;</span>&amp;gt;', formatted)

class CountTagsTestCase(unittest.TestCase):
    def test_count(self):
        html = '<i></i><p/><a></a><a></a>'
        tls = tag_highlight.parse_tag_locations(html)
        counts = tag_highlight.count_tags(tls)
        self.assertEqual({'i': 1, 'p': 1, 'a': 2}, counts)
