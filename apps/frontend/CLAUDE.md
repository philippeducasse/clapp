# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Circus Agent Frontend (caf)** - A personal assistant application for managing careers in performance arts, built with Next.js 15, React 19, TypeScript, Redux Toolkit, and TailwindCSS.

**Development server runs on port 3020** (not the default 3000)

## Essential Commands

```bash
# Development
npm run dev          # Start dev server (Turbopack, port 3020)

# Build & Deploy
npm run build        # Production build
npm start           # Start production server

# Code Quality
npm run lint        # Run ESLint
npm run type        # TypeScript type checking (npx tsc --noEmit)
```

## Architecture Overview

### Directory Structure

```
src/
├── app/                    # Next.js 15 App Router
│   ├── (main)/            # Authenticated pages (with sidebar/navbar)
│   ├── (auth)/            # Login/register pages
│   └── layout.tsx         # Root layout
├── components/
│   ├── common/            # Reusable components (form, table, details-view, etc.)
│   ├── page-components/   # Entity-specific components (festivals, venues, residencies, etc.)
│   └── ui/                # shadcn/ui components
├── redux/
│   ├── slices/            # Entity slices (festival, venue, residency, application, auth)
│   ├── shared/            # Shared reducers (filter reducers)
│   └── store.ts
├── api/                   # API service layer
│   ├── fetchHelper.ts     # Core HTTP utilities with auto-serialization
│   └── *ApiService.ts     # Entity-specific API services
├── interfaces/
│   ├── entities/          # Entity type definitions
│   ├── forms/             # Form interfaces
│   └── api/               # API interfaces
├── helpers/               # Utilities
│   ├── formHelper.tsx     # Auto-generates Zod schemas from form configs
│   └── serializer.ts      # camelCase ↔ snake_case conversion
└── middleware.ts          # Auth middleware
```

### Core Architectural Patterns

#### 1. Route Groups

- `(main)` - Authenticated pages with full layout (sidebar + navbar)
- `(auth)` - Login/register with minimal layout

#### 2. Entity CRUD Pattern

All main entities (festivals, venues, residencies, applications) follow the same pattern:

**Routes:**

- `/{entity}` - Table listing
- `/{entity}/[id]` - Detail view
- `/{entity}/[id]/edit` - Edit form
- `/{entity}/create` - Multi-step creation (step1 → step2)

**Components Pattern:**

```
page-components/{entity}/
├── components/
│   ├── form/          # Form components
│   ├── table/         # Table columns & filters
│   ├── details/       # Detail view sections
│   └── update/        # Update/diff components
└── helpers/
    ├── form/          # Form field configurations
    ├── get{Entity}Details.ts
    ├── refresh{Entity}.ts
    └── use{Entity}Columns.tsx
```

#### 3. API Layer

**Backend Integration:**

