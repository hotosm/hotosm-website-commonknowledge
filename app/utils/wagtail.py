def localized_pages(pages):
    return list({p.specific.localized for p in list(pages)})
