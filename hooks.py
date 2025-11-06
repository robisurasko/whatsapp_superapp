app_name = "whatsapp_superapp"
app_title = "Whatsapp Superapp"
app_publisher = "Robi Tejo Surasko"
app_description = "CSIS Whatsapp integration scaffold"
app_email = "admin@robi.my.id"
app_license = "MIT"

# Include doctype JS
doctype_js = {
    "CSIS Whatsapp Message": "public/js/csis_whatsapp_message.js",
    "CSIS Whatsapp Conversation": "public/js/csis_whatsapp_conversation.js",
}

app_include_js = ["whatsapp_superapp.bundle.js"]

# Whitelisted methods (API)
doc_events = {
}

# API routes (whitelisted methods)
override_whitelisted_methods = {
}

# Add methods
# Example: /api/method/whatsapp_superapp.api.webhook
# Make scheduler placeholder
scheduler_events = {
    "cron": {
        "*/1 * * * *": [
            "whatsapp_superapp.tasks.sync_messages"
        ]
    }
}
