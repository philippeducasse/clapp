'use client';
import { useEffect } from 'react';
import { useResidencyColumns } from '../../helpers/useResidencyColumns';
import { DataTable } from '@/components/common/table/DataTable';
import { useDispatch, useSelector } from 'react-redux';
import { fetchResidencies, selectAllResidencies } from '@/redux/slices/residencySlice';
import { EntityName } from '@/interfaces/Enums';
import { AppDispatch } from '@/redux/store';

export const ResidenciesTable = () => {
  const dispatch = useDispatch<AppDispatch>();
  const residencies = useSelector(selectAllResidencies);

  useEffect(() => {
    dispatch(fetchResidencies());
  }, [dispatch]);

  const columns = useResidencyColumns();

  return <DataTable columns={columns} data={residencies} entityName={EntityName.RESIDENCY} />;
};
