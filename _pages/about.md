---
layout: about
title: about
permalink: /
subtitle:

profile:
  align: right
  image: Saleh.jpg
  image_circular: true
  more_info: >
    <p><a href="/assets/pdf/cv.pdf">CV (PDF)</a></p>

selected_papers: true
social: true

announcements:
  enabled: false
latest_posts:
  enabled: false
---

{% assign p = site.data.cv.profile %}

{{ p.bio | markdownify }}

{{ p.current | markdownify }}

**Research interests:** {{ p.interests | join: " · " }}

### Software

<ul>
{%- for s in site.data.cv.software %}
<li><a href="https://github.com/{{ s.repo }}"><b>{{ s.name }}</b></a> — {{ s.description }}</li>
{%- endfor %}
</ul>
