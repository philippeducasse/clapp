import CreateButton from "./CreateButton";

interface AddSectionProps {
  label?: string;
}

const AddSection = ({ label }: AddSectionProps) => {
  return (
    <div className="flex items-center relative my-6">
      <div className="w-full h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent"></div>
      <CreateButton
        href="/festivals/create/contact"
        className="absolute left-1/2 -translate-x-1/2"
        label={`Add ${label} `}
      />
    </div>
  );
};

export default AddSection;
