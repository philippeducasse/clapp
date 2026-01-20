"use client";
import { useCallback, useMemo, useState } from "react";
import { Venue } from "@/interfaces/entities/Venue";
import { useVenueColumns } from "../../helpers/useVenueColumns";
import { DataTable } from "@/components/common/table/DataTable";
import { useDispatch } from "react-redux";
import { setVenues, deleteVenue } from "@/redux/slices/venueSlice";
import { EntityName } from "@/interfaces/Enums";
import { DeleteModal } from "@/components/common/modals/DeleteModal";
import { venueApiService } from "@/api/venueApiService";
import { getVenueFilters } from "../../helpers/getVenueFilters";
import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";

interface VenuesTableProps {
  initialData: PaginatedResponse<Venue>;
}

export const VenuesTable = ({ initialData }: VenuesTableProps) => {
  const dispatch = useDispatch();
  const [venueData, setVenueData] = useState<PaginatedResponse<Venue>>(initialData);
  const [openDeleteModal, setOpenDeleteModal] = useState(false);
  const [deleteVenueId, setDeleteVenueId] = useState<number | null>(null);

  const handleDeleteClick = useCallback((id: number) => {
    setDeleteVenueId(id);
    setOpenDeleteModal(true);
  }, []);

  const onConfirmDelete = useCallback(async () => {
    if (deleteVenueId === null) return;
    await venueApiService.remove(deleteVenueId);

    setVenueData((prev) => ({
      ...prev,
      results: prev.results.filter((venue) => venue.id !== deleteVenueId),
      count: prev.count - 1,
    }));

    dispatch(deleteVenue(deleteVenueId));
    setDeleteVenueId(null);
  }, [deleteVenueId, dispatch]);

  const handleDataFetched = useCallback(
    (data: PaginatedResponse<Venue>) => {
      setVenueData(data);
      dispatch(setVenues(data.results));
    },
    [dispatch],
  );

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
      <DataTable
        columns={columns}
        data={venueData.results}
        entityName={EntityName.VENUE}
        filters={filters}
        totalCount={venueData.count}
        fetchData={venueApiService.getAll}
        onDataFetched={handleDataFetched}
      />
    </>
  );
};
