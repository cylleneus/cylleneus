import re
from html3.html3 import HTML


def as_html(highlights):
    """Return formatted HTML elements for the given results object."""

    for href in highlights:
        htm = HTML()

        h = htm.div()
        if href.urn:
            htm.a(text=r"more...", href=href.urn, klass="card-link exportable")
        h.div(href.author, klass='h5 card-title font-weight-bold exportable')
        h.div(href.title, klass='h5 card-title font-italic exportable')
        if href.reference:
            h.div(href.reference, klass='h6 card-subtitle mb-2 text-muted pt-1 exportable')

        d = htm.div(klass="pt-1 exportable")
        # Process post-match context
        pre_text = re.search(
                r"<pre>(.*?)</pre>(\n\n)?",
                href.text,
                flags=re.DOTALL
            )
        if pre_text:
            if pre_text.group(2):
                klass = 'card-text d-block'
            else:
                klass = 'card-text'
            d.span(pre_text.group(1), klass=f'{klass}')

        # Process matched text
        text = re.search(
                r"<match>(.*?)</match>(\n\n)?",
                href.text,
                flags=re.DOTALL
        )
        t = re.sub(
            r"<em>(.*?)</em>",
            r" \1 ",
            text.group(1),
            flags=re.DOTALL
        )
        if text.group(2):
            klass = 'card-text d-block'
        else:
            klass = 'card-text'
        d.span(t, klass=f'{klass}')

        # Process post-match context
        post_text = re.search(
                r"<post>(.*?)</post>(\n\n)?",
                href.text,
                flags=re.DOTALL
            )
        if post_text:
            if post_text.group(2):
                klass = 'card-text d-block'
            else:
                klass = 'card-text'
            d.span(post_text.group(1), klass=f'{klass}')

        yield str(htm)
