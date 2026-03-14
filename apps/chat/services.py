"""
AI Chat services — Groq LLM integration for natural-language inventory ops.
"""

import json
import logging
from decimal import Decimal, InvalidOperation
from datetime import date

from django.conf import settings
from django.db.models import Sum

from groq import Groq

from apps.products.models import Product, ProductCategory, UnitOfMeasure
from apps.warehouses.models import Warehouse, Location
from apps.receipts.models import Receipt, ReceiptLine
from apps.deliveries.models import Delivery, DeliveryLine
from apps.transfers.models import Transfer, TransferLine
from apps.adjustments.models import Adjustment, AdjustmentLine
from apps.ledger.models import Stock, StockMove

logger = logging.getLogger(__name__)

GROQ_MODEL = 'llama-3.3-70b-versatile'


# ─── System Prompt ────────────────────────────────────────────────
SYSTEM_PROMPT = """You are CoreInventory AI — an intelligent assistant for a warehouse inventory management system.
You understand natural language requests and convert them into structured JSON actions.

## Available Models & Schema

### Product
- Fields: id, name, sku (auto-generated PRD-XXXXXX), category (FK), unit (FK), description, reorder_point, is_active
- Related: stock_records (Stock), receipt_lines, delivery_lines, transfer_lines, adjustment_lines

### Warehouse
- Fields: id, name, address, is_active
- Has many Locations

### Location
- Fields: id, warehouse (FK), name (e.g. "Rack A-1"), is_active
- Display format: "Warehouse Name / Location Name"

### Stock
- Fields: product (FK), location (FK), quantity
- Represents current stock per product per location

### Receipt (incoming stock)
- Fields: id, ref (RCP-YYYY-NNNN), supplier_name, supplier_contact, destination (Location FK), status, scheduled_date, notes
- Status flow: draft → waiting → ready → done (or cancelled at any stage)
- Lines: product (FK), expected_qty, received_qty, unit (FK), notes

### Delivery (outgoing stock)
- Fields: id, ref (DLV-YYYY-NNNN), customer_name, customer_contact, source (Location FK), status, scheduled_date, notes
- Status flow: draft → waiting → ready → done (or cancelled at any stage)
- Lines: product (FK), requested_qty, delivered_qty, unit (FK), notes

### Transfer (internal move between locations)
- Fields: id, ref (TRF-YYYY-NNNN), from_location (FK), to_location (FK), status, scheduled_date, notes
- Lines: product (FK), qty, unit (FK)

### Adjustment (stock corrections)
- Fields: id, ref (ADJ-YYYY-NNNN), location (FK), reason (damage|theft|count_correction|expiry|other), notes, status
- Status flow: draft → done (or cancelled)
- Lines: product (FK), recorded_qty, actual_qty, unit (FK)

## Available Actions

You MUST return a JSON object with this exact structure:
{
  "action_type": "<one of the types below>",
  "summary": "<human-readable description of what will happen>",
  "data": { <action-specific data> },
  "needs_confirmation": <true for mutations, false for queries>
}

### Action Types:

1. **query_products** — Search/list products
   data: { "filters": {"search": "...", "category": "...", "low_stock_only": bool} }

2. **query_stock** — Check stock levels
   data: { "product_name": "...", "warehouse_name": "..." }

3. **create_receipt** — Create incoming receipt
   data: { "supplier_name": "...", "supplier_contact": "...", "destination_location": "Warehouse / Location", "scheduled_date": "YYYY-MM-DD", "notes": "...", "lines": [{"product_name": "...", "expected_qty": N, "unit": "..."}] }

4. **create_delivery** — Create outgoing delivery
   data: { "customer_name": "...", "customer_contact": "...", "source_location": "Warehouse / Location", "scheduled_date": "YYYY-MM-DD", "notes": "...", "lines": [{"product_name": "...", "requested_qty": N, "unit": "..."}] }

5. **create_transfer** — Create internal transfer
   data: { "from_location": "Warehouse / Location", "to_location": "Warehouse / Location", "scheduled_date": "YYYY-MM-DD", "notes": "...", "lines": [{"product_name": "...", "qty": N, "unit": "..."}] }

6. **create_adjustment** — Create stock adjustment
   data: { "location": "Warehouse / Location", "reason": "damage|theft|count_correction|expiry|other", "notes": "...", "lines": [{"product_name": "...", "recorded_qty": N, "actual_qty": N, "unit": "..."}] }

7. **update_status** — Change status of a receipt/delivery/transfer/adjustment
   data: { "document_type": "receipt|delivery|transfer|adjustment", "ref": "RCP-2026-0001", "new_status": "waiting|ready|done|cancelled" }

8. **general_answer** — For informational questions (no mutation)
   data: { "answer": "..." }

9. **request_info** — When critical data is missing (e.g., location, product, quantity) needed to perform a requested mutation.
   data: { "question": "What is the specific missing information you need from the user? Example: 'Which warehouse should I create this receipt in?'" }

## Rules:
- For dates, if none specified use today's date.
- Match product names and locations fuzzily from the context provided.
- Context Accumulation: If you are in a multi-turn conversation asking for information (using `request_info`), you MUST remember the details the user provided in previous turns. When you finally have all the information and return a mutation action (e.g., `create_receipt`), its `data` object MUST include ALL the accumulated fields from the entire conversation history.
- If the user asks to create/update something but misses a CRITICAL detail (like product name, location, or quantity), you MUST use `action_type: "request_info"` instead of guessing or executing. Set the summary to the question you want to ask. Set needs_confirmation to false.
- For queries (query_products, query_stock, general_answer, request_info), set needs_confirmation to false.
- For ALL mutations (create_*, update_*), set needs_confirmation to true.
- Before suggesting a mutation, verify the user has the required permission listed in the context. If they do not, use `general_answer` to explain they lack permission.
- Always reply in valid JSON. No extra text before or after the JSON.
"""

