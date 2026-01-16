import CreateButton from "./CreateButton";

interface AddSectionProps {
  href: string;
  label?: string;
}

const AddSection = ({ label, href }: AddSectionProps) => {
  return (
    <div className="flex items-center gap-1 py-4">
      <div className="flex-1 h-px bg-gradient-to-r from-transparent to-gray-300"></div>
      <CreateButton href={href} label={`Add ${label} `} />
      <div className="flex-1 h-px bg-gradient-to-l from-transparent to-gray-300"></div>
    </div>
  );
};

export default AddSection;
