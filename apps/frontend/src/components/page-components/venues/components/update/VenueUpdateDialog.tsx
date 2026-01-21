import { VenueDiffTable } from "./VenueDiffTable";
import { Venue } from "@/interfaces/entities/Venue";
import { venueApiService } from "@/api/venueApiService";
import { useDispatch, useSelector } from "react-redux";
import { selectVenue, updateVenue } from "@/redux/slices/venueSlice";
import { useParams } from "next/navigation";
import { RootState } from "@/redux/store";
import { UpdateDialog } from "@/components/common/modals/UpdateDialog";

export const VenueUpdateDialog = () => {
  const dispatch = useDispatch();
  const params = useParams();
  const venueId = Number(params.id);
  const venue = useSelector((state: RootState) => selectVenue(state, venueId));

  return (
    <UpdateDialog<Venue>
      entity={venue}
      entityName="Venue"
      DiffTableComponent={VenueDiffTable}
      onEnrich={() => venueApiService.enrich(venue!.id)}
      onUpdate={async (updated) => {
        await venueApiService.update(updated);
        dispatch(updateVenue(updated));
      }}
    />
  );
};
