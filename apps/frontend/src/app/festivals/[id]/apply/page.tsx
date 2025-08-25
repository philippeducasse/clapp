import FormHeader from "@/components/common/form/FormHeader";
import React from "react";
import { Action } from "@/interfaces/Enums";
const FestivalApplicationPage = () => {
  return (
    <div>
      <FormHeader action={Action.APPLY} entityName="Festival" />
    </div>
  );
};

export default FestivalApplicationPage;
