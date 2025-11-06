import frappe
from frappe import _
def sync_messages():
    """Cron job: poll Meta WABA for messages or process queue.
    This is a placeholder — in production use webhooks for near real-time updates.
    """
    frappe.logger().info("sync_messages: running sync placeholder")
    # Find outgoing template messages and simulate sending (placeholder)
    rows = frappe.get_all("CSIS Whatsapp Message", filters={"direction":"Outgoing", "is_template":1}, fields=["name","contact","template_name"])
    for r in rows:
        # Simulate being sent
        frappe.db.set_value("CSIS Whatsapp Message", r.name, "sent_at", frappe.utils.now_datetime())
        frappe.db.set_value("CSIS Whatsapp Message", r.name, "message", frappe.db.get_value("CSIS Whatsapp Message", r.name, "message")+"\n\n[Simulated sent]")
