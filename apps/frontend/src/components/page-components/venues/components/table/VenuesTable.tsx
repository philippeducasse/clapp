"use client";
import { useEffect } from "react";
import { Venue } from "@/interfaces/entities/Venue";
import { useVenueColumns } from "../../helpers/useVenueColumns";
import { DataTable } from "@/components/common/table/DataTable";
import { useDispatch } from "react-redux";
import { setVenues } from "@/redux/slices/venueSlice";
import { EntityName } from "@/interfaces/Enums";

interface VenuesTableProps {
  venues: Venue[];
}

export const VenuesTable = ({ venues }: VenuesTableProps) => {
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(setVenues(venues));
  }, [dispatch, venues]);

  const columns = useVenueColumns();

  return (
    <DataTable columns={columns} data={venues} entityName={EntityName.VENUE} />
  );
};