def _build_context(user=None):
    """Gather current DB state for LLM context, including user permissions."""
    # Products with stock
    products = Product.objects.filter(is_active=True).select_related('category', 'unit')
    product_list = []
    for p in products[:50]:  # cap to avoid token overflow
        stock_total = (
            Stock.objects.filter(product=p)
            .aggregate(total=Sum('quantity'))['total'] or 0
        )
        product_list.append(
            f"  - {p.name} (SKU: {p.sku}, Unit: {p.unit.abbreviation}, "
            f"Stock: {stock_total}, Reorder Point: {p.reorder_point})"
        )

    # Warehouses & locations
    warehouses = Warehouse.objects.filter(is_active=True).prefetch_related('locations')
    wh_list = []
    for wh in warehouses:
        locs = [f"{wh.name} / {loc.name}" for loc in wh.locations.filter(is_active=True)]
        wh_list.append(f"  - {wh.name}: locations = [{', '.join(locs)}]")

    # Units
    units = UnitOfMeasure.objects.all()
    unit_list = [f"  - {u.name} ({u.abbreviation})" for u in units]

    # Recent operations
    recent_receipts = Receipt.objects.order_by('-created_at')[:5]
    recent_deliveries = Delivery.objects.order_by('-created_at')[:5]

    rcpt_list = [
        f"  - {r.ref} | {r.supplier_name} | status: {r.status} | {r.scheduled_date}"
        for r in recent_receipts
    ]
    dlv_list = [
        f"  - {d.ref} | {d.customer_name} | status: {d.status} | {d.scheduled_date}"
        for d in recent_deliveries
    ]


    # User permissions
    user_context = "Unknown User"
    if user:
        role_name = user.role.name if user.role else "No Role"
        perms = [rp.permission.codename for rp in user.role.role_permissions.all() if rp.granted] if user.role and hasattr(user.role, 'role_permissions') else []
        user_context = f"User: {user.full_name or user.email} | Role: {role_name}\nGranted Permissions: {', '.join(perms) if perms else 'None'}"

    context = f"""
## Current Database State

### Current User (Permissions)
{user_context}

### Products (active, up to 50):
{chr(10).join(product_list) if product_list else '  (none)'}

### Warehouses & Locations:
{chr(10).join(wh_list) if wh_list else '  (none)'}

### Units of Measure:
{chr(10).join(unit_list) if unit_list else '  (none)'}

### Recent Receipts:
{chr(10).join(rcpt_list) if rcpt_list else '  (none)'}

### Recent Deliveries:
{chr(10).join(dlv_list) if dlv_list else '  (none)'}

### Today's Date: {date.today().isoformat()}
"""
    return context


