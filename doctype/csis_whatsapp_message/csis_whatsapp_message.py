import frappe
from frappe.model.document import Document

class CSISWhatsappMessage(Document):
    def before_insert(self):
        # normalize phone on contact link if string provided
        if getattr(self, 'contact', None):
            try:
                c = frappe.get_doc('CSIS Contact', self.contact)
                self.contact = c.name
            except Exception:
                pass
