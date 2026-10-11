import { describe, it, expect } from "vitest";
import { configureStore } from "@reduxjs/toolkit";

// Auth Slice Tests
import authReducer, {
  setProfile,
  updateProfile,
  addPerformance,
  updatePerformance,
  selectProfile,
  fetchProfile,
} from "@/redux/slices/authSlice";
import { Profile } from "@/interfaces/entities/Profile";
import { Performance, PerformanceGenre, PerformanceType } from "@/interfaces/entities/Performance";

// Festival Slice Tests
import festivalReducer, {
  setFestivals,
  setFestival,
  addFestival,
  updateFestival,
  deleteFestival,
  setColumnFilters,
  setColumnFilter,
  removeColumnFilter,
  clearColumnFilters,
  setSearchBarFilter,
  initializeColumnFilters,
} from "@/redux/slices/festivalSlice";
import { Festival, FestivalType } from "@/interfaces/entities/Festival";

// Residency Slice Tests
import residencyReducer, {
  setResidencies,
  setResidency,
  addResidency,
  updateResidency,
  deleteResidency,
  setColumnFilter as setResidencyColumnFilter,
} from "@/redux/slices/residencySlice";
import { Residency } from "@/interfaces/entities/Residency";

// Venue Slice Tests
import venueReducer, {
  setVenues,
  setVenue,
  addVenue,
  updateVenue,
  deleteVenue,
  setColumnFilter as setVenueColumnFilter,
} from "@/redux/slices/venueSlice";
import { Venue, VenueType } from "@/interfaces/entities/Venue";

// Application Slice Tests
import applicationReducer, {
  setApplications,
  setApplication,
  addApplication,
  updateApplication,
  deleteApplication,
  clearColumnFilters as clearApplicationColumnFilters,
} from "@/redux/slices/applicationSlice";
import reminderReducer from "@/redux/slices/reminderSlice";
import { Application, ApplicationMethod, ApplicationStatus } from "@/interfaces/entities/Application";

