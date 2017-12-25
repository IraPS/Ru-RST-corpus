# -*- coding: utf-8 -*-

import os
import re

for html in os.listdir('./backend/templates/'):
    if html.endswith('.html'):
        print(html)

        html_file = open('./backend/templates/' + html, 'r', encoding='utf-8')
        html_text = html_file.read()
        html_file.close()

        html_static_links_href = re.findall('href="(/static/(.*?))"', html_text)
        html_static_links_src = re.findall('src="(/static/(.*?))"', html_text)

        for link in html_static_links_href:
            html_text = re.sub(link[0], "{{url_for('static', filename='" + link[1] + "')}}", html_text)

        for link in html_static_links_src:
            html_text = re.sub(link[0], "{{url_for('static', filename='" + link[1] + "')}}", html_text)

        html_file = open('./backend/templates/' + html, 'w', encoding='utf-8')
        html_file.write(html_text)
        html_file.close()
