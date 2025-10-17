from applications.models import Application
from organisations.festivals.models import Festival
from django.contrib.contenttypes.models import ContentType
from difflib import SequenceMatcher


def similarity(a: str, b: str) -> int:
    """Calculate similarity ratio between two strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


festival_ct = ContentType.objects.get(model="festival")
orphaned = Application.objects.filter(
    content_type=festival_ct, object_id__isnull=True, email_subject__isnull=False
)

print(f"Found {orphaned.count()} orphaned applications with email subjects\n")

all_festivals = list(Festival.objects.all())

matched = 0
unmatched = []

for app in orphaned:
    email_subject = app.email_subject
    best_match = None
    best_score = 0

    for festival in all_festivals:
        if festival.name.lower() in email_subject.lower():
            score = similarity(festival.name, email_subject)
            if score > best_score:
                best_score = score
                best_match = festival

    if best_match and best_score > 0.3:
        print(f"✓ App {app.id}: '{email_subject}'")
        print(f"  → Matched to: {best_match.name} (score: {best_score:.2f})")

        # Save the match
        app.object_id = best_match.id
        app.save()

        matched += 1
    else:
        print(f"✗ App {app.id}: '{email_subject}'")
        print(
            f"  → No good match found (best: {best_match.name if best_match else 'None'}, score: {best_score:.2f})"
        )
        unmatched.append((app, email_subject))

print(f"\n{'=' * 60}")
print(f"Matched: {matched}/{orphaned.count()}")
print(f"Unmatched: {len(unmatched)}")

if unmatched:
    print(f"\n{'=' * 60}")
    print("Unmatched applications that need manual review:")
    for app, subject in unmatched:
        print(f"  App {app.id}: {subject}")

print("\n✓ Script completed!")