describe("Redux Slices", () => {
  describe("Auth Slice", () => {
    it("should have initial state", () => {
      const state = authReducer(undefined, { type: "unknown" });
      expect(state.profile).toBeNull();
    });

    it("should set profile", () => {
      const mockProfile: Profile = {
        id: 1,
        email: "test@example.com",
        firstName: "John",
        lastName: "Doe",
        confirmedAccount: true,
        performances: [],
      };

      const state = authReducer(
        { profile: null },
        setProfile(mockProfile),
      );

      expect(state.profile).toEqual(mockProfile);
      expect(state.profile?.email).toBe("test@example.com");
    });

    it("should update profile", () => {
      const initialProfile: Profile = {
        id: 1,
        email: "test@example.com",
        firstName: "John",
        lastName: "Doe",
        confirmedAccount: true,
        performances: [],
      };

      const updates: Partial<Profile> = {
        firstName: "Jane",
        confirmedAccount: false,
      };

      const state = authReducer(
        { profile: initialProfile },
        updateProfile(updates as Profile),
      );

      expect(state.profile?.firstName).toBe("Jane");
      expect(state.profile?.confirmedAccount).toBe(false);
      expect(state.profile?.email).toBe("test@example.com"); // unchanged
    });

    it("should add performance to profile", () => {
      const initialProfile: Profile = {
        id: 1,
        email: "test@example.com",
        firstName: "John",
        lastName: "Doe",
        confirmedAccount: true,
        performances: [],
      };

      const mockPerformance: Performance = {
        id: 1,
        profile: 1,
        performanceTitle: "Juggling Act",
        genres: [PerformanceGenre.CIRCUS],
        performanceType: PerformanceType.STREET,
        shortDescription: "Amazing juggling performance",
      };

      const state = authReducer(
        { profile: initialProfile },
        addPerformance(mockPerformance),
      );

      expect(state.profile?.performances).toHaveLength(1);
      expect(state.profile?.performances[0].id).toBe(1);
      expect(state.profile?.performances[0].performanceTitle).toBe("Juggling Act");
    });

    it("should update performance in profile", () => {
      const mockPerformance: Performance = {
        id: 1,
        profile: 1,
        performanceTitle: "Juggling Act",
        genres: [PerformanceGenre.CIRCUS],
        performanceType: PerformanceType.STREET,
        shortDescription: "Original description",
      };

      const initialProfile: Profile = {
        id: 1,
        email: "test@example.com",
        firstName: "John",
        lastName: "Doe",
        confirmedAccount: true,
        performances: [mockPerformance],
      };

      const updatedPerformance: Performance = {
        id: 1,
        profile: 1,
        performanceTitle: "Advanced Juggling",
        genres: [PerformanceGenre.CIRCUS],
        performanceType: PerformanceType.INDOOR_STAGE,
        shortDescription: "Updated description",
      };

      const state = authReducer(
        { profile: initialProfile },
        updatePerformance(updatedPerformance),
      );

      expect(state.profile?.performances[0].performanceTitle).toBe("Advanced Juggling");
      expect(state.profile?.performances[0].shortDescription).toBe("Updated description");
    });

    it("should not update profile if profile is null", () => {
      const state = authReducer(
        { profile: null },
        addPerformance({
          id: 1,
          profile: 1,
          performanceTitle: "Performance",
          genres: [PerformanceGenre.CIRCUS],
          performanceType: PerformanceType.STREET,
        }),
      );

      expect(state.profile).toBeNull();
    });

    it("should select profile from state", () => {
      const mockProfile: Profile = {
        id: 1,
        email: "test@example.com",
        firstName: "John",
        lastName: "Doe",
        confirmedAccount: true,
        performances: [],
      };

      const store = configureStore({
        reducer: {
          profile: authReducer,
          festivals: festivalReducer,
          residencies: residencyReducer,
          venues: venueReducer,
          applications: applicationReducer,
          reminders: reminderReducer,
        },
        preloadedState: {
          profile: { profile: mockProfile },
          festivals: { festivals: [], filters: [], searchBarFilter: "", filtersInitialized: false, loading: false, error: null },
          residencies: { residencies: [], filters: [], searchBarFilter: "", filtersInitialized: false, loading: false, error: null },
          venues: { venues: [], filters: [], searchBarFilter: "", filtersInitialized: false, loading: false, error: null },
          applications: { applications: [], filters: [], searchBarFilter: "", filtersInitialized: false, loading: false, error: null },
          reminders: { unreadCount: 0 },
        },
      });

      const selected = selectProfile(store.getState());
      expect(selected).toEqual(mockProfile);
    });
  });

  describe("Festival Slice", () => {
    const initialState = {
      festivals: [],
      filters: [],
      searchBarFilter: "",
      filtersInitialized: false,
      loading: false,
      error: null,
    };

    it("should have initial state", () => {
      const state = festivalReducer(undefined, { type: "unknown" });
      expect(state.festivals).toEqual([]);
      expect(state.filters).toEqual([]);
      expect(state.searchBarFilter).toBe("");
    });

    it("should set festivals", () => {
      const mockFestivals: Festival[] = [
        {
          id: 1,
          name: "Jazz Fest",
          country: "France",
          festivalType: FestivalType.MUSIC,
        },
        {
          id: 2,
          name: "Circus Fest",
          country: "Germany",
          festivalType: FestivalType.CIRCUS,
        },
      ];

      const state = festivalReducer(initialState, setFestivals(mockFestivals));

      expect(state.festivals).toHaveLength(2);
      expect(state.festivals[0].name).toBe("Jazz Fest");
    });

    it("should set single festival (add or update)", () => {
      const mockFestival: Festival = {
        id: 1,
        name: "Jazz Fest",
        country: "France",
        festivalType: FestivalType.MUSIC,
      };

      const state = festivalReducer(initialState, setFestival(mockFestival));

      expect(state.festivals).toHaveLength(1);
      expect(state.festivals[0].id).toBe(1);
    });

    it("should update existing festival via setFestival", () => {
      const initialFestivals: Festival[] = [
        {
          id: 1,
          name: "Jazz Fest",
          country: "France",
          festivalType: FestivalType.MUSIC,
        },
      ];

      const updated: Festival = {
        id: 1,
        name: "Updated Jazz Fest",
        country: "France",
        festivalType: FestivalType.MUSIC,
      };

      const state = festivalReducer(
        { ...initialState, festivals: initialFestivals },
        setFestival(updated),
      );

      expect(state.festivals).toHaveLength(1);
      expect(state.festivals[0].name).toBe("Updated Jazz Fest");
    });

    it("should add festival", () => {
      const mockFestival: Festival = {
        id: 1,
        name: "Jazz Fest",
        country: "France",
        festivalType: FestivalType.MUSIC,
      };

      const state = festivalReducer(initialState, addFestival(mockFestival));

      expect(state.festivals).toHaveLength(1);
      expect(state.festivals[0].id).toBe(1);
    });

    it("should update festival", () => {
      const initialFestivals: Festival[] = [
        {
          id: 1,
          name: "Jazz Fest",
          country: "France",
          festivalType: FestivalType.MUSIC,
        },
      ];

      const updated: Festival = {
        id: 1,
        name: "Updated Jazz Fest",
        country: "Spain",
        festivalType: FestivalType.MUSIC,
      };

      const state = festivalReducer(
        { ...initialState, festivals: initialFestivals },
        updateFestival(updated),
      );

      expect(state.festivals[0].name).toBe("Updated Jazz Fest");
      expect(state.festivals[0].country).toBe("Spain");
    });

    it("should delete festival", () => {
      const initialFestivals: Festival[] = [
        { id: 1, name: "Jazz Fest", festivalType: FestivalType.MUSIC },
        { id: 2, name: "Circus Fest", festivalType: FestivalType.CIRCUS },
      ];

      const state = festivalReducer(
        { ...initialState, festivals: initialFestivals },
        deleteFestival(1),
      );

      expect(state.festivals).toHaveLength(1);
      expect(state.festivals[0].id).toBe(2);
    });

    it("should set column filters", () => {
      const filters = [
        { id: "type", column: "type", value: "MUSIC" },
        { id: "country", column: "country", value: "France" },
      ];

      const state = festivalReducer(initialState, setColumnFilters(filters));

      expect(state.filters).toHaveLength(2);
      expect(state.filters[0].value).toBe("MUSIC");
    });

    it("should add/update single column filter", () => {
      const filter = { id: "type", column: "type", value: "MUSIC" };

      const state = festivalReducer(initialState, setColumnFilter(filter));

      expect(state.filters).toHaveLength(1);
      expect(state.filters[0].id).toBe("type");
    });

    it("should remove column filter", () => {
      const filters = [
        { id: "type", column: "type", value: "MUSIC" },
        { id: "country", column: "country", value: "France" },
      ];

      const state = festivalReducer(
        { ...initialState, filters },
        removeColumnFilter("type"),
      );

      expect(state.filters).toHaveLength(1);
      expect(state.filters[0].id).toBe("country");
    });

    it("should clear all column filters", () => {
      const filters = [
        { id: "type", column: "type", value: "MUSIC" },
        { id: "country", column: "country", value: "France" },
      ];

      const state = festivalReducer(
        { ...initialState, filters },
        clearColumnFilters(),
      );

      expect(state.filters).toHaveLength(0);
    });

    it("should set search bar filter", () => {
      const state = festivalReducer(initialState, setSearchBarFilter("jazz"));

      expect(state.searchBarFilter).toBe("jazz");
    });

    describe("filtersInitialized", () => {
      const typeFilter = { id: "type", value: "MUSIC" };

      it("is false initially", () => {
        expect(festivalReducer(undefined, { type: "unknown" }).filtersInitialized).toBe(false);
      });

      it("initializeColumnFilters sets filters when not initialized", () => {
        const state = festivalReducer(initialState, initializeColumnFilters([typeFilter]));
        expect(state.filters).toEqual([typeFilter]);
        expect(state.filtersInitialized).toBe(true);
      });

      it("initializeColumnFilters is a no-op once initialized", () => {
        const state = festivalReducer(
          { ...initialState, filtersInitialized: true },
          initializeColumnFilters([typeFilter]),
        );
        expect(state.filters).toEqual([]);
      });

      it.each([
        ["setColumnFilters", setColumnFilters([typeFilter])],
        ["setColumnFilter", setColumnFilter(typeFilter)],
        ["removeColumnFilter", removeColumnFilter("type")],
        ["clearColumnFilters", clearColumnFilters()],
      ])("%s marks filters as initialized", (_, action) => {
        expect(festivalReducer(initialState, action).filtersInitialized).toBe(true);
      });
    });
  });

  describe("Residency Slice", () => {
    const initialState = {
      residencies: [],
      filters: [],
      searchBarFilter: "",
      filtersInitialized: false,
      loading: false,
      error: null,
    };

    it("should have initial state", () => {
      const state = residencyReducer(undefined, { type: "unknown" });
      expect(state.residencies).toEqual([]);
    });

    it("should set residencies", () => {
      const mockResidencies: Residency[] = [
        {
          id: 1,
          name: "Artist Residency",
          country: "France",
          town: "Paris",
        },
        {
          id: 2,
          name: "Creative Hub",
          country: "Germany",
          town: "Berlin",
        },
      ];

      const state = residencyReducer(initialState, setResidencies(mockResidencies));

      expect(state.residencies).toHaveLength(2);
    });

    it("should set single residency", () => {
      const mockResidency: Residency = {
        id: 1,
        name: "Artist Residency",
        country: "France",
        town: "Paris",
      };

      const state = residencyReducer(initialState, setResidency(mockResidency));

      expect(state.residencies).toHaveLength(1);
      expect(state.residencies[0].id).toBe(1);
    });

    it("should add residency", () => {
      const mockResidency: Residency = {
        id: 1,
        name: "Artist Residency",
        country: "France",
        town: "Paris",
      };

      const state = residencyReducer(initialState, addResidency(mockResidency));

      expect(state.residencies).toHaveLength(1);
    });

    it("should update residency", () => {
      const initialResidencies: Residency[] = [
        {
          id: 1,
          name: "Artist Residency",
          country: "France",
          town: "Paris",
        },
      ];

      const updated: Residency = {
        id: 1,
        name: "Updated Residency",
        country: "Spain",
        town: "Barcelona",
      };

      const state = residencyReducer(
        { ...initialState, residencies: initialResidencies },
        updateResidency(updated),
      );

      expect(state.residencies[0].name).toBe("Updated Residency");
      expect(state.residencies[0].country).toBe("Spain");
    });

    it("should delete residency", () => {
      const initialResidencies: Residency[] = [
        { id: 1, name: "Residency 1", country: "France" },
        { id: 2, name: "Residency 2", country: "Germany" },
      ];

      const state = residencyReducer(
        { ...initialState, residencies: initialResidencies },
        deleteResidency(1),
      );

      expect(state.residencies).toHaveLength(1);
      expect(state.residencies[0].id).toBe(2);
    });
  });

  describe("Venue Slice", () => {
    const initialState = {
      venues: [],
      filters: [],
      searchBarFilter: "",
      filtersInitialized: false,
      loading: false,
      error: null,
    };

    it("should have initial state", () => {
      const state = venueReducer(undefined, { type: "unknown" });
      expect(state.venues).toEqual([]);
    });

    it("should set venues", () => {
      const mockVenues: Venue[] = [
        {
          id: 1,
          name: "Theatre Central",
          country: "France",
          town: "Paris",
          venueType: VenueType.THEATRE,
        },
        {
          id: 2,
          name: "Concert Hall",
          country: "Germany",
          town: "Berlin",
          venueType: VenueType.CONCERT_HALL,
        },
      ];

      const state = venueReducer(initialState, setVenues(mockVenues));

      expect(state.venues).toHaveLength(2);
    });

    it("should set single venue", () => {
      const mockVenue: Venue = {
        id: 1,
        name: "Theatre Central",
        country: "France",
        town: "Paris",
        venueType: "THEATRE",
      };

      const state = venueReducer(initialState, setVenue(mockVenue));

      expect(state.venues).toHaveLength(1);
      expect(state.venues[0].id).toBe(1);
    });

    it("should add venue", () => {
      const mockVenue: Venue = {
        id: 1,
        name: "Theatre Central",
        country: "France",
        town: "Paris",
        venueType: "THEATRE",
      };

      const state = venueReducer(initialState, addVenue(mockVenue));

      expect(state.venues).toHaveLength(1);
    });

    it("should update venue", () => {
      const initialVenues: Venue[] = [
        {
          id: 1,
          name: "Theatre Central",
          country: "France",
          town: "Paris",
          venueType: VenueType.THEATRE,
        },
      ];

      const updated: Venue = {
        id: 1,
        name: "Updated Theatre",
        country: "Spain",
        town: "Barcelona",
        venueType: "THEATRE",
      };

      const state = venueReducer(
        { ...initialState, venues: initialVenues },
        updateVenue(updated),
      );

      expect(state.venues[0].name).toBe("Updated Theatre");
      expect(state.venues[0].country).toBe("Spain");
    });

    it("should delete venue", () => {
      const initialVenues: Venue[] = [
        { id: 1, name: "Venue 1", country: "France", venueType: "THEATRE" },
        { id: 2, name: "Venue 2", country: "Germany", venueType: "CONCERT_HALL" },
      ];

      const state = venueReducer(
        { ...initialState, venues: initialVenues },
        deleteVenue(1),
      );

      expect(state.venues).toHaveLength(1);
      expect(state.venues[0].id).toBe(2);
    });
  });

  describe("Application Slice", () => {
    const initialState = {
      applications: [],
      filters: [],
      searchBarFilter: "",
      filtersInitialized: false,
      loading: false,
      error: null,
    };

    it("should have initial state", () => {
      const state = applicationReducer(undefined, { type: "unknown" });
      expect(state.applications).toEqual([]);
    });

    describe("default season filter", () => {
      const baseProfile: Profile = {
        id: 1,
        email: "test@example.com",
        firstName: "John",
        lastName: "Doe",
        confirmedAccount: true,
        performances: [],
      };

      it("filters on the default season when the profile is set", () => {
        const state = applicationReducer(
          initialState,
          setProfile({
            ...baseProfile,
            applicationSeasons: [
              { id: 1, name: "2025", isDefault: false },
              { id: 2, name: "2026", isDefault: true },
            ],
          }),
        );
        expect(state.filters).toEqual([{ id: "season", value: "2026" }]);
      });

      it("filters on the default season when the profile is fetched", () => {
        const state = applicationReducer(
          initialState,
          fetchProfile.fulfilled(
            { ...baseProfile, applicationSeasons: [{ id: 2, name: "2026", isDefault: true }] },
            "requestId",
          ),
        );
        expect(state.filters).toEqual([{ id: "season", value: "2026" }]);
      });

      it("does not override filters that are already initialized", () => {
        const state = applicationReducer(
          {
            ...initialState,
            filters: [{ id: "status", value: "APPLIED" }],
            filtersInitialized: true,
          },
          setProfile({
            ...baseProfile,
            applicationSeasons: [{ id: 2, name: "2026", isDefault: true }],
          }),
        );
        expect(state.filters).toEqual([{ id: "status", value: "APPLIED" }]);
      });

      it("does not re-apply the default after the user cleared filters", () => {
        const profile = {
          ...baseProfile,
          applicationSeasons: [{ id: 2, name: "2026", isDefault: true }],
        };
        let state = applicationReducer(initialState, setProfile(profile));
        state = applicationReducer(state, clearApplicationColumnFilters());
        state = applicationReducer(state, setProfile(profile));
        expect(state.filters).toEqual([]);
      });

      it("applies no filter when there is no default season", () => {
        const state = applicationReducer(
          initialState,
          setProfile({
            ...baseProfile,
            applicationSeasons: [{ id: 1, name: "2025", isDefault: false }],
          }),
        );
        expect(state.filters).toEqual([]);
      });

      it("applies no filter when the profile has no seasons", () => {
        const state = applicationReducer(initialState, setProfile(baseProfile));
        expect(state.filters).toEqual([]);
      });
    });

    it("should set applications", () => {
      const mockApplications: Application[] = [
        {
          id: 1,
          organisation: { id: 1, name: "Festival 1" },
          organisationType: "Festival",
          profile: 1,
          applicationDate: "2025-01-15",
          applicationMethod: ApplicationMethod.EMAIL,
          status: ApplicationStatus.APPLIED,
          createdAt: "2025-01-15T10:00:00",
        },
        {
          id: 2,
          organisation: { id: 2, name: "Venue 1" },
          organisationType: "Venue",
          profile: 1,
          applicationDate: "2025-01-16",
          applicationMethod: ApplicationMethod.FORM,
          status: ApplicationStatus.DRAFT,
          createdAt: "2025-01-16T10:00:00",
        },
      ];

      const state = applicationReducer(initialState, setApplications(mockApplications));

      expect(state.applications).toHaveLength(2);
    });

    it("should set single application", () => {
      const mockApplication: Application = {
        id: 1,
        organisation: { id: 1, name: "Festival 1" },
        organisationType: "Festival",
        profile: 1,
        applicationDate: "2025-01-15",
        applicationMethod: ApplicationMethod.EMAIL,
        status: ApplicationStatus.APPLIED,
        createdAt: "2025-01-15T10:00:00",
      };

      const state = applicationReducer(initialState, setApplication(mockApplication));

      expect(state.applications).toHaveLength(1);
      expect(state.applications[0].id).toBe(1);
    });

    it("should add application", () => {
      const mockApplication: Application = {
        id: 1,
        organisation: { id: 1, name: "Festival 1" },
        organisationType: "Festival",
        profile: 1,
        applicationDate: "2025-01-15",
        applicationMethod: ApplicationMethod.EMAIL,
        status: ApplicationStatus.DRAFT,
        createdAt: "2025-01-15T10:00:00",
      };

      const state = applicationReducer(initialState, addApplication(mockApplication));

      expect(state.applications).toHaveLength(1);
    });

    it("should update application", () => {
      const initialApplications: Application[] = [
        {
          id: 1,
          organisation: { id: 1, name: "Festival 1" },
          organisationType: "Festival",
          profile: 1,
          applicationDate: "2025-01-15",
          applicationMethod: ApplicationMethod.EMAIL,
          status: ApplicationStatus.DRAFT,
          createdAt: "2025-01-15T10:00:00",
        },
      ];

      const updated: Application = {
        id: 1,
        organisation: { id: 1, name: "Festival 1" },
        organisationType: "Festival",
        profile: 1,
        applicationDate: "2025-01-15",
        applicationMethod: ApplicationMethod.EMAIL,
        status: ApplicationStatus.APPLIED,
        message: "Updated message",
        createdAt: "2025-01-15T10:00:00",
      };

      const state = applicationReducer(
        { ...initialState, applications: initialApplications },
        updateApplication(updated),
      );

      expect(state.applications[0].status).toBe(ApplicationStatus.APPLIED);
      expect(state.applications[0].message).toBe("Updated message");
    });

    it("should delete application", () => {
      const initialApplications: Application[] = [
        {
          id: 1,
          organisation: { id: 1, name: "Festival 1" },
          organisationType: "Festival",
          profile: 1,
          applicationDate: "2025-01-15",
          applicationMethod: ApplicationMethod.EMAIL,
          status: ApplicationStatus.DRAFT,
          createdAt: "2025-01-15T10:00:00",
        },
        {
          id: 2,
          organisation: { id: 2, name: "Venue 1" },
          organisationType: "Venue",
          profile: 1,
          applicationDate: "2025-01-16",
          applicationMethod: ApplicationMethod.FORM,
          status: ApplicationStatus.DRAFT,
          createdAt: "2025-01-16T10:00:00",
        },
      ];

      const state = applicationReducer(
        { ...initialState, applications: initialApplications },
        deleteApplication(1),
      );

      expect(state.applications).toHaveLength(1);
      expect(state.applications[0].id).toBe(2);
    });

    it("should handle application status transitions", () => {
      const mockApplication: Application = {
        id: 1,
        organisation: { id: 1, name: "Festival 1" },
        organisationType: "Festival",
        profile: 1,
        applicationDate: "2025-01-15",
        applicationMethod: ApplicationMethod.EMAIL,
        status: ApplicationStatus.DRAFT,
        createdAt: "2025-01-15T10:00:00",
      };

      let state = applicationReducer(initialState, addApplication(mockApplication));
      expect(state.applications[0].status).toBe(ApplicationStatus.DRAFT);

      // Transition to APPLIED
      const appliedApp = { ...mockApplication, status: ApplicationStatus.APPLIED };
      state = applicationReducer(state, updateApplication(appliedApp));
      expect(state.applications[0].status).toBe(ApplicationStatus.APPLIED);

      // Transition to ACCEPTED
      const acceptedApp = { ...mockApplication, status: ApplicationStatus.ACCEPTED };
      state = applicationReducer(state, updateApplication(acceptedApp));
      expect(state.applications[0].status).toBe(ApplicationStatus.ACCEPTED);
    });
  });

  describe("Cross-slice integration", () => {
    it("should maintain separate state for different slices", () => {
      const store = configureStore({
        reducer: {
          auth: authReducer,
          festivals: festivalReducer,
          residencies: residencyReducer,
          venues: venueReducer,
          applications: applicationReducer,
        },
      });

      const mockFestival: Festival = {
        id: 1,
        name: "Test Festival",
        festivalType: FestivalType.MUSIC,
      };

      const mockResidency: Residency = {
        id: 1,
        name: "Test Residency",
        country: "France",
      };

      store.dispatch(setFestival(mockFestival));
      store.dispatch(setResidency(mockResidency));

      const state = store.getState();
      expect(state.festivals.festivals).toHaveLength(1);
      expect(state.residencies.residencies).toHaveLength(1);
      expect(state.festivals.festivals[0].name).toBe("Test Festival");
      expect(state.residencies.residencies[0].name).toBe("Test Residency");
    });

    it("should maintain filter state independently per slice", () => {
      const store = configureStore({
        reducer: {
          festivals: festivalReducer,
          residencies: residencyReducer,
        },
      });

      const festivalFilter = { id: "type", column: "type", value: "MUSIC" };
      const residencyFilter = { id: "country", column: "country", value: "France" };

      store.dispatch(setColumnFilter(festivalFilter));
      store.dispatch(setResidencyColumnFilter(residencyFilter));

      const state = store.getState();
      expect(state.festivals.filters).toHaveLength(1);
      expect(state.residencies.filters).toHaveLength(1);
      expect(state.festivals.filters[0].value).toBe("MUSIC");
      expect(state.residencies.filters[0].value).toBe("France");
    });
  });
});
