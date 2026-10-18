import pytest
from mistralai.extra import response_format_from_pydantic_model

from organisations.festivals.utils import FestivalEnrichment
from organisations.llm import OrganisationEnrichment
from organisations.residencies.utils import ResidencyEnrichment
from organisations.venues.utils import VenueEnrichment


def _sent_schema(model):
    """The JSON schema actually sent to Mistral's structured-output API."""
    return response_format_from_pydantic_model(model).model_dump(by_alias=True)["json_schema"][
        "schema"
    ]


@pytest.mark.parametrize(
    "model", [OrganisationEnrichment, FestivalEnrichment, ResidencyEnrichment, VenueEnrichment]
)
def test_all_enrichment_fields_are_required_in_schema(model):
    # Regression: without "required", constrained decoding let the LLM skip description.
    schema = _sent_schema(model)
    assert set(schema["required"]) == set(schema["properties"])
    assert "description" in schema["required"]


def test_required_fields_remain_nullable():
    description = _sent_schema(FestivalEnrichment)["properties"]["description"]
    assert {"type": "null"} in description["anyOf"]


def test_enrichment_can_still_be_built_partially():
    enrichment = FestivalEnrichment(description="Only this")
    assert enrichment.model_dump(exclude_none=True)["description"] == "Only this"
    assert enrichment.town is None