def call_groq(user_prompt, user=None, history=None):
    """Send prompt to Groq and return parsed JSON action."""
    if history is None:
        history = []
        
    client = Groq(api_key=settings.GROQ_API_KEY)
    context = _build_context(user)
    
    system_content = f"{SYSTEM_PROMPT}\n\n{context}"
    messages = [{"role": "system", "content": system_content}]
    
    # Add recent history (limit to avoid token overflow)
    for msg in history[-10:]:
        role = "assistant" if msg.get("role") == "ai" else "user"
        content = msg.get("content", "")
        # Strip HTML tags or complex formatting if needed, but raw string is okay for Groq
        if content:
            messages.append({"role": role, "content": content})
            
    # Add current prompt
    messages.append({"role": "user", "content": f"## User Request:\n{user_prompt}"})

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=2048,
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error("Groq returned invalid JSON: %s", e)
        return {
            "action_type": "general_answer",
            "summary": "Sorry, I couldn't process that request. Please try again.",
            "data": {"answer": "Failed to parse AI response."},
            "needs_confirmation": False,
        }
    except Exception as e:
        logger.error("Groq API error: %s", e)
        return {
            "action_type": "general_answer",
            "summary": f"API error: {str(e)}",
            "data": {"answer": f"Error contacting AI service: {str(e)}"},
            "needs_confirmation": False,
        }


# ─── Location Resolver ────────────────────────────────────────────

def _resolve_location(location_str):
    """Resolve 'Warehouse / Location' string to a Location object."""
    if not location_str:
        return None
    parts = [p.strip() for p in location_str.split('/')]
    if len(parts) == 2:
        wh_name, loc_name = parts
        loc = Location.objects.filter(
            warehouse__name__icontains=wh_name,
            name__icontains=loc_name,
            is_active=True,
        ).first()
        if loc:
            return loc
    # Fallback: try matching location name alone
    loc = Location.objects.filter(name__icontains=location_str, is_active=True).first()
    return loc


def _resolve_product(product_name):
    """Resolve product name to Product object (fuzzy match)."""
    # Try exact first
    p = Product.objects.filter(name__iexact=product_name, is_active=True).first()
    if p:
        return p
    # Try contains
    p = Product.objects.filter(name__icontains=product_name, is_active=True).first()
    if p:
        return p
    # Try SKU
    p = Product.objects.filter(sku__iexact=product_name, is_active=True).first()
    return p


def _resolve_unit(unit_str):
    """Resolve unit name or abbreviation to UnitOfMeasure."""
    u = UnitOfMeasure.objects.filter(abbreviation__iexact=unit_str).first()
    if u:
        return u
    u = UnitOfMeasure.objects.filter(name__icontains=unit_str).first()
    return u


def _parse_date(date_str):
    """Parse YYYY-MM-DD string to date, fallback to today."""
    try:
        return date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return date.today()


# ─── Action Executors ─────────────────────────────────────────────

