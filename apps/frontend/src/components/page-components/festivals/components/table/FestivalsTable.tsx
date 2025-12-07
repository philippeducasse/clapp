"use client";
import { useEffect, useState } from "react";
import { Festival } from "@/interfaces/entities/Festival";
import { PaginatedResponse } from "@/interfaces/table/PaginatedResponse";
import { useFestivalColumns } from "../../helpers/useFestivalColumns";
import { DataTable } from "@/components/common/table/DataTable";
import { useDispatch } from "react-redux";
import { setFestivals, deleteFestival } from "@/redux/slices/festivalSlice";
import { EntityName } from "@/interfaces/Enums";
import { festivalApiService } from "@/api/festivalApiService";
import { getFestivalFilters } from "../../helpers/getFestivalFilters";
import { DeleteModal } from "@/components/common/modals/DeleteModal";

interface FestivalsTableProps {
  initialData: PaginatedResponse<Festival>;
}

export const FestivalsTable = ({ initialData }: FestivalsTableProps) => {
  const dispatch = useDispatch();
  const [festivalData, setFestivalData] = useState<PaginatedResponse<Festival>>(initialData);
  const [openDeleteModal, setOpenDeleteModal] = useState(false);
  const [deleteFestivalId, setDeleteFestivalId] = useState<number | null>(null);
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 50,
  });
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    dispatch(setFestivals(festivalData.results));
  }, [dispatch, festivalData.results]);

  useEffect(() => {
    if (pagination.pageIndex === 0) return;

    const fetchFestivals = async () => {
      setIsLoading(true);
      // const offset = pagination.pageIndex * pagination.pageSize;
      const data = await festivalApiService.getAll();
      // pagination.pageSize,
      // offset
      setFestivalData(data);
      setIsLoading(false);
    };

    fetchFestivals();
  }, [pagination]);

  const handleDeleteClick = (id: number) => {
    setDeleteFestivalId(id);
    setOpenDeleteModal(true);
  };

  const onConfirmDelete = async () => {
    if (deleteFestivalId === null) return;
    await festivalApiService.remove(deleteFestivalId);

    // Update local state by filtering out the deleted festival
    setFestivalData(prev => ({
      ...prev,
      results: prev.results.filter(festival => festival.id !== deleteFestivalId),
      count: prev.count - 1
    }));

    // Also update Redux for consistency
    dispatch(deleteFestival(deleteFestivalId));
    setDeleteFestivalId(null);
  };

  const columns = useFestivalColumns({ onDeleteClick: handleDeleteClick });

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
        pagination={pagination}
        setPagination={setPagination}
        totalCount={festivalData.count}
        isLoading={isLoading}
        filters={getFestivalFilters()}
      />
    </>
  );
};
