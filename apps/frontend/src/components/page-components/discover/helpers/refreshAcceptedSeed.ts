import { AppDispatch } from "@/redux/store";
import { DiscoveryCandidate, DiscoveryOrgType } from "@/interfaces/entities/Discovery";
import { refreshFestival } from "@/components/page-components/festivals/helpers/refreshFestival";
import { refreshResidency } from "@/components/page-components/residencies/helpers/refreshResidency";
import { refreshVenue } from "@/components/page-components/venues/helpers/refreshVenue";

/** After an accept, load the new seed into the matching Redux slice (superusers see seeds). */
export const refreshAcceptedSeed = async (
  candidate: DiscoveryCandidate,
  dispatch: AppDispatch,
): Promise<void> => {
  const seed = candidate.createdSeed;
  if (!seed) return;
  const refresh = {
    [DiscoveryOrgType.FESTIVAL]: refreshFestival,
    [DiscoveryOrgType.RESIDENCY]: refreshResidency,
    [DiscoveryOrgType.VENUE]: refreshVenue,
  }[seed.orgType];
  await refresh(seed.id, dispatch);
};