def execute_action(action_json, user):
    """Route and execute a confirmed action. Returns dict with result."""
    action_type = action_json.get('action_type', '')
    data = action_json.get('data', {})

    executors = {
        'query_products': _exec_query_products,
        'query_stock': _exec_query_stock,
        'create_receipt': _exec_create_receipt,
        'create_delivery': _exec_create_delivery,
        'create_transfer': _exec_create_transfer,
        'create_adjustment': _exec_create_adjustment,
        'update_status': _exec_update_status,
        'general_answer': _exec_general_answer,
        'request_info': _exec_request_info,
    }

    # Extract required permission dynamically based on action mappings (ONLY FOR MUTATIONS)
    req_perms = {
        'create_receipt': 'can_create_receipt',
        'create_delivery': 'can_create_delivery',
        'create_transfer': 'can_create_transfer',
        'create_adjustment': 'can_create_adjustment',
        'update_status': 'can_approve_documents', # Or a similar permission if you have one
    }
    
    # Check permissions if mapped
    if action_type in req_perms and user.role:
        perm_code = req_perms[action_type]
        has_perm = user.role.role_permissions.filter(permission__codename=perm_code, granted=True).exists()
        if not has_perm:
             return {'success': False, 'message': f'Lacking permission: {perm_code}. Action rejected.'}

    executor = executors.get(action_type)
    if not executor:
        return {'success': False, 'message': f'Unknown action type: {action_type}'}

    try:
        return executor(data, user)
    except Exception as e:
        logger.exception("Error executing action %s", action_type)
        return {'success': False, 'message': f'Error: {str(e)}'}


def _exec_query_products(data, user):
    """Query products based on filters."""
    qs = Product.objects.filter(is_active=True).select_related('category', 'unit')
    filters = data.get('filters', {})

    if filters.get('search'):
        qs = qs.filter(name__icontains=filters['search'])
    if filters.get('category'):
        qs = qs.filter(category__name__icontains=filters['category'])

    products = []
    for p in qs[:30]:
        stock_total = (
            Stock.objects.filter(product=p)
            .aggregate(total=Sum('quantity'))['total'] or 0
        )
        is_low = stock_total <= p.reorder_point
        if filters.get('low_stock_only') and not is_low:
            continue
        products.append({
            'name': p.name,
            'sku': p.sku,
            'category': p.category.name if p.category else '—',
            'unit': p.unit.abbreviation,
            'stock': float(stock_total),
            'reorder_point': float(p.reorder_point),
            'low_stock': is_low,
        })

    return {
        'success': True,
        'message': f'Found {len(products)} product(s).',
        'result_type': 'product_list',
        'products': products,
    }


def _exec_query_stock(data, user):
    """Query stock levels for a specific product/warehouse."""
    product_name = data.get('product_name', '')
    warehouse_name = data.get('warehouse_name', '')

    qs = Stock.objects.select_related('product', 'location', 'location__warehouse')

    if product_name:
        qs = qs.filter(product__name__icontains=product_name)
    if warehouse_name:
        qs = qs.filter(location__warehouse__name__icontains=warehouse_name)

    records = []
    for s in qs[:50]:
        records.append({
            'product': s.product.name,
            'location': str(s.location),
            'quantity': float(s.quantity),
        })

    return {
        'success': True,
        'message': f'Found {len(records)} stock record(s).',
        'result_type': 'stock_list',
        'stock': records,
    }


def _exec_create_receipt(data, user):
    """Create a receipt with line items."""
    dest = _resolve_location(data.get('destination_location', ''))
    if not dest:
        return {'success': False, 'message': f"Could not find location: {data.get('destination_location')}"}

    receipt = Receipt.objects.create(
        supplier_name=data.get('supplier_name', 'Unknown Supplier'),
        supplier_contact=data.get('supplier_contact', ''),
        destination=dest,
        status='draft',
        scheduled_date=_parse_date(data.get('scheduled_date')),
        notes=data.get('notes', ''),
        created_by=user,
    )

    lines_created = 0
    for line_data in data.get('lines', []):
        product = _resolve_product(line_data.get('product_name', ''))
        if not product:
            continue
        unit = _resolve_unit(line_data.get('unit', '')) or product.unit
        try:
            qty = Decimal(str(line_data.get('expected_qty', 0)))
        except (InvalidOperation, TypeError):
            qty = Decimal('0')

        ReceiptLine.objects.create(
            receipt=receipt,
            product=product,
            expected_qty=qty,
            received_qty=Decimal('0'),
            unit=unit,
        )
        lines_created += 1

    return {
        'success': True,
        'message': f'Receipt {receipt.ref} created with {lines_created} line(s).',
        'ref': receipt.ref,
        'id': receipt.pk,
    }


