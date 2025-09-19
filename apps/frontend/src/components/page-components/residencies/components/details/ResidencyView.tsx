'use client';

import React, { useEffect } from 'react';
import { Flag } from 'lucide-react';
import EditButton from '@/components/common/buttons/EditButton';
import { useSelector } from 'react-redux';
import { selectResidency, setSelectedResidency } from '@/redux/slices/residencySlice';
import { RootState } from '@/redux/store';
import { useDispatch } from 'react-redux';
import { getResidencyBasicInfo } from '../../helpers/getResidencyBasicInfo';
import { getResidencyDetails } from '../../helpers/getResidencyDetails';
import { useRouter } from 'next/navigation';
import { Info, NotebookTabs } from 'lucide-react';
import { refreshResidency } from '../../helpers/refreshResidency';
import { Skeleton } from '@/components/ui/skeleton';
import GenericButton from '@/components/common/buttons/GenericButton';
import DetailsViewHeader from '@/components/common/details-view/DetailsViewHeader';
import DetailsViewSection from '@/components/common/details-view/DetailsViewSection';
import DetailsViewWrapper from '@/components/common/details-view/DetailsViewWrapper';

const ResidencyView = ({ id }: { id: number }) => {
  const dispatch = useDispatch();
  const residency = useSelector((state: RootState) => selectResidency(state, id));
  const router = useRouter();

  useEffect(() => {
    if (!residency) {
      refreshResidency(id, dispatch);
    } else {
      dispatch(setSelectedResidency(residency));
    }
  }, [id, residency, dispatch]);

  if (!residency) {
    return <Skeleton />;
  }

  const goToApplyPage = async () => {
    router.push(`/residencies/${id}/apply`);
  };

  return (
    <DetailsViewWrapper href='/residencies'>
      <DetailsViewHeader
        title={residency.name}
        subtitle={residency.location}
        icon={<Flag className='text-emerald-600 dark:text-emerald-400' size={32} />}
        actionElements={
          <>
            <GenericButton
              onClick={goToApplyPage}
              label={'Apply to residency'}
              isLoading={false}
            />
            <EditButton href={`/residencies/${residency.id}/edit`} />
          </>
        }
      />
      <DetailsViewSection
        title='Basic information'
        icon={<Info className='text-emerald-600 dark:text-emerald-400' />}
        data={getResidencyBasicInfo(residency)}
      />
      <DetailsViewSection
        title='Residency details'
        icon={<NotebookTabs className='text-emerald-600 dark:text-emerald-400' />}
        data={getResidencyDetails(residency)}
      />
    </DetailsViewWrapper>
  );
};

export default ResidencyView;
