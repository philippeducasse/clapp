# TODOS

- Add update button to editfestival page
- add filtering to festivals slice
- add redux update on festival delete (from table)

# SEARCH

● Plan: Add Organization Search Field to Manual Application Form

Overview

The goal is to replace the simple text field for "Organisation" with a searchable autocomplete/combobox that:

- Searches across ALL organization types (Festivals, Venues, Residencies)
- Displays results in a dropdown as the user types
- Allows selection of an organization
- Sets both organisation and organisationType fields in the Application

Implementation Steps

1. Create a unified organization search API endpoint/service

- Create a new API service or extend existing ones to search across all organization types
- The endpoint should:
  - Accept a search query parameter
  - Search festivals, venues, and residencies simultaneously
  - Return unified results with: id, name, type ("Festival" | "Venue" | "Residency")
- Could use parallel API calls to all three services and merge results
- Files to create/modify:
  - /src/api/organisationSearchService.ts (new file)

2. Add new form element type: AUTOCOMPLETE

- Add AUTOCOMPLETE = "AUTOCOMPLETE" to ControlledFormElementType enum
- File: /src/interfaces/forms/ControlledFormElementType.ts

3. Create ControlledAutocomplete component

- Build a new form field component using shadcn/ui Combobox or Command components
- Features:
  - Debounced search input (300-500ms delay)
  - Loading state while searching
  - Display organization name and type in dropdown
  - Handle selection to update form value
- File to create: /src/components/common/form/form-fields/ControlledAutocomplete.tsx
- Reference shadcn Combobox: https://ui.shadcn.com/docs/components/combobox

4. Update form helper to support AUTOCOMPLETE type

- Modify getControlledInputs function in /src/helpers/formHelper.tsx
- Add case for ControlledFormElementType.AUTOCOMPLETE that returns <ControlledAutocomplete />

5. Update ManualApplicationFormFields

- Replace the "Organisation" text field with AUTOCOMPLETE type
- Update /src/components/page-components/applications/helpers/form/getManualApplicationFormFields.tsx:
  {
  label: "Organisation",
  fieldName: "organisation",
  type: ControlledFormElementType.AUTOCOMPLETE,
  // Additional config for autocomplete
  }

6. Handle form submission

- When user selects an organization from autocomplete:
  - Store the organization ID in the form (or the full object)
  - Separately track the organisationType
- Options:
  - Option A: Store as nested object: { organisationId: number, organisationType: string }
  - Option B: Add a hidden field for organisationType that gets set when organization is selected
- Update form submission logic in ManualApplicationForm.tsx to properly format the data for the API

7. Update ControlledFormElement interface (if needed)

- Add properties to support autocomplete configuration:
  - searchFunction?: (query: string) => Promise<SearchResult[]>
  - onSelect?: (value: unknown) => void
- File: /src/interfaces/forms/ControlledFormElement.ts

Questions to Consider

1. How should the selected organization be stored?

   - Just the ID, or the full object?
   - Do we need a separate hidden field for organisationType?

2. Should there be a minimum character count before searching?

   - e.g., only search after user types 2+ characters

3. How should results be displayed in the dropdown?

   - Format: "Festival Name (Festival)" or "Festival Name - Festival"?

4. Should we show an indicator (badge/icon) for organization type in dropdown?
