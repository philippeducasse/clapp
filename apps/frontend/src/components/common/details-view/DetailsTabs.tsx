import React from "react";
import { Tabs, TabsContent } from "@/components/ui/tabs";
import TabListing from "./TabList";

interface TabProps {
  name: string;
  children: React.ReactNode;
}

export const Tab = ({ children }: TabProps) => {
  return <>{children}</>;
};

interface DetailsTabsProps {
  defaultTab: string;
  children: React.ReactElement<TabProps> | React.ReactElement<TabProps>[];
  onTabChange?: (value: string) => void;
}

const DetailsTabs = ({ defaultTab, children, onTabChange }: DetailsTabsProps) => {
  const tabs = React.Children.toArray(children) as React.ReactElement<TabProps>[];

  const tabSections = tabs.map((tab) => ({
    key: tab.props.name.toLowerCase().replace(/\s+/g, "-"),
    name: tab.props.name,
  }));

  return (
    <Tabs defaultValue={defaultTab} className="w-full" onValueChange={onTabChange}>
      <TabListing viewSections={tabSections} />
      {tabs.map((tab) => {
        const key = tab.props.name.toLowerCase().replace(/\s+/g, "-");
        return (
          <TabsContent key={key} value={key}>
            {tab.props.children}
          </TabsContent>
        );
      })}
    </Tabs>
  );
};

export default DetailsTabs;
