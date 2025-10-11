"use client";
import { useEffect, useState } from "react";
import { Festival } from "@/interfaces/entities/Festival";
import { PaginatedResponse } from "@/interfaces/PaginatedResponse";
import { useFestivalColumns } from "../../helpers/useFestivalColumns";
import { DataTable } from "@/components/common/table/DataTable";
import { useDispatch } from "react-redux";
import { setFestivals } from "@/redux/slices/festivalSlice";
import { EntityName } from "@/interfaces/Enums";
import { festivalApiService } from "@/api/festivalApiService";

interface FestivalsTableProps {
  initialData: PaginatedResponse<Festival>;
}

export const FestivalsTable = ({ initialData }: FestivalsTableProps) => {
  const dispatch = useDispatch();
  const [festivals, setFestivalsData] = useState<PaginatedResponse<Festival>>(initialData);
  const [pagination, setPagination] = useState({
    pageIndex: 0,
    pageSize: 50,
  });
  const [isLoading, setIsLoading] = useState(false);

  // Update Redux store when data changes
  useEffect(() => {
    dispatch(setFestivals(festivals.results));
  }, [dispatch, festivals.results]);

  // Fetch new data when pagination changes (but not on initial mount)
  useEffect(() => {
    if (pagination.pageIndex === 0) return; // Skip initial mount

    const fetchFestivals = async () => {
      setIsLoading(true);
      const offset = pagination.pageIndex * pagination.pageSize;
      const data = await festivalApiService.getAllFestivals(
        pagination.pageSize,
        offset
      );
      setFestivalsData(data);
      setIsLoading(false);
    };

    fetchFestivals();
  }, [pagination]);

  const columns = useFestivalColumns();

  return (
    <DataTable
      columns={columns}
      data={festivals.results}
      entityName={EntityName.FESTIVAL}
      pagination={pagination}
      setPagination={setPagination}
      totalCount={festivals.count}
      isLoading={isLoading}
    />
  );
};
