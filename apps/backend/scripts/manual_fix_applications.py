from applications.models import Application
from organisations.festivals.models import Festival
from django.contrib.contenttypes.models import ContentType

# Manual matches
manual_matches = {
    17: "Brueckensensationen",  # or the exact name in your DB
    20: "Friedrichshafen Kulturufer",  # or the exact name in your DB
}

festival_ct = ContentType.objects.get(model="festival")

for app_id, festival_name in manual_matches.items():
    try:
        app = Application.objects.get(id=app_id)
        festival = Festival.objects.get(name__iexact=festival_name)

        app.object_id = festival.id
        app.save()

        print(f"✓ Matched App {app_id} to Festival '{festival.name}' (ID: {festival.id})")
    except Application.DoesNotExist:
        print(f"✗ Application {app_id} not found")
    except Festival.DoesNotExist:
        print(f"✗ Festival '{festival_name}' not found")
        # Show available festivals to help you find the exact name
        similar = Festival.objects.filter(name__icontains=festival_name.split()[0])
        if similar.exists():
            print("  Did you mean one of these?")
            for f in similar:
                print(f"    - {f.name} (ID: {f.id})")

print("\n✓ Manual matching completed!")