- Backend URL: `NEXT_PUBLIC_BACKEND_URL` (default: http://localhost:8000)
- All API calls through `fetchHelper.ts`
- **Automatic serialization:** Frontend uses camelCase, backend uses snake_case
- CSRF token handling built-in
- Toast notifications on success/error

**Standard API Service Pattern:**

```typescript
interface EntityApiService<T> {
  getAll: () => Promise<PaginatedResponse<T>>;
  get: (id: number) => Promise<T>;
  create: (entity: T) => Promise<T>;
  update: (entity: T) => Promise<T>;
  remove: (id: number) => Promise<void>;
  tag: (entityId: number, action: TagAction) => Promise<T>;
  enrich: (id: number) => Promise<T>;
}
```

#### 4. Redux State Management

**Store Structure:**

```typescript
{
  festivals: { entities: Festival[], filters: {...} },
  residencies: { entities: Residency[], filters: {...} },
  venues: { entities: Venue[], filters: {...} },
  applications: { entities: Application[], filters: {...} },
  profile: AuthState
}
```

**Usage:**

```typescript
const dispatch = useAppDispatch();
const festival = useSelector((state: RootState) => selectFestival(state, id));

// Refresh pattern (fetch and update Redux)
refreshFestival(festivalId, dispatch);
```

#### 5. Form System

**Stack:** react-hook-form + zod + @hookform/resolvers

**Declarative Form Configuration:**
Forms are defined via `ControlledFormElement[]` arrays that specify field types, validation, visibility per action (CREATE/EDIT/APPLY), etc.

**Auto-generated Validation:**
`createZodFormSchema(formFields)` automatically generates Zod schemas from field configs.

**Form Helpers (formHelper.tsx):**

- `createZodFormSchema()` - Generate Zod schema
- `sanitizeFormData()` - Prepare backend data for form
- `prepareFormDataForSubmission()` - Prepare form data for backend
- `getControlledInputs()` - Render appropriate input component
- `getInitialValues()` - Generate initial form values

**Multi-Step Form Pattern:**

1. Step 1 (basic info) → Stores temp entity in Redux with `id: -1`
2. Step 2 (contact info) → Creates final entity via API

**Form Persistence:**
`useFormPersist(formTitle, form, shouldPersist)` auto-saves to localStorage for CREATE actions.

#### 6. Table Pattern

**TanStack React Table** with:

- Server-side or client-side pagination
- Column filtering & global search
- Sortable headers
- Fixed table layout with column sizing

**Usage:**

```typescript
const columns = useEntityColumns(); // Custom hook per entity
<DataTable
  columns={columns}
  data={entities}
  entityName={EntityName.ENTITY}
  filters={getEntityFilters()}
/>;
```

#### 7. Details View Pattern

```typescript
<DetailsViewWrapper href="/entities">
  <DetailsViewHeader title={entity.name} ... />
  <DetailsViewSection
    title="Basic information"
    data={getEntityBasicInfo(entity)} // Array of SectionCellProps
  />
  <ContactsViewSection contacts={entity.contacts} />
</DetailsViewWrapper>
```

Each entity has helper functions converting entity data to `SectionCellProps[]` for display.

## Key Conventions

### Naming

- **Frontend:** camelCase for all data
- **Backend:** snake_case (auto-converted by API layer)
- **Components:** PascalCase files
- **Hooks:** camelCase with "use" prefix
- **Helpers:** camelCase
- **Routes:** kebab-case segments

### Path Aliasing

`@/*` maps to `./src/*` (configured in tsconfig.json)

### Client vs Server Components

- Server components by default (Next.js 15)
- Mark with `"use client"` only when needed (hooks, state, event handlers)
- Pages typically fetch initial data server-side, pass to client components

### Data Fetching Pattern

```typescript
// In client components
useEffect(() => {
  if (!entity && entityId) {
    refreshEntity(entityId, dispatch); // Fetch & update Redux
  }
}, [entityId, entity, dispatch]);
```

### Enums

Extensive use of enums for type safety:

- `Action` - CREATE, EDIT, APPLY, LOGIN, REGISTER
- `EntityName` - FESTIVAL, VENUE, RESIDENCY, etc.
- `TagAction` - STAR, WATCH, INACTIVE, etc.

### Authentication

- Middleware checks `sessionid` cookie
- Redirects unauthenticated users to `/login`
- Profile data stored in Redux (`profile` slice)
- `ProfileHydrator` component hydrates profile on mount

## Styling

- **TailwindCSS 4** - Utility-first CSS
- **shadcn/ui** - Component library (Radix UI primitives)
- **next-themes** - Dark mode support
- **Primary color:** Defined in globals.css as CSS variables (primary, primary-foreground)

## Important Notes

- **Never use default port 3000** - This project runs on port 3020
- **Always use `@/` path alias** for imports from src/
- **Follow entity patterns** - When adding new entities, mirror the festival/venue/residency pattern
- **Serialization is automatic** - Don't manually convert camelCase ↔ snake_case; fetchHelper handles it
- **Form validation is declarative** - Define field config, Zod schema is auto-generated
- **Type safety first** - Use existing interfaces and enums, avoid `any`
- **Multi-step forms** - Create flows store temp entity with `id: -1` in Redux before final API call
