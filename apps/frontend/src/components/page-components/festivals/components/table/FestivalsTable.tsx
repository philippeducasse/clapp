"use client";
import { useState, useCallback, useMemo } from "react";
import { Festival } from "@/interfaces/entities/Festival";
import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";
import { ColumnFilter } from "@/interfaces/table/FilterCongig";
import { useFestivalColumns } from "../../helpers/useFestivalColumns";
import { DataTable } from "@/components/common/table/DataTable";
import { useDispatch } from "react-redux";
import { setFestivals, deleteFestival, updateFestival } from "@/redux/slices/festivalSlice";
import { EntityName, TagAction } from "@/interfaces/Enums";
import { festivalApiService } from "@/api/festivalApiService";
import { getFestivalFilters } from "../../helpers/getFestivalFilters";
import { DeleteModal } from "@/components/common/modals/DeleteModal";

interface FestivalsTableProps {
  initialData: PaginatedResponse<Festival>;
  /** Filters the server applied to `initialData` (e.g. hidden tags). */
  initialColumnFilters?: ColumnFilter[];
}

export const FestivalsTable = ({ initialData, initialColumnFilters }: FestivalsTableProps) => {
  const dispatch = useDispatch();
  const [festivalData, setFestivalData] = useState<PaginatedResponse<Festival>>(initialData);
  const [openDeleteModal, setOpenDeleteModal] = useState(false);
  const [deleteFestivalId, setDeleteFestivalId] = useState<number | null>(null);

  const handleDeleteClick = useCallback((id: number) => {
    setDeleteFestivalId(id);
    setOpenDeleteModal(true);
  }, []);

  const onConfirmDelete = useCallback(async () => {
    if (deleteFestivalId === null) return;
    await festivalApiService.remove(deleteFestivalId);

    // Update local state by filtering out the deleted festival
    setFestivalData((prev) => ({
      ...prev,
      results: prev.results.filter((festival) => festival.id !== deleteFestivalId),
      count: prev.count - 1,
    }));

    // Also update Redux for consistency
    dispatch(deleteFestival(deleteFestivalId));
    setDeleteFestivalId(null);
  }, [deleteFestivalId, dispatch]);

  const handleDataFetched = useCallback(
    (data: PaginatedResponse<Festival>) => {
      setFestivalData(data);
      dispatch(setFestivals(data.results));
    },
    [dispatch],
  );

  const handleTagClick = useCallback(
    async (id: number, action: TagAction) => {
      try {
        const updated = await festivalApiService.tag(id, action);
        setFestivalData((prev) => ({
          ...prev,
          results: prev.results.map((festival) =>
            festival.id === id ? { ...festival, tag: updated.tag } : festival,
          ),
        }));
        dispatch(updateFestival(updated));
      } catch (error) {
        console.error("Failed to tag festival:", error);
      }
    },
    [dispatch],
  );

  const columns = useFestivalColumns({
    onDeleteClick: handleDeleteClick,
    onTagClick: handleTagClick,
  });

  const filters = useMemo(() => getFestivalFilters(), []);

  return (
    <>
      <DeleteModal
        open={openDeleteModal}
        onOpenChange={setOpenDeleteModal}
        onConfirm={onConfirmDelete}
        itemName="festival"
      />
      <DataTable
        columns={columns}
        data={festivalData.results}
        entityName={EntityName.FESTIVAL}
        filters={filters}
        initialColumnFilters={initialColumnFilters}
        fetchData={festivalApiService.getAll}
        onDataFetched={handleDataFetched}
      />
    </>
  );
};