def _exec_create_delivery(data, user):
    """Create a delivery with line items."""
    source = _resolve_location(data.get('source_location', ''))
    if not source:
        return {'success': False, 'message': f"Could not find location: {data.get('source_location')}"}

    delivery = Delivery.objects.create(
        customer_name=data.get('customer_name', 'Unknown Customer'),
        customer_contact=data.get('customer_contact', ''),
        source=source,
        status='draft',
        scheduled_date=_parse_date(data.get('scheduled_date')),
        notes=data.get('notes', ''),
        created_by=user,
    )

    lines_created = 0
    for line_data in data.get('lines', []):
        product = _resolve_product(line_data.get('product_name', ''))
        if not product:
            continue
        unit = _resolve_unit(line_data.get('unit', '')) or product.unit
        try:
            qty = Decimal(str(line_data.get('requested_qty', 0)))
        except (InvalidOperation, TypeError):
            qty = Decimal('0')

        DeliveryLine.objects.create(
            delivery=delivery,
            product=product,
            requested_qty=qty,
            delivered_qty=Decimal('0'),
            unit=unit,
        )
        lines_created += 1

    return {
        'success': True,
        'message': f'Delivery {delivery.ref} created with {lines_created} line(s).',
        'ref': delivery.ref,
        'id': delivery.pk,
    }


def _exec_create_transfer(data, user):
    """Create a transfer with line items."""
    from_loc = _resolve_location(data.get('from_location', ''))
    to_loc = _resolve_location(data.get('to_location', ''))
    if not from_loc:
        return {'success': False, 'message': f"Could not find source location: {data.get('from_location')}"}
    if not to_loc:
        return {'success': False, 'message': f"Could not find destination location: {data.get('to_location')}"}

    transfer = Transfer.objects.create(
        from_location=from_loc,
        to_location=to_loc,
        status='draft',
        scheduled_date=_parse_date(data.get('scheduled_date')),
        notes=data.get('notes', ''),
        created_by=user,
    )

    lines_created = 0
    for line_data in data.get('lines', []):
        product = _resolve_product(line_data.get('product_name', ''))
        if not product:
            continue
        unit = _resolve_unit(line_data.get('unit', '')) or product.unit
        try:
            qty = Decimal(str(line_data.get('qty', 0)))
        except (InvalidOperation, TypeError):
            qty = Decimal('0')

        TransferLine.objects.create(
            transfer=transfer,
            product=product,
            qty=qty,
            unit=unit,
        )
        lines_created += 1

    return {
        'success': True,
        'message': f'Transfer {transfer.ref} created with {lines_created} line(s).',
        'ref': transfer.ref,
        'id': transfer.pk,
    }


def _exec_create_adjustment(data, user):
    """Create an adjustment with line items."""
    location = _resolve_location(data.get('location', ''))
    if not location:
        return {'success': False, 'message': f"Could not find location: {data.get('location')}"}

    reason = data.get('reason', 'other')
    valid_reasons = ['damage', 'theft', 'count_correction', 'expiry', 'other']
    if reason not in valid_reasons:
        reason = 'other'

    adjustment = Adjustment.objects.create(
        location=location,
        reason=reason,
        notes=data.get('notes', ''),
        status='draft',
        created_by=user,
    )

    lines_created = 0
    for line_data in data.get('lines', []):
        product = _resolve_product(line_data.get('product_name', ''))
        if not product:
            continue
        unit = _resolve_unit(line_data.get('unit', '')) or product.unit
        try:
            recorded = Decimal(str(line_data.get('recorded_qty', 0)))
            actual = Decimal(str(line_data.get('actual_qty', 0)))
        except (InvalidOperation, TypeError):
            recorded = Decimal('0')
            actual = Decimal('0')

        AdjustmentLine.objects.create(
            adjustment=adjustment,
            product=product,
            recorded_qty=recorded,
            actual_qty=actual,
            unit=unit,
        )
        lines_created += 1

    return {
        'success': True,
        'message': f'Adjustment {adjustment.ref} created with {lines_created} line(s).',
        'ref': adjustment.ref,
        'id': adjustment.pk,
    }


