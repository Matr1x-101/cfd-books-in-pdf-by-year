#!/usr/bin/env python3
import pywikibot
from pywikibot import pagegenerators, textlib

def has_parent_category(category, target_title, max_depth=2, seen=None, depth=0):
    """
    Check if a category has a given parent category (up to max_depth levels).

    :param category: pywikibot.Category object (starting point)
    :param target_title: str, category title to search for (e.g. "Category:Science")
    :param max_depth: int, recursion depth limit
    :param seen: set, keeps track of visited categories
    :param depth: int, current recursion depth
    :return: bool
    """
    if seen is None:
        seen = set()
    if depth >= max_depth:
        return False

    for parent in category.categories():
        # Skip hidden categories
        if parent.isHiddenCategory():
            continue

        if target_title in parent.title(with_ns=True):
            return True

        if parent not in seen:
            seen.add(parent)
            if has_parent_category(parent, target_title, max_depth, seen, depth + 1):
                return True

    return False

def process_year(year, site):
    pdf_cat = pywikibot.Category(site, f"{year} books PDF files")
    books_cat = pywikibot.Category(site, f"{year} books")

    # If the "(year) books PDF files" category doesn't exist, skip
    if not pdf_cat.exists():
        return

    print(f"Processing {pdf_cat.title()} ...")

    gen = pagegenerators.CategorizedPageGenerator(pdf_cat, recurse=False)

    for page in gen:
        if not page.is_filepage():
            continue

        text = page.text
        categories = list(page.categories())

        # Condition 1: direct membership in "Books in (year)"
        has_books_in_year = any(c == books_cat for c in categories)

        # Condition 2: any parent of file categories is "Books in (year)"
        has_subcat_in_books_in_year = False
        for i in categories:
            if "books PDF files" in i.title():
                continue
            has_subcat_in_books_in_year =  has_parent_category(i, f"{year} books")
            if has_subcat_in_books_in_year:
                break

        print(has_subcat_in_books_in_year)

        new_text = text
        if has_books_in_year or has_subcat_in_books_in_year:
            new_text = textlib.replaceCategoryInPlace(new_text, pdf_cat, None, site)
        else:
            new_text = textlib.replaceCategoryInPlace(new_text, pdf_cat, books_cat, site)

        if new_text != text:
            page.text = new_text
            try:
                page.save(summary=f"Updating categories for {year} books")
            except pywikibot.exceptions.OtherPageSaveError as e:
                print(f"Could not save {page.title()}: {e}")

def main():
    site = pywikibot.Site()
    for year in range(1518, 2026):  # adjust upper bound if needed
        process_year(year, site)

if __name__ == "__main__":
    main()
