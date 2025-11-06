import frappe
from frappe import _

@frappe.whitelist(allow_guest=True)
def webhook():
    """Endpoint to receive webhook from Meta (WABA). Expects JSON payload."""
    # Frappe's form_dict doesn't parse nested JSON body; try request.get_data
    raw = frappe.local.request.get_data(as_text=True)
    frappe.logger().debug("Webhook raw: %s" % raw)
    try:
        import json
        payload = json.loads(raw)
    except Exception:
        frappe.logger().error("Invalid JSON payload")
        frappe.throw(_("Invalid JSON payload"))

    # Simplified example: parse messages
    entries = payload.get("entry", [])
    for entry in entries:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})
            messages = value.get("messages") or []
            for m in messages:
                process_incoming_message(m, value)
    return "ok"

def process_incoming_message(m, value):
    # m: single message object from WABA
    phone = m.get("from") or value.get("metadata", {}).get("phone_number_id")
    text = None
    content_type = "text"
    if m.get("text"):
        text = m["text"].get("body")
    elif m.get("image"):
        content_type = "image"
        text = m["image"].get("caption") or ""
    # Create or update Contact
    contact = find_or_create_contact(phone, value)
    # Create or update Conversation
    conv = find_or_create_conversation(contact)
    # Create message record
    from frappe.utils.data import now_datetime
    doc = frappe.get_doc({
        "doctype": "CSIS Whatsapp Message",
        "message_id": m.get("id"),
        "conversation": conv.name if conv else None,
        "contact": contact.name if contact else None,
        "direction": "Incoming",
        "content_type": content_type,
        "message": text,
        "sent_at": now_datetime()
    })
    doc.insert(ignore_permissions=True)
    # update conversation last message
    if conv:
        conv.db_set("last_message", text)
        conv.db_set("last_updated", now_datetime())

def find_or_create_contact(phone, value):
    if not phone:
        return None
    phone_clean = phone.strip().lstrip('+')
    existing = frappe.db.get_value("CSIS Contact", {"phone": phone_clean})
    if existing:
        return frappe.get_doc("CSIS Contact", existing)
    # create contact with minimal info
    name = None
    if value.get("contacts"):
        try:
            name = value.get("contacts", [{}])[0].get("profile", {}).get("name")
        except Exception:
            name = None
    doc = frappe.get_doc({
        "doctype": "CSIS Contact",
        "full_name": name or ("WA-"+phone_clean[-6:]),
        "phone": phone_clean
    })
    doc.insert(ignore_permissions=True)
    return doc

def find_or_create_conversation(contact):
    if not contact:
        return None
    conv = frappe.db.get_value("CSIS Whatsapp Conversation", {"contact": contact.name})
    if conv:
        return frappe.get_doc("CSIS Whatsapp Conversation", conv)
    newc = frappe.get_doc({
        "doctype": "CSIS Whatsapp Conversation",
        "contact": contact.name,
        "last_message": "",
    })
    newc.insert(ignore_permissions=True)
    return newc

@frappe.whitelist()
def list_conversations(limit_start=0, limit_page_length=50):
    rows = frappe.db.sql("""
        SELECT name, contact, last_message, last_updated, tags
        FROM `tabCSIS Whatsapp Conversation`
        ORDER BY last_updated DESC NULLS LAST
        LIMIT %s, %s
    """, (int(limit_start), int(limit_page_length)), as_dict=True)
    return rows

@frappe.whitelist()
def list_messages(conversation):
    rows = frappe.db.sql("""
        SELECT name, message_id, contact, direction, content_type, message, sent_at
        FROM `tabCSIS Whatsapp Message`
        WHERE conversation=%s
        ORDER BY sent_at ASC
    """, (conversation,), as_dict=True)
    return rows

@frappe.whitelist()
def send_template(contact, template_name, variables=None):
    """Queue a template message to be sent via Meta WABA. This is a placeholder that
    saves an outgoing CSIS Whatsapp Message with is_template=1.
    """
    doc = frappe.get_doc({
        "doctype": "CSIS Whatsapp Message",
        "message_id": frappe.generate_hash(),
        "contact": contact,
        "direction": "Outgoing",
        "content_type": "text",
        "message": template_name if not variables else template_name + " " + str(variables),
        "is_template": 1,
        "template_name": template_name
    })
    doc.insert()
    # In production, you would enqueue a job to call Meta Graph API here.
    return {"status":"queued", "name": doc.name}