def _exec_update_status(data, user):
    """Update the status of a document."""
    doc_type = data.get('document_type', '')
    ref = data.get('ref', '')
    new_status = data.get('new_status', '')

    model_map = {
        'receipt': Receipt,
        'delivery': Delivery,
        'transfer': Transfer,
        'adjustment': Adjustment,
    }

    model = model_map.get(doc_type)
    if not model:
        return {'success': False, 'message': f'Unknown document type: {doc_type}'}

    doc = model.objects.filter(ref__iexact=ref).first()
    if not doc:
        return {'success': False, 'message': f'{doc_type.title()} {ref} not found.'}

    # Validate transition
    valid_transitions = {
        'draft': ['waiting', 'cancelled'],
        'waiting': ['ready', 'cancelled'],
        'ready': ['done', 'cancelled'],
    }

    allowed = valid_transitions.get(doc.status, [])

    # Special case for adjustments: draft → done directly
    if doc_type == 'adjustment' and doc.status == 'draft':
        allowed = ['done', 'cancelled']

    if new_status not in allowed:
        return {
            'success': False,
            'message': f'Cannot change {doc_type} {ref} from "{doc.status}" to "{new_status}". '
                       f'Allowed transitions: {", ".join(allowed) if allowed else "none"}',
        }

    # For receipts going to 'done', use the service
    if doc_type == 'receipt' and new_status == 'done':
        try:
            from apps.receipts.services import validate_receipt
            validate_receipt(doc, user)
            return {'success': True, 'message': f'Receipt {ref} validated and completed.'}
        except ValueError as e:
            return {'success': False, 'message': str(e)}

    doc.status = new_status
    if new_status == 'done' and hasattr(doc, 'validated_by'):
        doc.validated_by = user
        from django.utils import timezone
        doc.validated_at = timezone.now()
    doc.save()

    return {'success': True, 'message': f'{doc_type.title()} {ref} status changed to "{new_status}".'}


def _exec_general_answer(data, user):
    """Return informational answer — no mutation."""
    return {
        'success': True,
        'message': data.get('answer', 'No answer provided.'),
        'result_type': 'text',
    }


def _exec_request_info(data, user):
    """Return requested info question — no mutation."""
    return {
        'success': True,
        'message': data.get('question', 'Could you provide more details?'),
        'result_type': 'text',
    }


def generate_user_insights(user):
    """
    Generate actionable AI insights based on the current database state
    and save them as Notifications for the given user.
    """
    from apps.alerts.models import Notification
    client = Groq(api_key=settings.GROQ_API_KEY)
    context = _build_context()
    
    prompt = f"""
{context}

Based on the above inventory state, please provide exactly 3 actionable insights or warnings for the warehouse manager.
Consider low stock items, lack of pending receipts, high volume of pending deliveries vs available stock, etc.

Return the result as a JSON object with this exact structure, no extra text:
{{
  "insights": [
    "Insight 1 text...",
    "Insight 2 text...",
    "Insight 3 text..."
  ]
}}
"""

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are an inventory analyst AI. Focus on actionable insights."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=1024,
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        insights = data.get('insights', [])
        
        # Keep things fresh: remove old insights for this user
        Notification.objects.filter(user=user, type='ai_insight').delete()
        
        for ins in insights:
            Notification.objects.create(
                user=user,
                type='ai_insight',
                message=ins,
                is_read=False
            )
            
        return {"success": True, "count": len(insights)}

    except Exception as e:
        logger.error("Error generating AI insights: %s", e)
        return {"success": False, "message": str(e)}
