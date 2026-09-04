Filtering with a sliced queryset raises TypeError instead of resolving

Description

When you pass a sliced queryset as the value of an __in lookup, Django raises
"Cannot filter a query once a slice has been taken." even though the sliced
queryset is being used as a subquery, not being filtered itself.

Steps to reproduce:

    inner = Author.objects.filter(age__gt=30)[:5]
    Book.objects.filter(author__in=inner)

Expected: the ORM compiles the inner queryset into a LIMIT subquery.
Actual: TypeError is raised at resolve_lookup_value.

This worked in 3.2 and regressed somewhere in 4.0. I bisected it to the change
that started calling resolve_expression() on every filter value that exposes
it, without first checking whether the queryset had already been sliced.

I think the fix is to guard the resolve_expression() call on
value.query.is_sliced, but I am not confident that is the right layer -- it
may belong in Query.check_related_objects instead. Happy to write the patch
if someone can confirm which of the two is preferred.
