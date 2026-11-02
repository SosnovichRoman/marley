import frappe
from frappe import _

PORTAL_HOME = "/patient-portal"

ALLOWED_EXACT = {
	"/patient-portal",
	"/login",
	"/logout",
	"/update-password",
	"/forgot",
	"/api/method/login",
	"/api/method/logout",
	"/api/method/frappe.core.doctype.user.user.update_password",
	"/socket.io",
}

ALLOWED_PREFIXES = (
	"/patient-portal/",
	"/assets/",
	"/files/",
	"/api/method/healthcare.healthcare.api.patient_portal.",
	"/api/method/payments.",
	"/socket.io/",
)


def is_portal_only_patient(user=None) -> bool:
	"""A patient login with no desk role. Staff who also have Patient are left alone."""
	user = user or frappe.session.user
	if user in ("Guest", "Administrator"):
		return False

	roles = set(frappe.get_roles(user)) - {"All", "Guest"}
	if "Patient" not in roles:
		return False

	if frappe.db.get_value("User", user, "user_type") == "Website User":
		return True

	return not _has_desk_role(roles)


def portal_access_decision(path: str) -> str:
	"""How to treat a path once the caller is known to be a portal-only patient.

	Returns ``allow``, ``redirect`` (send the browser to the portal), or ``deny``
	(an API call outside the portal).
	"""
	path = (path or "").split("?", 1)[0]
	if path in ALLOWED_EXACT or path.startswith(ALLOWED_PREFIXES):
		return "allow"
	if path.startswith("/api/"):
		return "deny"
	return "redirect"


def restrict_patient_portal():
	"""before_request hook. Portal patients never reach the desk, /me, or other APIs."""
	if not is_portal_only_patient():
		return

	# Client cmd is the deprecated RPC channel and runs before the URL.
	# Portal calls go to /api/method/...; Frappe fills cmd from that path after this hook.
	form = getattr(frappe.local, "form_dict", None)
	if form:
		form.pop("cmd", None)

	decision = portal_access_decision(_request_path())
	if decision == "allow":
		return
	if decision == "deny":
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	frappe.local.flags.redirect_location = PORTAL_HOME
	raise frappe.Redirect


def _has_desk_role(roles: set[str]) -> bool:
	if not roles:
		return False
	return bool(frappe.db.exists("Role", {"name": ["in", list(roles)], "desk_access": 1}))


def _request_path() -> str:
	request = getattr(frappe.local, "request", None)
	return getattr(request, "path", None) or ""
