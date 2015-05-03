import tag_highlight
import application

import httpretty
import json
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

    def test_tokenizer_state_script(self):
        html = '<script><foo></script><bar>'
        tls = tag_highlight.parse_tag_locations(html)
        self.assertEqual(3, len(tls))

    def test_tokenizer_state_textarea(self):
        html = '<textarea><foo></textarea><bar>'
        tls = tag_highlight.parse_tag_locations(html)
        self.assertEqual(3, len(tls))

    def test_tokenizer_state_plaintext(self):
        html = '<plaintext><foo>'
        tls = tag_highlight.parse_tag_locations(html)
        self.assertEqual(1, len(tls))


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


class DescribePageTestCase(unittest.TestCase):
    def setUp(self):
        self.app = application.application.test_client()

    @httpretty.activate
    def test_success(self):
        httpretty.register_uri(httpretty.GET, "http://example.com/",
                               body="<html></html>")
        r = json.loads(self.app.get(
            '/api/v1/describe-page?url=http://example.com/').data)
        self.assertEqual(True, r['success'])
        self.assertEqual(
            '<span class="tag-html">&lt;html&gt;</span><span class="tag-html">' +
            '&lt;/html&gt;</span>', r['highlighted_html'])
        self.assertEqual({'html': 1}, r['tag_counts'])

    @httpretty.activate
    def test_failed(self):
        httpretty.register_uri(httpretty.GET, "http://example.com/",
                               status=404)
        r = json.loads(self.app.get(
            '/api/v1/describe-page?url=http://example.com/').data)
        self.assertEqual(False, r['success'])
