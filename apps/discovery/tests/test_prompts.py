import pytest
from pydantic import ValidationError

from discovery.prompts.classify import PageClassification
from discovery.prompts.extract_leads import LeadList
from discovery.prompts.extract_org import OrgExtraction
from discovery.prompts.pick_link import LinkChoice


def test_lead_list_accepts_null_fields():
    """Models answer null for fields they don't know; that must not lose the whole page."""
    leads = LeadList.model_validate(
        {
            "leads": [
                {"name": "Fest A", "org_type": "FESTIVAL", "town": "Ghent", "country": "Belgium"},
                {
                    "name": "Fest B",
                    "org_type": "FESTIVAL",
                    "town": None,
                    "country": None,
                    "dates": None,
                    "link_number": None,
                },
            ]
        }
    )
    assert len(leads.leads) == 2
    b = leads.leads[1]
    assert (b.town, b.country, b.dates, b.link_number) == ("", "", "", None)


def test_null_lists_use_default():
    assert LeadList.model_validate({"leads": None}).leads == []
    assert LinkChoice.model_validate({"numbers": None, "reason": None}).numbers == []


def test_org_extraction_accepts_null_fields():
    org = OrgExtraction.model_validate(
        {"name": "Fest", "org_type": "VENUE", "town": None, "contacts": None, "start_date": None}
    )
    assert (org.town, org.contacts, org.start_date) == ("", [], "")


def test_classification_accepts_null_fields():
    c = PageClassification.model_validate({"kind": "ARTIST_SITE", "town": None, "org_type": None})
    assert c.town == "" and c.org_type is None


def test_required_fields_still_required():
    with pytest.raises(ValidationError):
        LeadList.model_validate({"leads": [{"name": None, "org_type": "FESTIVAL"}]})
