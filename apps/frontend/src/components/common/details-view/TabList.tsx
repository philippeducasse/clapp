import { TabsList, TabsTrigger } from "@/components/ui/tabs";

interface TabListProps {
  viewSections: { key: string; name: string }[];
}

const TabListing = ({ viewSections }: TabListProps) => {
  return (
    <TabsList className="mb-4">
      {viewSections.map((section) => (
        <TabsTrigger key={section.key} value={section.key}>
          {section.name}
        </TabsTrigger>
      ))}
    </TabsList>
  );
};

export default TabListing;
