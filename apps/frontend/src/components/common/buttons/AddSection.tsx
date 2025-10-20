import CreateButton from "./CreateButton";

interface AddSectionProps {
  href: string;
  label?: string;
}

const AddSection = ({ label, href }: AddSectionProps) => {
  return (
    <div className="flex items-center relative my-6">
      <div className="w-full h-px bg-gradient-to-r from-transparent via-gray-300 to-transparent"></div>
      <CreateButton
        href={href}
        className="absolute left-1/2 -translate-x-1/2"
        label={`Add ${label} `}
      />
    </div>
  );
};

export default AddSection;
