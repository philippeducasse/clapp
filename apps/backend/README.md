Critical N+1 Issues Found

2. FestivalSerializer.update() - contacts handling (serializer.py:73)

Severity: MEDIUM

existing_contacts = {c.id: c for c in instance.contacts.all()}

This line triggers an additional query for each festival being updated. While this is less severe (only happens on update, not list), it could be optimized.

3. ApplicationSerializer.to_representation() (serializer.py:63-81)

Severity: MEDIUM-HIGH

When listing applications, each instance checks its organisation type and fetches the full nested organisation:

if instance.organisation:
if isinstance(instance.organisation, Festival):
data["organisation"] = FestivalSerializer(instance.organisation).data
elif isinstance(instance.organisation, Venue):
data["organisation"] = VenueSerializer(instance.organisation).data
elif isinstance(instance.organisation, Residency):
data["organisation"] = ResidencySerializer(instance.organisation).data

Problem: The GenericForeignKey doesn't use select_related, so accessing instance.organisation triggers a query for each application.
