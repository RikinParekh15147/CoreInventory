"""
AI Chat views — send prompt and execute confirmed actions.
"""

import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

from .services import call_groq, execute_action
from apps.products.models import Product
from apps.warehouses.models import Location


@login_required
@require_POST
def chat_send(request):
    """Receive a user prompt, call Groq, return the JSON action plan."""
    try:
        body = json.loads(request.body)
        prompt = body.get('prompt', '').strip()
        history = body.get('history', [])
    except (json.JSONDecodeError, AttributeError):
        prompt = request.POST.get('prompt', '').strip()
        history = []

    if not prompt:
        return JsonResponse({'error': 'Empty prompt.'}, status=400)

    result = call_groq(prompt, request.user, history)

    # For non-confirmation actions (queries), execute immediately
    if not result.get('needs_confirmation', True):
        exec_result = execute_action(result, request.user)
        return JsonResponse({
            'action': result,
            'executed': True,
            'result': exec_result,
        })

    # For mutation actions, return the plan for confirmation
    return JsonResponse({
        'action': result,
        'executed': False,
    })


@login_required
@require_POST
def chat_execute(request):
    """Execute a confirmed action."""
    try:
        body = json.loads(request.body)
        action_json = body.get('action', {})
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid request.'}, status=400)

    if not action_json:
        return JsonResponse({'error': 'No action provided.'}, status=400)

    result = execute_action(action_json, request.user)
    return JsonResponse({'result': result})
@login_required
def chat_metadata(request):
    """Return all active products, locations, and contacts for UI dropdowns."""
    from apps.contacts.models import Supplier, Customer
    products = list(Product.objects.filter(is_active=True).values('id', 'name', 'sku'))
    locations = list(Location.objects.filter(is_active=True).values('id', 'name'))
    suppliers = list(Supplier.objects.filter(is_active=True).values('id', 'name'))
    customers = list(Customer.objects.filter(is_active=True).values('id', 'name'))
    return JsonResponse({
        'products': products,
        'locations': locations,
        'suppliers': suppliers,
        'customers': customers,
    })
