# Performance Improvements TODO

Generated from codebase analysis on 2026-03-25

## 🔴 Critical Issues

### 1. Remove Redux Store Console Logging
- **File**: `src/redux/store.ts` (lines 9-11)
- **Issue**: Store subscription logs entire state on every update
- **Impact**: Console spam, memory overhead in dev and production
- **Fix**: Remove the console.log subscription, use Redux DevTools instead
- **Effort**: 1 minute
- [ ] Remove console.log subscription
- [ ] Test Redux state updates don't log to console
- [ ] Verify Redux DevTools still works in dev

### 2. Debounce Form Persistence
- **File**: `src/hooks/useFormPersist.ts`
- **Issue**: `form.watch()` triggers localStorage write on every keystroke
- **Impact**: Excessive localStorage writes, potential jank on large forms
- **Fix**: Add 300-500ms debounce before localStorage.setItem()
- **Effort**: 5 minutes
- [ ] Add debounce utility (lodash or custom)
- [ ] Wrap localStorage write in debounce
- [ ] Test form still saves on unmount
- [ ] Verify no jank on rapid typing

## 🟠 High Priority

### 3. Implement API Response Caching
- **File**: `src/api/fetchHelper.ts`
- **Issue**: No caching strategy - every navigation/filter triggers fresh API calls
- **Impact**: Redundant network requests, slower navigation, poor UX
- **Fix**: Implement response caching or request deduplication layer
- **Effort**: 30 minutes
- [ ] Design cache key strategy (URL + params)
- [ ] Implement cache store (in-memory or sessionStorage)
- [ ] Add cache invalidation logic
- [ ] Test cache works across navigation
- [ ] Consider cache expiration time (5-10 min recommended)

### 4. Debounce Table Search/Filter Input
- **File**: `src/components/common/table/DataTable.tsx` (lines 74-92)
- **Issue**: API calls fire on every keystroke in search/filter inputs
- **Impact**: Excessive API calls, server load, poor performance
- **Fix**: Add 300-500ms debounce to search input handler
- **Effort**: 10 minutes
- [ ] Import debounce utility
- [ ] Wrap filter/search handlers in debounce
- [ ] Test with rapid typing
- [ ] Ensure user can still clear search quickly

### 5. Memoize Zod Schema Generation
- **File**: `src/helpers/formHelper.tsx` (line 147)
- **Issue**: `createZodFormSchema()` called on every render without memoization
- **Impact**: Repeated schema validation compilation, slower form renders
- **Fix**: Memoize schema generation using useMemo or move outside component
- **Effort**: 10 minutes
- [ ] Create memoized version of createZodFormSchema
- [ ] Test schema caching works across re-renders
- [ ] Verify form validation still accurate

## 🟡 Medium Priority

### 6. Implement Virtual Scrolling for Tables
- **File**: `src/components/common/table/DataTable.tsx`
- **Issue**: All rows rendered in DOM (currently 25/page, manageable but inefficient)
- **Impact**: Will struggle with larger datasets or increased page sizes
- **Fix**: Implement virtual scrolling for table rows
- **Effort**: 45 minutes
- [ ] Evaluate virtualization library (react-window, tanstack/react-virtual)
- [ ] Integrate with existing TanStack React Table
- [ ] Test with current page size
- [ ] Ensure column sizing still works
- [ ] Performance test with 500+ rows

### 7. Add Memoization to Components
- **Files**: Multiple component files (only 13/100+ currently use memoization)
- **Issue**: Missing React.memo, useMemo, useCallback in many components
- **Impact**: Unnecessary re-renders throughout the app
- **Priority targets**:
  - Table column definitions (`use{Entity}Columns.tsx` files)
  - Table row callbacks (onDeleteClick, onEditClick)
  - Form field components
  - Details view sections
- **Effort**: 60+ minutes (do gradually)
- [ ] Wrap table column callbacks with useCallback
- [ ] Add React.memo to frequently-rendered list items
- [ ] Memoize filter objects in table components
- [ ] Use useCallback for event handlers in forms

