import frappe
from frappe.model.document import Document

class CSISContact(Document):
    def on_update(self):
        # ensure no leading plus on phone
        if self.phone:
            self.phone = self.phone.strip().lstrip('+')
