import re

from html3.html3 import HTML


def as_html(highlights):
    """Return formatted HTML elements for the given results object."""

    for href in highlights:
        htm = HTML()

        htm.div(href.author, klass='h5 card-title font-weight-bold')
        htm.div(href.title, klass='h5 card-title font-italic')
        if href.urn:
            htm.a(text=r"more &rarr;", href=href.urn, klass="card-link")
        htm.div(href.reference, klass='h6 card-subtitle mb-2 text-muted')

        # Process post-match context
        pre_text = re.search(
                r"<pre>(.*?)</pre>",
                href.text,
                flags=re.DOTALL
            )
        if pre_text:
            htm.span(pre_text.group(1), klass='card-text')

        # Process matched text
        text = re.search(
                r"<match>(.*?)</match>",
                href.text,
                flags=re.DOTALL
        ).group(1)
        text = re.sub(
            r"<em>(.*?)</em>",
            r"\1",
            text,
            flags=re.DOTALL
        )
        htm.span(text, klass='card-text')

        # Process post-match context
        post_text = re.search(
                r"<post>(.*?)</post>",
                href.text,
                flags=re.DOTALL
            )
        if post_text:
            htm.span(post_text.group(1), klass='card-text')

        yield str(htm)
