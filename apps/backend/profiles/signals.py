import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from organisations.festivals.models import Festival, FestivalContact
from organisations.residencies.models import Residency, ResidencyContact
from organisations.venues.models import Venue, VenueContact
from .models import Profile
from .tasks import send_registration_confirmation_email

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Profile, dispatch_uid="send_confirmation_email")
def send_confirmation_email(sender, instance, created, raw, **kwargs):
    if raw:
        return  # Skip during fixture loading (loaddata)

    if created:
        send_registration_confirmation_email.delay(instance.email)


@receiver(post_save, sender=Profile, dispatch_uid="seed_user_organisations")
def seed_user_organisations(sender, instance, created, raw, **kwargs):
    """
    When a new user registers, clone all seed organisations and contacts for them.

    Seed organisations are those with user=NULL and serve as templates.
    We bulk clone them with user=instance to give each new user their own copy.

    Args:
        sender: Profile model class
        instance: The newly created Profile instance
        created: Boolean indicating if this is a new object
        raw: Boolean indicating if data is being loaded via fixtures
        **kwargs: Other signal kwargs
    """
    if not created or raw:
        return

    logger.info(f"Seeding organisations for new user {instance.email} (id={instance.id})")

    # Clone seed organisations (user=NULL) for this user
    seed_festivals = Festival.objects.filter(user__isnull=True)
    if seed_festivals.exists():
        new_festivals = [
            Festival(
                user=instance,
                name=fest.name,
                description=fest.description,
                country=fest.country,
                town=fest.town,
                website_url=fest.website_url,
                comments=fest.comments,
                tag=fest.tag,
                festival_type=fest.festival_type,
                start_date=fest.start_date,
                end_date=fest.end_date,
                approximate_date=fest.approximate_date,
                application_date_start=fest.application_date_start,
                application_date_end=fest.application_date_end,
                application_type=fest.application_type,
            )
            for fest in seed_festivals
        ]
        Festival.objects.bulk_create(new_festivals)
        logger.info(f"Created {len(new_festivals)} festivals for user {instance.id}")

    seed_venues = Venue.objects.filter(user__isnull=True)
    if seed_venues.exists():
        new_venues = [
            Venue(
                user=instance,
                name=venue.name,
                description=venue.description,
                country=venue.country,
                town=venue.town,
                website_url=venue.website_url,
                comments=venue.comments,
                tag=venue.tag,
                venue_type=venue.venue_type,
                contacted=venue.contacted,
            )
            for venue in seed_venues
        ]
        Venue.objects.bulk_create(new_venues)
        logger.info(f"Created {len(new_venues)} venues for user {instance.id}")

    seed_residencies = Residency.objects.filter(user__isnull=True)
    if seed_residencies.exists():
        new_residencies = [
            Residency(
                user=instance,
                name=res.name,
                description=res.description,
                country=res.country,
                town=res.town,
                website_url=res.website_url,
                comments=res.comments,
                tag=res.tag,
                start_date=res.start_date,
                end_date=res.end_date,
                approximate_date=res.approximate_date,
                application_date_start=res.application_date_start,
                application_date_end=res.application_date_end,
                application_type=res.application_type,
            )
            for res in seed_residencies
        ]
        Residency.objects.bulk_create(new_residencies)
        logger.info(f"Created {len(new_residencies)} residencies for user {instance.id}")

    # Clone seed contacts and remap to new organisations
    # We need to fetch the newly created orgs to map old IDs to new ones

    # Festival contacts
    seed_festival_contacts = FestivalContact.objects.filter(festival__user__isnull=True)
    if seed_festival_contacts.exists():
        # Map old festival IDs to new festival IDs
        seed_festival_map = {}
        for seed_fest in seed_festivals:
            new_fest = Festival.objects.filter(user=instance, name=seed_fest.name).first()
            if new_fest:
                seed_festival_map[seed_fest.id] = new_fest.id

        new_festival_contacts = [
            FestivalContact(
                user=instance,
                festival_id=seed_festival_map.get(contact.festival_id),
                name=contact.name,
                email=contact.email,
                role=contact.role,
                phone=contact.phone,
            )
            for contact in seed_festival_contacts
            if seed_festival_map.get(contact.festival_id)
        ]
        if new_festival_contacts:
            FestivalContact.objects.bulk_create(new_festival_contacts)
            logger.info(
                f"Created {len(new_festival_contacts)} festival contacts for user {instance.id}"
            )

    # Venue contacts
    seed_venue_contacts = VenueContact.objects.filter(venue__user__isnull=True)
    if seed_venue_contacts.exists():
        seed_venue_map = {}
        for seed_venue in seed_venues:
            new_venue = Venue.objects.filter(user=instance, name=seed_venue.name).first()
            if new_venue:
                seed_venue_map[seed_venue.id] = new_venue.id

        new_venue_contacts = [
            VenueContact(
                user=instance,
                venue_id=seed_venue_map.get(contact.venue_id),
                name=contact.name,
                email=contact.email,
                role=contact.role,
                phone=contact.phone,
            )
            for contact in seed_venue_contacts
            if seed_venue_map.get(contact.venue_id)
        ]
        if new_venue_contacts:
            VenueContact.objects.bulk_create(new_venue_contacts)
            logger.info(f"Created {len(new_venue_contacts)} venue contacts for user {instance.id}")

    # Residency contacts
    seed_residency_contacts = ResidencyContact.objects.filter(residency__user__isnull=True)
    if seed_residency_contacts.exists():
        seed_residency_map = {}
        for seed_res in seed_residencies:
            new_res = Residency.objects.filter(user=instance, name=seed_res.name).first()
            if new_res:
                seed_residency_map[seed_res.id] = new_res.id

        new_residency_contacts = [
            ResidencyContact(
                user=instance,
                residency_id=seed_residency_map.get(contact.residency_id),
                name=contact.name,
                email=contact.email,
                role=contact.role,
                phone=contact.phone,
            )
            for contact in seed_residency_contacts
            if seed_residency_map.get(contact.residency_id)
        ]
        if new_residency_contacts:
            ResidencyContact.objects.bulk_create(new_residency_contacts)
            logger.info(
                f"Created {len(new_residency_contacts)} residency contacts for user {instance.id}"
            )

    logger.info(f"Finished seeding organisations for user {instance.id}")
