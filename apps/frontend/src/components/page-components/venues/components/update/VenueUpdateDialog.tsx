import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { VenueDiffTable } from "./VenueDiffTable";
import { Venue } from "@/interfaces/entities/Venue";
import { useState } from "react";
import { Hammer } from "lucide-react";
import { venueApiService } from "@/api/venueApiService";
import SubmitButton from "../../../../common/buttons/SubmitButton";
import { DynamicProgress } from "../../../../common/DynamicProgress";
import { useDispatch, useSelector } from "react-redux";
import { selectVenue, updateVenue } from "@/redux/slices/venueSlice";
import { useParams } from "next/navigation";
import { RootState } from "@/redux/store";
import { X } from "lucide-react";
import GenericButton from "@/components/common/buttons/GenericButton";

export const VenueUpdateDialog = () => {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [updatedFields, setUpdatedFields] = useState<Venue | undefined>();

  const dispatch = useDispatch();
  const params = useParams();
  const venueId = Number(params.id);
  const venue = useSelector((state: RootState) => selectVenue(state, venueId));

  const handleUpdate = async () => {
    setLoading(true);
    try {
      if (venue && !updatedFields) {
        const response = await venueApiService.enrichVenue(venue);
        setUpdatedFields(response);
      }
    } catch (error) {
      console.error(`Error: could not update venue: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (updatedFields) {
      setLoading(true);
      try {
        await venueApiService.updateVenue(updatedFields);
        dispatch(updateVenue(updatedFields));
        setOpen(false);
      } catch (error) {
        console.error(`Error: could not update venue: ${error}`);
      } finally {
        setLoading(false);
      }
    }
  };

  if (!venue) {
    return null;
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <GenericButton
          variant="secondary"
          icon={<Hammer />}
          label="Update"
          onClick={handleUpdate}
        />
      </DialogTrigger>
      <DialogContent className="w-full md:w-[90vw] max-w-full h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Update Venue</DialogTitle>
          <DialogDescription>Review changes</DialogDescription>
        </DialogHeader>
        {updatedFields ? (
          <VenueDiffTable
            original={venue}
            updated={updatedFields}
            setUpdated={setUpdatedFields}
          />
        ) : (
          <DynamicProgress />
        )}
        <DialogFooter className="items-end">
          <DialogClose asChild>
            <Button variant="outline">
              <X className="text-red-500" /> Cancel
            </Button>
          </DialogClose>
          <SubmitButton
            isLoading={loading}
            onClick={handleSubmit}
            label="Save changes"
          />
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
