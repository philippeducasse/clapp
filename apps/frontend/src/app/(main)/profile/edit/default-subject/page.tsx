import ProfileForm from "@/components/page-components/profile/components/form/ProfileForm";
import { Action } from "@/interfaces/Enums";

const EditDefaultSubjectPage = () => {
  return <ProfileForm action={Action.EDIT} isDefaultSubject />;
};

export default EditDefaultSubjectPage;
