'use client';

import React from 'react';
import { ResidencyView } from '@/components/page-components/residencies/components/details/ResidencyView';

const ResidencyDetailsPage = ({ params }: { params: { id: string } }) => {
  return <ResidencyView id={Number(params.id)} />;
};

export default ResidencyDetailsPage;
