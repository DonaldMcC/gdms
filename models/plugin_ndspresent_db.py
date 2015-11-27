# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
# this is developed from presentation demo on web2pyslices developed by Mariano Reingart

# Need a sensible method of putting graphics etc

db.define_table("plugin_presentation",
    Field("name"),
    Field("title"),
    Field("description"),
    Field("keywords"),
    Field("author"),
    Field("markmin", "text")
    )

db.define_table("plugin_slide",
    Field("presentation_id", db.plugin_presentation),
    Field("div_class", "string", default="slide"),
    Field("div_id", "string", default="",
        requires=IS_IN_SET(['title-slide', 'page-title_article', 'page-title_homepage', 'page-title_channel','page-title_column', 'seo-instruction', 'page_description', 'summary'])),
    Field("markmin", "text"),
    Field("notes", "text"),
    Field("item1", "text"),
    Field("item2", "text"),
    Field("item3", "text"),
    Field("media", "upload"),
    Field("positions","list:integer")
    )
