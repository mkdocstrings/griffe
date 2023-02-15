"""Set redirection pages in docs."""

import mkdocs_gen_files

redirect_map = {
    "usage.md": "../cli_reference",
}

redirect_template = """
<script type="text/javascript">
    window.location.href = "{link}";
</script>
<a href="{link}">Redirecting...</a>
"""

for page, link in redirect_map.items():
    with mkdocs_gen_files.open(page, "w") as fd:
        print(redirect_template.format(link=link), file=fd)
