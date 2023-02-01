from products.forms import ProductSearchForm


def add_variable_to_context(request):
    return {
        'search_form': ProductSearchForm,
    }