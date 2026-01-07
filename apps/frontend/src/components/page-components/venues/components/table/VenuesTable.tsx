"use client";
import { useEffect, useState, useCallback, useMemo } from "react";
import { Venue } from "@/interfaces/entities/Venue";
import { useVenueColumns } from "../../helpers/useVenueColumns";
import { DataTable } from "@/components/common/table/DataTable";
import { useDispatch } from "react-redux";
import { setVenues, deleteVenue } from "@/redux/slices/venueSlice";
import { EntityName } from "@/interfaces/Enums";
import { DeleteModal } from "@/components/common/modals/DeleteModal";
import { venueApiService } from "@/api/venueApiService";
import { getVenueFilters } from "../../helpers/getVenueFilters";

interface VenuesTableProps {
  venues: Venue[];
}

export const VenuesTable = ({ venues }: VenuesTableProps) => {
  const dispatch = useDispatch();
  const [venueData, setVenueData] = useState<Venue[]>(venues);
  const [openDeleteModal, setOpenDeleteModal] = useState(false);
  const [deleteVenueId, setDeleteVenueId] = useState<number | null>(null);

  useEffect(() => {
    dispatch(setVenues(venueData));
  }, [dispatch, venueData]);

  const handleDeleteClick = useCallback((id: number) => {
    setDeleteVenueId(id);
    setOpenDeleteModal(true);
  }, []);

  const onConfirmDelete = useCallback(async () => {
    if (deleteVenueId === null) return;
    await venueApiService.remove(deleteVenueId);

    // Update local state by filtering out the deleted venue
    setVenueData(prev => prev.filter(venue => venue.id !== deleteVenueId));

    // Also update Redux for consistency
    dispatch(deleteVenue(deleteVenueId));
    setDeleteVenueId(null);
  }, [deleteVenueId, dispatch]);

  const columns = useVenueColumns({ onDeleteClick: handleDeleteClick });

  const filters = useMemo(() => getVenueFilters(), []);

  return (
    <>
      <DeleteModal
        open={openDeleteModal}
        onOpenChange={setOpenDeleteModal}
        onConfirm={onConfirmDelete}
        itemName="venue"
      />
      <DataTable columns={columns} data={venueData} entityName={EntityName.VENUE} filters={filters} />
    </>
  );
};
