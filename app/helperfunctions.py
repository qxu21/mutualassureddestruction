def sum_form(form):
    total = 0
    for field in form:
        if field.name == "csrf_token":
            continue #skip hidden csrf field
        total += field.data
    return total
