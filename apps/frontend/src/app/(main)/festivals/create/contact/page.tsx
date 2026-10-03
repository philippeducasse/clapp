import FestivalContactsForm from "@/components/page-components/festivals/components/form/FestivalContactsForm";

import { Action } from "@/interfaces/Enums";

const FestivalCreationPage = () => {
  return <FestivalContactsForm action={Action.CREATE} />;
};

export default FestivalCreationPage;
