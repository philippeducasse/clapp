'use client';

import React from 'react';
import { ResidencyForm } from '@/components/page-components/residencies/components/form/ResidencyForm';

const EditResidencyPage = ({ params }: { params: { id: string } }) => {
  return <ResidencyForm id={Number(params.id)} />;
};

export default EditResidencyPage;