### 8. Replace Full Lodash Import
- **File**: `src/utils/stringUtils.ts`
- **Issue**: Imports entire lodash library (~24KB gzipped) for 4 functions
- **Functions used**: camelCase, snakeCase, capitalize, lowerCase
- **Impact**: Unnecessary bundle size increase
- **Fix**: Replace with native JS or smaller alternative
- **Effort**: 15 minutes
- [ ] Create native implementations of camelCase and snakeCase
- [ ] Replace all lodash function calls
- [ ] Remove lodash import
- [ ] Verify serialization still works
- [ ] Check bundle size reduction

## 🔵 Low Priority

### 9. Sanitize dangerouslySetInnerHTML Usage
- **Files**:
  - `src/components/common/form/BasicForm.tsx` (line 70)
  - `src/components/common/details-view/Row.tsx` (line 70)
- **Issue**: Renders HTML without validation/sanitization
- **Risk**: XSS vulnerability if content from user input
- **Fix**: Validate/sanitize HTML or use JSON-safe rendering
- **Effort**: 20 minutes
- [ ] Audit where HTML content comes from
- [ ] Add sanitization library if needed (DOMPurify)
- [ ] Replace dangerouslySetInnerHTML or validate content
- [ ] Add security tests

### 10. Add Selector Memoization Library
- **File**: Redux slices in `src/redux/slices/`
- **Issue**: Redux selectors not using `reselect` for computed selectors
- **Impact**: Minor performance impact, selectors recompute on every call
- **Fix**: Implement `reselect` for complex selectors
- **Effort**: 20 minutes
- [ ] Add reselect library
- [ ] Identify computed selectors (filters, derived values)
- [ ] Convert to memoized selectors
- [ ] Test selector performance

### 11. Fix Missing Error Handling in Refresh Functions
- **File**: `src/components/page-components/{entity}/helpers/refresh{Entity}.ts` (all entities)
- **Issue**: No error handling for failed fetches
- **Impact**: Silent failures, poor user experience
- **Fix**: Add try/catch and user notification
- **Effort**: 15 minutes per entity × 4 = 60 minutes total
- [ ] Add error handling to refreshFestival
- [ ] Add error handling to refreshVenue
- [ ] Add error handling to refreshResidency
- [ ] Add error handling to refreshApplication
- [ ] Consider global error toast pattern

### 12. Reduce useEffect Hook Redundancy
- **Files**: Detail view and form components
- **Issue**: Many components independently call refresh functions in useEffect
- **Impact**: Duplicate fetches, complex dependency arrays
- **Fix**: Centralize data fetching logic or use React Query pattern
- **Effort**: 90+ minutes (refactor effort)
- [ ] Audit useEffect patterns in detail views
- [ ] Consider custom hook for data fetching
- [ ] Combine redundant fetches
- [ ] Simplify dependency arrays

---

## Performance Wins Summary

| Issue | Severity | Effort | Est. Impact |
|-------|----------|--------|-------------|
| Remove console logging | Critical | 1 min | High |
| Debounce form persistence | Critical | 5 min | High |
| API response caching | High | 30 min | Very High |
| Debounce search input | High | 10 min | High |
| Memoize Zod schema | High | 10 min | Medium |
| Virtual scrolling | Medium | 45 min | Medium |
| Add memoization | Medium | 60+ min | Medium |
| Replace lodash | Medium | 15 min | Low (bundle) |
| Sanitize HTML | Low | 20 min | Security |
| Reselect memoization | Low | 20 min | Low |
| Error handling | Low | 60 min | UX |
| Reduce useEffect | Low | 90 min | High (refactor) |

---

## Quick Wins (Start Here)
1. Remove Redux console logging (1 min)
2. Debounce form persistence (5 min)
3. Debounce table search (10 min)
4. Replace lodash (15 min)
5. Memoize Zod schema (10 min)

**Total time for quick wins: ~40 minutes**

---

## Implementation Strategy

1. **Phase 1** (Critical): Items 1-2 (6 minutes)
2. **Phase 2** (High Priority): Items 3-5 (50 minutes)
3. **Phase 3** (Medium): Items 6-8 (120+ minutes)
4. **Phase 4** (Low/As Needed): Items 9-12 (165+ minutes)

Recommend starting with Phase 1 & 2 for maximum impact per time invested.