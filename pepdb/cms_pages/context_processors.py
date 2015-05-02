def get_site_root(request):
    # NB this returns a core.Page, not the implementation-specific model used
    # so object-comparison to self will return false as objects would differ
    return request.site.root_page


def has_menu_children(page):
    return page.get_children().live().in_menu().exists()


def menu_processor(request):
    menuitems = get_site_root(request).get_children().live().in_menu()

    for menuitem in menuitems:
        menuitem.show_dropdown = has_menu_children(menuitem)

    return {
        'menuitems': menuitems,
    }
